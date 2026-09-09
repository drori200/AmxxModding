#!/usr/bin/env python3
"""Acquire hash-pinned canonical PAWN sources and build isolated research tools.

No system installation, production compiler, or AMXX source is used here.
Run from any directory: python3 research/tools/toolchains.py [--current]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache/research"
EVIDENCE = ROOT / "research/evidence"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_digest(path):
    records = {str(p.relative_to(path)): digest(p) for p in sorted(path.rglob("*")) if p.is_file()}
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def run(command, log):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as output:
        output.write(json.dumps([str(x) for x in command]) + "\n")
        output.flush()
        subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, check=True, timeout=600)


def acquire():
    sources = json.loads((EVIDENCE / "sources.json").read_text())
    for source in sources:
        path = ROOT / source["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            temporary = path.with_suffix(path.suffix + ".part")
            request = urllib.request.Request(source["url"], headers={"User-Agent": "PAWN-research-lab/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as out:
                shutil.copyfileobj(response, out)
            if digest(temporary) != source["sha256"]:
                temporary.unlink()
                raise RuntimeError(f"Archive hash mismatch: {source['id']}")
            temporary.replace(path)
        if digest(path) != source["sha256"]:
            raise RuntimeError(f"Archive hash mismatch: {path}")
        if path.suffix == ".zip":
            destination = CACHE / "toolchains" / path.stem
            # Extract only to the isolated source cache. Check entry paths first.
            with zipfile.ZipFile(path) as archive:
                for entry in archive.infolist():
                    target = (destination / entry.filename).resolve()
                    if not target.is_relative_to(destination.resolve()):
                        raise RuntimeError(f"Unsafe archive path: {entry.filename}")
                archive.extractall(destination)


def build(source, builddir, bits, cmake, compiler_only=False):
    flags = ["-DCMAKE_POLICY_VERSION_MINIMUM=3.5", "-DCMAKE_BUILD_TYPE=Debug",
             "-DCMAKE_C_STANDARD=99", "-DHAVE_CURSES_H=0",
             f"-DCMAKE_C_FLAGS=-DPAWN_CELL_SIZE={bits} -DAMXDBG",
             "-DCMAKE_INSTALL_LIBDIR=lib", "-DCMAKE_INSTALL_BINDIR=bin"]
    configure = [cmake, "-S", str(source), "-B", str(builddir), *flags]
    run(configure, CACHE / "logs" / f"{builddir.name}-configure.txt")
    targets = ["--target", "pawncc"] if compiler_only else []
    run([cmake, "--build", str(builddir), *targets, "--parallel", "4"], CACHE / "logs" / f"{builddir.name}-build.txt")
    module_fix = None
    if not compiler_only:
        # Upstream CMake's stream-console String target omits getch.c, leaving
        # unresolved getch/kbhit symbols on Linux. Link those original sources
        # explicitly; do not alter the archive or disable string formatting.
        module_fix = ["cc", "-std=gnu99", "-O0", "-g", "-shared", "-fPIC",
                      f"-DPAWN_CELL_SIZE={bits}", "-DHAVE_STDINT_H", "-DHAVE_UNISTD_H",
                      "-D_GNU_SOURCE", "-DFLOATPOINT", "-DFIXEDPOINT",
                      f"-I{source / 'amx'}", f"-I{source / 'linux'}",
                      *[str(source / part) for part in ["amx/amxstring.c", "amx/amx.c", "amx/amxcons.c", "linux/getch.c"]],
                      "-lm", "-ldl", "-o", str(builddir / "amxString.so")]
        run(module_fix, CACHE / "logs" / f"{builddir.name}-string-link.txt")
    return {
        "source": str(source.relative_to(ROOT)), "source_tree_sha256": tree_digest(source),
        "cell_bits": bits, "configure_command": configure,
        "compiler_only": compiler_only, "stream_console_string_link": module_fix,
        # This compiler returns 3 even for its successful help display.
        "compiler_banner": subprocess.run([builddir / "pawncc", "-h"], text=True, capture_output=True).stdout.splitlines()[0],
        "binaries": {str(p.relative_to(ROOT)): digest(p) for p in sorted(builddir.iterdir())
                     if p.is_file() and (p.name.startswith("pawn") or ".so" in p.name)},
        "include_tree_sha256": tree_digest(source / "include"),
        "revision_metadata": (source / "compiler/svnrev.h").read_text(),
    }


def build_lab_host(source, bits):
    output = CACHE / f"build{bits}/labrun"
    output.parent.mkdir(parents=True, exist_ok=True)
    # No optional extension modules. The test host registers its own small native API.
    # Nonrelocating token interpreter is supported at all three cell widths.
    command = ["cc", "-std=gnu99", "-O0", "-g", f"-DPAWN_CELL_SIZE={bits}",
               "-DAMX_NODYNALOAD", "-DAMX_DONT_RELOCATE", "-DHAVE_STDINT_H", "-D_GNU_SOURCE",
               f"-I{source / 'amx'}", f"-I{source / 'linux'}",
               str(ROOT / "research/pawn/host/labrun.c"), str(source / "amx/amx.c"),
               "-o", str(output)]
    run(command, CACHE / "logs" / f"labrun{bits}-build.txt")
    host_sources = [ROOT / "research/pawn/host/labrun.c", ROOT / "research/pawn/host/contracts.h", source / "amx/amx.c"]
    return {"command": command, "sha256": digest(output), "cell_bits": bits,
            "sources_sha256": {str(p.relative_to(ROOT)): digest(p) for p in host_sources},
            "configuration": "C interpreter; no dynamic loading; no JIT; no optional libraries; no relocation"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", action="store_true", help="also build the separately pinned development compiler")
    parser.add_argument("--acquire-only", action="store_true")
    parser.add_argument("--hosts-only", action="store_true", help="rebuild lab hosts without touching compiler/module binaries")
    args = parser.parse_args()
    if args.hosts_only:
        manifest = json.loads((EVIDENCE / "toolchains.json").read_text())
        for bits in (16, 32, 64):
            manifest["hosts"][str(bits)] = build_lab_host(CACHE / "toolchains/pawn-stable", bits)
        (EVIDENCE / "toolchains.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return
    acquire()
    if args.acquire_only:
        return
    cmake = shutil.which("cmake") or str(CACHE / "python/bin/cmake")
    if not Path(cmake).is_file():
        raise SystemExit("CMake required. Use an isolated venv: python3 -m venv .cache/research/python; .cache/research/python/bin/pip install cmake==4.4.3")
    stable = CACHE / "toolchains/pawn-stable"
    manifest = {"platform": platform.platform(), "host_machine": platform.machine(),
                "c_compiler": subprocess.check_output(["cc", "--version"], text=True),
                "cmake": subprocess.check_output([cmake, "--version"], text=True),
                "stable": {}, "hosts": {}}
    for bits in (16, 32, 64):
        manifest["stable"][str(bits)] = build(stable, CACHE / f"build{bits}", bits, cmake, compiler_only=bits == 16)
    for bits in (16, 32, 64):
        manifest["hosts"][str(bits)] = build_lab_host(stable, bits)
    if args.current:
        current = CACHE / "toolchains/pawn-current/pawn"
        try:
            manifest["current"] = build(current, CACHE / "build-current32", 32, cmake)
            manifest["current"]["status"] = "built"
        except subprocess.CalledProcessError as failure:
            # A broken development snapshot is evidence, not permission to
            # silently patch it or lose the successful stable build manifest.
            manifest["current"] = {
                "status": "build_failed", "command": failure.cmd,
                "returncode": failure.returncode, "source_tree_sha256": tree_digest(current),
                "log": ".cache/research/logs/build-current32-build.txt",
                "log_sha256": digest(CACHE / "logs/build-current32-build.txt"),
                "revision_metadata": (current / "compiler/svnrev.h").read_text(),
            }
    (EVIDENCE / "toolchains.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Stable canonical PAWN tools ready. Provenance: research/evidence/toolchains.json")
    if manifest.get("current", {}).get("status") == "build_failed":
        print("The separate development snapshot did not build; its failure is retained in the manifest.")


if __name__ == "__main__":
    main()

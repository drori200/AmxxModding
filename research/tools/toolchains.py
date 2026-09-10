#!/usr/bin/env python3
"""Acquire hash-pinned canonical PAWN sources and build isolated research tools.

No system installation, production compiler, or AMXX source is used here.
Run from any directory: python3 research/tools/toolchains.py [--current]
"""
import argparse
from contextlib import contextmanager
import fcntl
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
COMPILER_CONFIG = ROOT / "research/pawn/empty.cfg"
OFFICIAL_STABLE_URL = "https://www.compuphase.com/pawn/pawn-4.1.7487.zip"
OFFICIAL_STABLE_SHA256 = "05cf630baef59912a9ffaf2745652187038d8d5be1a3aab870d13ea0bd31c7bc"


@contextmanager
def toolchain_lock(exclusive=False):
    """Cooperating setup/test commands cannot replace tools during execution."""
    CACHE.mkdir(parents=True, exist_ok=True)
    with (CACHE / "toolchains.lock").open("a") as handle:
        try:
            fcntl.flock(handle, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("PAWN toolchains are in use; finish the active setup/test command first") from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.part")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def zip_tree(archive_path, destination, extract_missing=False):
    """Compare EVERY extracted file to archive bytes. Never overwrite a change."""
    with zipfile.ZipFile(archive_path) as archive:
        expected = {}
        for entry in archive.infolist():
            target = destination / entry.filename
            if target.is_symlink() or not target.resolve().is_relative_to(destination.resolve()):
                raise RuntimeError(f"Unsafe archive path: {entry.filename}")
            if not entry.is_dir():
                if entry.filename in expected:
                    raise RuntimeError(f"Duplicate archive entry: {entry.filename}")
                raw = archive.read(entry)
                expected[entry.filename] = hashlib.sha256(raw).hexdigest()
                if extract_missing and not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
        actual = {str(p.relative_to(destination)): digest(p) for p in destination.rglob("*") if p.is_file()}
        if actual != expected:
            changed = sorted(k for k in set(actual) | set(expected) if actual.get(k) != expected.get(k))
            raise RuntimeError(f"Extracted official archive differs: {archive_path.name}: {changed}")
        return {"files": len(expected), "files_sha256": expected, "matches_archive": True}


def source_manifest():
    sources = json.loads((EVIDENCE / "sources.json").read_text())
    ids = [s["id"] for s in sources]
    required = {"pawn-stable.zip", "pawn-current.zip", "pawntest.zip", "Pawn_Language_Guide.pdf", "Pawn_Implementer_Guide.pdf"}
    if len(ids) != len(required) or set(ids) != required:
        raise RuntimeError("Canonical source manifest has missing or duplicate identities")
    stable = next(s for s in sources if s["id"] == "pawn-stable.zip")
    if stable["url"] != OFFICIAL_STABLE_URL or stable["sha256"] != OFFICIAL_STABLE_SHA256:
        raise RuntimeError("Stable compiler is not the approved official CompuPhase archive")
    for source in sources:
        if source["path"] != f".cache/research/downloads/{source['id']}":
            raise RuntimeError(f"Pinned source must use its canonical cache path: {source['id']}")
    return sources


def verify_sources():
    sources = source_manifest()
    observations = {}
    for source in sources:
        path = ROOT / source["path"]
        if not path.is_file() or digest(path) != source["sha256"]:
            raise RuntimeError(f"Pinned source missing or changed: {source['id']}")
        result = {"url": source["url"], "sha256": digest(path)}
        if path.suffix == ".zip":
            result.update(zip_tree(path, CACHE / "toolchains" / path.stem))
        observations[source["id"]] = result
    return observations


def runtime_inputs():
    """Snapshot actual files, not only a manifest claiming they are unchanged."""
    paths = [EVIDENCE / "sources.json", EVIDENCE / "toolchains.json", COMPILER_CONFIG]
    for directory in [CACHE / "toolchains/pawn-stable", ROOT / "research/pawn", ROOT / "research/tools"]:
        paths += [p for p in directory.rglob("*") if p.is_file() and
                  (directory == CACHE / "toolchains/pawn-stable" or p.suffix in (".p", ".inc", ".h", ".c", ".py", ".cfg"))]
    for bits in (16, 32, 64):
        paths += [p for p in (CACHE / f"build{bits}").glob("*") if p.is_file() and
                  (p.name in ("pawncc", "pawnrun", "labrun") or ".so" in p.name)]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))}


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
    sources = source_manifest()
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
            zip_tree(path, destination, extract_missing=True)
    verify_sources()


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
    host_sources += list((source / "amx").glob("*.h")) + list((source / "linux").glob("*.h"))
    return {"command": command, "sha256": digest(output), "cell_bits": bits,
            "sources_sha256": {str(p.relative_to(ROOT)): digest(p) for p in host_sources},
            "configuration": "C interpreter; no dynamic loading; no JIT; no optional libraries; no relocation"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", action="store_true", help="also build the separately pinned development compiler")
    parser.add_argument("--acquire-only", action="store_true")
    parser.add_argument("--hosts-only", action="store_true", help="rebuild lab hosts without touching compiler/module binaries")
    parser.add_argument("--verify-only", action="store_true", help="verify official archive bytes and source trees without rebuilding")
    args = parser.parse_args()
    if args.verify_only:
        report = verify_sources()
        write_json(EVIDENCE / "pawn-official-provenance.json", report)
        print("All five pinned downloads verified; every extracted source file matches its archive.")
        return
    if args.hosts_only:
        verify_sources()
        manifest = json.loads((EVIDENCE / "toolchains.json").read_text())
        for bits in (16, 32, 64):
            manifest["hosts"][str(bits)] = build_lab_host(CACHE / "toolchains/pawn-stable", bits)
        write_json(EVIDENCE / "toolchains.json", manifest)
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
    write_json(EVIDENCE / "toolchains.json", manifest)
    print("Stable canonical PAWN tools ready. Provenance: research/evidence/toolchains.json")
    if manifest.get("current", {}).get("status") == "build_failed":
        print("The separate development snapshot did not build; its failure is retained in the manifest.")


if __name__ == "__main__":
    with toolchain_lock(exclusive=True):
        main()

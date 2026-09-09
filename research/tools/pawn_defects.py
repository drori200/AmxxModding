#!/usr/bin/env python3
"""Bounded regression probes and an explicitly LOCAL diagnostic VM repair.

Unmodified upstream sources remain intact. The local repair only substitutes
cell-width stores in five cell instructions. It is causal evidence, not an
upstream release, a production recommendation, or a general correctness claim.
"""
import json
import subprocess
from pathlib import Path

from toolchains import ROOT, CACHE, EVIDENCE, digest
from pawn_lab import execute


def main():
    source = CACHE / "toolchains/pawn-stable"
    work = CACHE / "defect-probes"
    work.mkdir(parents=True, exist_ok=True)
    original = (source / "amx/amx.c").read_text()
    repairs = {
        "_W32(data,i,pri);": "_W(data,i,pri);",
        "_W32(data,stk,pri);": "_W(data,stk,pri);",
        "_W32(data,stk,alt);": "_W(data,stk,alt);",
        "_W32(data,offs,val);": "_W(data,offs,val);",
        "_W32(data,frm+offs,val);": "_W(data,frm+offs,val);",
    }
    patched = original
    for old, new in repairs.items():
        if patched.count(old) != 1:
            raise RuntimeError("Pinned source changed; diagnostic patch must be reviewed")
        patched = patched.replace(old, new)
    repaired_source = work / "amx-cell-stores.c"
    repaired_source.write_text(patched)
    report = {"schema": 1, "upstream_amx_sha256": digest(source / "amx/amx.c"),
              "local_repair_sha256": digest(repaired_source), "repairs": repairs,
              "repair_scope": "local diagnostic comparison only; upstream remains unchanged", "builds": [], "probes": []}
    for bits in (16, 64):
        command = ["cc", "-std=gnu99", "-O0", "-g", f"-DPAWN_CELL_SIZE={bits}", "-DAMX_NODYNALOAD",
                   "-DAMX_DONT_RELOCATE", "-DHAVE_STDINT_H", "-D_GNU_SOURCE",
                   f"-I{source / 'amx'}", f"-I{source / 'linux'}",
                   str(ROOT / "research/pawn/host/labrun.c"), str(repaired_source), "-o", str(work / f"labrun-fixed{bits}")]
        build = execute(command, work / f"build{bits}")
        report["builds"].append(build)
        if build["returncode"] or build["timeout"]:
            raise RuntimeError("Local diagnostic VM did not build")
    configs = [("cell16_fill", 16, 0), ("cell16_swap", 16, 0),
               ("cell64_fill", 64, 0), ("cell64_store", 64, 1),
               ("optimizer32_shift", 32, 3), ("optimizer64_expression", 64, 3)]
    for name, bits, optimize in configs:
        directory = work / name
        directory.mkdir(exist_ok=True)
        amx = directory / "program.amx"
        amx.unlink(missing_ok=True)
        script = ROOT / "research/pawn/defects" / (name + ".p")
        compiled = execute([CACHE / f"build{bits}/pawncc", script, f"-C{bits}", "-d2", f"-O{optimize}",
                            "-p", "-S1024", f"-i{ROOT / 'research/pawn/include'}", f"-o{amx}"], directory / "compile")
        probe = {"id": name, "cell_bits": bits, "optimization": optimize,
                 "source_sha256": digest(script), "compile": compiled}
        if not compiled["returncode"] and amx.exists():
            probe["unmodified_vm"] = execute([CACHE / f"build{bits}/labrun", amx], directory / "upstream")
            if bits in (16, 64):
                probe["locally_repaired_vm"] = execute([work / f"labrun-fixed{bits}", amx], directory / "local-repair")
        report["probes"].append(probe)
        print(name, compiled["returncode"], probe.get("unmodified_vm", {}).get("output", "").strip(),
              "LOCAL:", probe.get("locally_repaired_vm", {}).get("output", "").strip())
    (EVIDENCE / "pawn-defect-probes.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

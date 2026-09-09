#!/usr/bin/env python3
"""Re-execute preserved prior snippets and independently predicted exercises.

Prior snippets are an audit corpus, not correctness oracles. They remain
unchanged inside explicit wrappers. The independent exercises have separate
pre-recorded expected outputs; later observed outputs never replace them.
"""
import json
import re
from pathlib import Path
from pawn_lab import execute
from toolchains import ROOT, CACHE, EVIDENCE, digest


def main():
    prior = ROOT / "research/pawn/prior"
    cc, vm = CACHE / "build32/pawncc", CACHE / "build32/pawnrun"
    include = CACHE / "toolchains/pawn-stable/include"
    records = json.loads((prior / "prior-examples-audit.json").read_text())
    predictions = json.loads((prior / "independent-exercise-predictions.json").read_text())
    report = {"purpose": "Preserved-example audit plus independent combined-feature exercises",
              "compiler_sha256": digest(cc), "vm_sha256": digest(vm),
              "prior_artifacts": json.loads((prior / "original-artifacts.json").read_text()),
              "audit": [], "exercises": []}
    for item in records:
        name = f"{item['deck']}-{item['slide']:02d}"
        directory = CACHE / "examples/audit" / name
        directory.mkdir(parents=True, exist_ok=True)
        script = directory / "wrapped.p"
        script.write_text(item["wrapper_prefix"] + item["source"] + item["wrapper_suffix"] + "\n")
        amx = directory / "program.amx"
        amx.unlink(missing_ok=True)
        compiled = execute([cc, script, "-C32", "-d2", "-O0", f"-i{include}", f"-o{amx}"], directory / "compile")
        result = {"name": name, "classification": item["classification"], "wrapped_source_sha256": digest(script),
                  "wrapper_prefix": item["wrapper_prefix"], "original_snippet": item["source"],
                  "wrapper_suffix": item["wrapper_suffix"], "compile": compiled}
        if compiled["returncode"] == 0 and amx.exists():
            result["runtime"] = execute([vm, amx], directory / "runtime")
        report["audit"].append(result)
    for n in range(1, 6):
        script = prior / f"exercise-{n:02d}.p"
        for debug in (0, 2):
            for opt in (0, 1, 2, 3):
                directory = CACHE / "examples/exercises" / f"{n:02d}-d{debug}-O{opt}"
                directory.mkdir(parents=True, exist_ok=True)
                amx = directory / "program.amx"
                amx.unlink(missing_ok=True)
                compiled = execute([cc, script, "-C32", f"-d{debug}", f"-O{opt}", f"-i{include}", f"-o{amx}"], directory / "compile")
                diagnostic_codes = [int(x) for x in re.findall(r"(?:warning|error) (\d+):", compiled["output"])]
                expected_diagnostics = [237] if n == 5 and debug == 2 else []
                result = {"exercise": n, "debug": debug, "optimization": opt,
                          "source_sha256": digest(script), "expected_output": predictions[str(n)],
                          "expected_diagnostics": expected_diagnostics, "compile": compiled, "passed": False}
                if compiled["returncode"] == 0 and diagnostic_codes == expected_diagnostics and amx.exists():
                    result["runtime"] = execute([vm, amx], directory / "runtime")
                    output = re.sub(r"\x1b\[[0-9;]*m", "", result["runtime"]["output"]).strip()
                    result["passed"] = result["runtime"]["returncode"] == 0 and output == predictions[str(n)]
                report["exercises"].append(result)
    report["summary"] = {"audited_snippets": len(report["audit"]),
                         "standalone_prior_programs": sum(x["classification"] == "standalone" for x in report["audit"]),
                         "prior_compile_successes": sum(x["compile"]["returncode"] == 0 for x in report["audit"]),
                         "exercises_passed": sum(x["passed"] for x in report["exercises"]),
                         "exercise_profiles": len(report["exercises"])}
    (EVIDENCE / "pawn-examples-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"]))
    raise SystemExit(0 if all(x["passed"] for x in report["exercises"]) else 1)


if __name__ == "__main__":
    main()

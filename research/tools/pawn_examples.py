#!/usr/bin/env python3
"""Re-execute preserved prior snippets and independently predicted exercises.

Prior snippets are an audit corpus, not correctness oracles. They remain
unchanged inside explicit wrappers. The independent exercises have separate
pre-recorded expected outputs; later observed outputs never replace them.
"""
import collections
import hashlib
import json
import time
import re
from pathlib import Path
from pawn_lab import execute, process_errors
from toolchains import (ROOT, CACHE, EVIDENCE, COMPILER_CONFIG, CANONICAL_COMPILER, digest,
                        runtime_inputs, toolchain_lock, verify_sources, write_json)


def compile_command(script, debug, opt, amx):
    return [str(CANONICAL_COMPILER), str(script), f"-T{COMPILER_CONFIG}", "-C32",
            f"-d{debug}", f"-O{opt}", f"-i{CACHE / 'toolchains/pawn-stable/include'}", f"-o{amx}"]


def artifact_errors(record, script, debug, opt, verify_files):
    errors = []
    binary = Path(record.get("bytecode_path", "/missing"))
    if record.get("compile", {}).get("command") != compile_command(script, debug, opt, binary):
        errors.append("example compiler command differs from selected source/configuration")
    if record.get("compile", {}).get("returncode") == 0:
        if verify_files and (not binary.is_file() or digest(binary) != record.get("bytecode_sha256")):
            errors.append("example bytecode missing or changed")
        if record.get("runtime", {}).get("command") != [str(CACHE / "build32/pawnrun"), str(binary)]:
            errors.append("example runtime command differs from selected canonical host")
    return errors


def snapshot():
    prior = ROOT / "research/pawn/prior"
    return {"actual_files": runtime_inputs(), "prior_manifests": {
        str(p.relative_to(ROOT)): digest(p) for p in prior.glob("*.json")}}


def exercise_errors(result, prediction, verify_files=False):
    errors = process_errors(result.get("compile", {}), verify_files)
    n, debug = result["exercise"], result["debug"]
    diagnostics = [int(x) for x in re.findall(r"(?:warning|error) (\d+):", result["compile"].get("output", ""))]
    expected_diagnostics = [237] if n == 5 and debug == 2 else []
    if result["compile"].get("returncode") != 0 or diagnostics != expected_diagnostics:
        errors.append("exercise compiler exit or diagnostics mismatch")
    ran = result.get("runtime", {})
    errors += process_errors(ran, verify_files)
    output = re.sub(r"\x1b\[[0-9;]*m", "", ran.get("output", "")).strip()
    if ran.get("returncode") != 0 or output != prediction:
        errors.append("exercise output differs from independent prediction")
    if result.get("expected_output") != prediction or result.get("expected_diagnostics") != expected_diagnostics:
        errors.append("stored expectation differs from authoritative prediction")
    return errors


def validate_report(report, verify_files=True):
    failures = []
    prior = ROOT / "research/pawn/prior"
    predictions = json.loads((prior / "independent-exercise-predictions.json").read_text())
    corpus = json.loads((prior / "prior-examples-audit.json").read_text())
    expected_audit = {f"{item['deck']}-{item['slide']:02d}": item for item in corpus}
    audits = report.get("audit", [])
    if len(expected_audit) != 47 or len(audits) != 47 or {r['name'] for r in audits} != set(expected_audit):
        failures.append("prior audit must contain exactly the 47 unique preserved snippets")
    for record in audits:
        item = expected_audit.get(record["name"])
        if item is None:
            continue
        wrapper = item["wrapper_prefix"] + item["source"] + item["wrapper_suffix"] + "\n"
        if (record.get("wrapped_source_sha256") != hashlib.sha256(wrapper.encode()).hexdigest() or
                record.get("original_snippet") != item["source"] or record.get("classification") != item["classification"]):
            failures.append(f"prior snippet or wrapper changed: {record['name']}")
        compiled = record.get("compile", {})
        script = Path(record.get("wrapped_source_path", "/missing"))
        errors = artifact_errors(record, script, 2, 0, verify_files)
        if verify_files and (not script.is_file() or script.read_text() != wrapper):
            errors.append("preserved wrapper file missing or changed")
        errors += process_errors(compiled, verify_files)
        if compiled.get("returncode") == 0:
            errors += process_errors(record.get("runtime", {}), verify_files)
            if record.get("runtime", {}).get("returncode") != 0:
                errors.append("compiled prior snippet did not execute successfully; disposition required")
        elif not re.search(r"(?:fatal )?error \d+:", compiled.get("output", "")):
            errors.append("prior snippet failed without an error diagnostic")
        if errors:
            failures.append(f"prior audit {record['name']}: {errors}")
    expected = {(n, d, o) for n in range(1, 6) for d in (0, 2) for o in (0, 1, 2, 3)}
    observed = report.get("exercises", [])
    keys = [(r["exercise"], r["debug"], r["optimization"]) for r in observed]
    if len(keys) != 40 or set(keys) != expected:
        failures.append("independent exercises must cover exactly 40 unique selected profiles")
    for result in observed:
        n, debug, opt = result["exercise"], result["debug"], result["optimization"]
        if (n, debug, opt) not in expected:
            continue
        errors = exercise_errors(result, predictions[str(n)], verify_files)
        errors += artifact_errors(result, prior / f"exercise-{n:02d}.p", debug, opt, verify_files)
        if result.get("source_sha256") != digest(prior / f"exercise-{n:02d}.p"):
            errors.append("exercise source changed")
        if result.get("passed") != (not errors):
            errors.append("stored pass flag differs from recomputed oracle")
        if errors:
            failures.append(f"exercise {n}-d{debug}-O{opt}: {errors}")
    if report.get("inputs_before") != snapshot() or report.get("inputs_unchanged") is not True:
        failures.append("prior/example inputs, predictions or toolchain changed since run")
    return failures


def main():
    verify_sources()
    before = snapshot()
    workspace = CACHE / "examples" / str(time.time_ns())
    prior = ROOT / "research/pawn/prior"
    cc, vm = CANONICAL_COMPILER, CACHE / "build32/pawnrun"
    include = CACHE / "toolchains/pawn-stable/include"
    records = json.loads((prior / "prior-examples-audit.json").read_text())
    predictions = json.loads((prior / "independent-exercise-predictions.json").read_text())
    report = {"schema": 2, "inputs_before": before, "purpose": "Preserved-example audit plus independent combined-feature exercises",
              "compiler_sha256": digest(cc), "vm_sha256": digest(vm),
              "prior_artifacts": json.loads((prior / "original-artifacts.json").read_text()),
              "audit": [], "exercises": []}
    for item in records:
        name = f"{item['deck']}-{item['slide']:02d}"
        directory = workspace / "audit" / name
        directory.mkdir(parents=True, exist_ok=True)
        script = directory / "wrapped.p"
        script.write_text(item["wrapper_prefix"] + item["source"] + item["wrapper_suffix"] + "\n")
        amx = directory / "program.amx"
        amx.unlink(missing_ok=True)
        compiled = execute(compile_command(script, 2, 0, amx), directory / "compile")
        result = {"name": name, "classification": item["classification"], "wrapped_source_sha256": digest(script),
                  "wrapped_source_path": str(script), "bytecode_path": str(amx),
                  "wrapper_prefix": item["wrapper_prefix"], "original_snippet": item["source"],
                  "wrapper_suffix": item["wrapper_suffix"], "compile": compiled}
        if not process_errors(compiled) and compiled["returncode"] == 0 and amx.exists():
            result["bytecode_sha256"] = digest(amx)
            result["runtime"] = execute([vm, amx], directory / "runtime")
        report["audit"].append(result)
    for n in range(1, 6):
        script = prior / f"exercise-{n:02d}.p"
        for debug in (0, 2):
            for opt in (0, 1, 2, 3):
                directory = workspace / "exercises" / f"{n:02d}-d{debug}-O{opt}"
                directory.mkdir(parents=True, exist_ok=True)
                amx = directory / "program.amx"
                amx.unlink(missing_ok=True)
                compiled = execute(compile_command(script, debug, opt, amx), directory / "compile")
                diagnostic_codes = [int(x) for x in re.findall(r"(?:warning|error) (\d+):", compiled["output"])]
                expected_diagnostics = [237] if n == 5 and debug == 2 else []
                result = {"exercise": n, "debug": debug, "optimization": opt,
                          "source_sha256": digest(script), "bytecode_path": str(amx), "expected_output": predictions[str(n)],
                          "expected_diagnostics": expected_diagnostics, "compile": compiled, "passed": False}
                if not process_errors(compiled) and compiled["returncode"] == 0 and diagnostic_codes == expected_diagnostics and amx.exists():
                    result["bytecode_sha256"] = digest(amx)
                    result["runtime"] = execute([vm, amx], directory / "runtime")
                    output = re.sub(r"\x1b\[[0-9;]*m", "", result["runtime"]["output"]).strip()
                    result["passed"] = not exercise_errors(result, predictions[str(n)], True)
                report["exercises"].append(result)
    report["summary"] = {"audited_snippets": len(report["audit"]),
                         "standalone_prior_programs": sum(x["classification"] == "standalone" for x in report["audit"]),
                         "prior_compile_successes": sum(x["compile"]["returncode"] == 0 for x in report["audit"]),
                         "exercises_passed": sum(x["passed"] for x in report["exercises"]),
                         "exercise_profiles": len(report["exercises"])}
    report["inputs_unchanged"] = before == snapshot()
    report["validation_failures"] = validate_report(report)
    write_json(workspace / "results.json", report)
    write_json(EVIDENCE / "pawn-examples-results.json", report)
    print(json.dumps(report["summary"]))
    raise SystemExit(0 if not report["validation_failures"] else 1)


if __name__ == "__main__":
    with toolchain_lock():
        main()

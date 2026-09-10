#!/usr/bin/env python3
"""Execute source-backed PAWN checks. A passing test suite is NOT the proficiency gate."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import time

from toolchains import (ROOT, CACHE, EVIDENCE, COMPILER_CONFIG, digest, tree_digest,
                        runtime_inputs, toolchain_lock, verify_sources, write_json)


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (2 * 1024 * 1024, 2 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def execute(command, directory):
    """No shell. Bounded process group, disk output, CPU and address space."""
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "process-output.txt"
    started = time.monotonic()
    environment = dict(os.environ)
    environment["LC_ALL"] = "C"
    environment["AMXLIB"] = str(Path(command[0]).parent)
    environment["LD_LIBRARY_PATH"] = str(Path(command[0]).parent)
    with output.open("wb") as sink:
        process = subprocess.Popen([str(x) for x in command], cwd=ROOT, stdout=sink, stderr=subprocess.STDOUT,
                                   preexec_fn=limits, start_new_session=True, env=environment)
        timed_out = False
        try:
            rc = process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            rc = process.wait()
    return {"command": [str(x) for x in command], "returncode": rc, "timeout": timed_out,
            "seconds": round(time.monotonic() - started, 3), "output": output.read_text(errors="replace"),
            "output_path": str(output), "output_sha256": digest(output),
            "output_limit_reached": output.stat().st_size >= 2 * 1024 * 1024,
            "environment": {k: environment[k] for k in ("LC_ALL", "AMXLIB", "LD_LIBRARY_PATH")}}


def profiles(bits):
    if bits == 32:
        return [(d, o) for d in (0, 1, 2) for o in (0, 1, 2, 3)]
    if bits == 64:
        return [(d, o) for d in (0, 2) for o in (0, 1, 3)]
    return [(0, 0), (2, 0), (2, 1)]


def execution_inputs_hash():
    # Documentation and the independent advancement decision affect the gate,
    # but editing them does not change compiled test inputs. Keeping these
    # separate avoids a review -> rerun -> review fingerprint dependency cycle.
    paths = [p for p in (ROOT / "research/pawn").rglob("*")
             if p.is_file() and p.suffix in (".p", ".inc", ".c", ".h")]
    paths.append(ROOT / "research/pawn/cases.json")
    values = {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def process_errors(process, verify_files=False):
    errors = []
    if process.get("timeout") is not False:
        errors.append("process timed out or timeout status missing")
    if process.get("output_limit_reached") is not False:
        errors.append("process output limit reached or status missing")
    if type(process.get("returncode")) is not int or process["returncode"] < 0:
        errors.append("process crashed or exit status missing")
    if verify_files:
        path = Path(process.get("output_path", "/missing"))
        if (not path.is_file() or digest(path) != process.get("output_sha256") or
                path.read_text(errors="replace") != process.get("output")):
            errors.append("raw process log missing or changed")
    return errors


def validate_compile(compiled, case, debug, verify_files=False):
    errors = process_errors(compiled, verify_files)
    diagnostics = [int(x) for x in re.findall(r"(?:error|warning) (\d+):", compiled.get("output", ""))]
    expected = case.get("diagnostics_by_debug", {}).get(str(debug), case.get("diagnostics", []))
    if collections.Counter(diagnostics) != collections.Counter(expected):
        errors.append(f"diagnostics {diagnostics} != {expected}")
    if case.get("compile_fails", False):
        if compiled.get("returncode", -1) <= 0 or not re.search(r"(?:fatal )?error \d+:", compiled.get("output", "")):
            errors.append("expected diagnostic failure needs a normal positive exit and an error diagnostic")
    elif compiled.get("returncode") != 0:
        errors.append("unexpected compiler exit status")
    return errors


def validate_runtime(ran, case, bits, debug, verify_files=False):
    errors = process_errors(ran, verify_files)
    output = ran.get("output", "")
    matches = re.findall(r"^lab: bits=(\d+) checks=(\d+) failures=(\d+) result=(-?\d+) error=(\d+) sleeps=(\d+)$", output, re.M)
    stages = re.findall(r"^phase: init=(-?\d+) register=(-?\d+) exec_entered=(\d+) stage=(\w+)$", output, re.M)
    if stages != [("0", "0", "1", "exec")]:
        errors.append("runtime result did not follow successful initialization, registration and execution entry")
    if len(matches) != 1:
        return errors + ["missing or duplicate complete host result"]
    b, checks, failures, result, error, sleeps = map(int, matches[0])
    expected_error = case.get("release_error", case.get("error", 0)) if debug == 0 else case.get("error", 0)
    expected_result = case.get("release_result", case.get("result", 0)) if debug == 0 else case.get("result", 0)
    if (b, checks, failures, error, sleeps) != (bits, case["checks"], 0, expected_error, case.get("sleeps", 0)):
        errors.append("runtime observation differs from explicit expectation")
    if expected_error == 0 and result != expected_result:
        errors.append(f"return value {result} != {expected_result}")
    if ran.get("returncode") != (2 if expected_error else 0):
        errors.append("unexpected host exit status")
    if "host_checks" in case:
        hosts = re.findall(r"^host: checks=(\d+) failures=(\d+) debug_breaks=(\d+)$", output, re.M)
        if len(hosts) != 1 or tuple(map(int, hosts[0][:2])) != (case["host_checks"], 0):
            errors.append("host contract checks incomplete or failed")
    return errors


def selected_profiles(manifest):
    result = {}
    cases = manifest["cases"]
    if not cases or len({c["id"] for c in cases}) != len(cases):
        raise ValueError("empty or duplicate case inventory")
    for case in cases:
        if not case["widths"] or len(set(case["widths"])) != len(case["widths"]):
            raise ValueError("empty or duplicate width selection")
        for bits in case["widths"]:
            if type(bits) is not int or bits not in (16, 32, 64):
                raise ValueError("invalid cell width")
            for debug, opt in profiles(bits):
                if case.get("checked_only") and debug == 0:
                    continue
                if case.get("hazard") == "invalid-memory" and debug == 0:
                    raise ValueError("Unchecked invalid-memory correctness tests are forbidden")
                result[f"{case['id']}-C{bits}-d{debug}-O{opt}"] = (case, bits, debug, opt)
    return result


def compile_command(case, bits, debug, opt, amx):
    return [str(CACHE / f"build{bits}/pawncc"), str(ROOT / f"research/pawn/cases/{case['id']}.p"),
            f"-T{COMPILER_CONFIG}", f"-C{bits}", f"-d{debug}", f"-O{opt}", "-S1024", "-p",
            f"-i{ROOT / 'research/pawn/include'}", f"-i{CACHE / 'toolchains/pawn-stable/include'}", f"-o{amx}"]


def validate_record(record, case, bits, debug, opt, verify_files=True):
    errors = validate_compile(record["compile"], case, debug, verify_files)
    if (record.get("case"), record.get("bits"), record.get("debug"), record.get("optimization")) != (case["id"], bits, debug, opt):
        errors.append("profile metadata differs from selection")
    if record.get("source_sha256") != digest(ROOT / f"research/pawn/cases/{case['id']}.p"):
        errors.append("source hash differs")
    amx = Path(record.get("bytecode_path", "/missing"))
    if record["compile"].get("command") != compile_command(case, bits, debug, opt, amx):
        errors.append("compiler command differs from selected configuration")
    if not case.get("compile_fails") and not errors:
        if not amx.is_file() or digest(amx) != record.get("bytecode_sha256"):
            errors.append("missing or changed bytecode")
        ran = record.get("runtime", {})
        if ran.get("command") != [str(CACHE / f"build{bits}/labrun"), str(amx), *case.get("host_args", [])]:
            errors.append("runtime command differs from selected host")
        errors += validate_runtime(ran, case, bits, debug, verify_files)
    elif case.get("compile_fails") and "runtime" in record:
        errors.append("negative compilation unexpectedly executed")
    return errors


def snapshot():
    return {"actual_files": runtime_inputs(),
            "cases_manifest_sha256": digest(ROOT / "research/pawn/cases.json"),
            "test_inputs_sha256": execution_inputs_hash()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="one case id; does not update the full-suite record")
    args = parser.parse_args()
    verify_sources()
    before = snapshot()
    manifest = json.loads((ROOT / "research/pawn/cases.json").read_text())
    selected = selected_profiles(manifest)
    records = []
    run_id = str(time.time_ns())
    workspace = CACHE / "runs/original" / run_id
    for name, (case, bits, debug, optimization) in selected.items():
        if args.case and args.case != case["id"]:
            continue
        work = workspace / name
        work.mkdir(parents=True, exist_ok=False)
        amx = work / "program.amx"
        source = ROOT / "research/pawn/cases" / f"{case['id']}.p"
        compiled = execute(compile_command(case, bits, debug, optimization, amx), work / "compile")
        record = {"name": name, "case": case["id"], "source_sha256": digest(source),
                  "bits": bits, "debug": debug, "optimization": optimization,
                  "compile": compiled, "bytecode_path": str(amx)}
        if not case.get("compile_fails") and not validate_compile(compiled, case, debug) and amx.is_file():
            record["bytecode_sha256"] = digest(amx)
            record["runtime"] = execute([CACHE / f"build{bits}/labrun", amx, *case.get("host_args", [])], work / "runtime")
        errors = validate_record(record, case, bits, debug, optimization)
        record["failures"] = errors
        record["status"] = "FAIL" if errors else "PASS"
        records.append(record)
        if errors:
            print(name + ": " + "; ".join(errors))
    if not records:
        raise SystemExit("No matching cases")
    unchanged = before == snapshot()
    report = {"schema": 2, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "inputs_before": before, "inputs_unchanged": unchanged,
              "cases_manifest_sha256": before["cases_manifest_sha256"],
              "test_inputs_sha256": before["test_inputs_sha256"],
              "toolchains_manifest_sha256": before["actual_files"]["research/evidence/toolchains.json"],
              "harness_sha256": before["actual_files"]["research/tools/pawn_lab.py"], "total": len(records),
              "passed": sum(r["status"] == "PASS" for r in records), "records": records}
    write_json(workspace / "results.json", report)
    target = CACHE / "runs/original/results.json" if args.case else EVIDENCE / "pawn-original-results.json"
    write_json(target, report)
    print(f"{report['passed']}/{report['total']} profiles passed; unchanged inputs: {unchanged}; {target.relative_to(ROOT)}")
    raise SystemExit(0 if unchanged and report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    with toolchain_lock():
        main()

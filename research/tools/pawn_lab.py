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

from toolchains import ROOT, CACHE, EVIDENCE, digest, tree_digest


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
    with output.open("wb") as sink:
        process = subprocess.Popen([str(x) for x in command], cwd=ROOT, stdout=sink, stderr=subprocess.STDOUT,
                                   preexec_fn=limits, start_new_session=True)
        timed_out = False
        try:
            rc = process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            rc = process.wait()
    return {"command": [str(x) for x in command], "returncode": rc, "timeout": timed_out,
            "seconds": round(time.monotonic() - started, 3), "output": output.read_text(errors="replace")}


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="one case id; does not update the full-suite record")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "research/pawn/cases.json").read_text())
    records = []
    for case in manifest["cases"]:
        if args.case and args.case != case["id"]:
            continue
        for bits in case["widths"]:
            for debug, optimization in profiles(bits):
                if case.get("checked_only") and debug == 0:
                    continue
                if case.get("hazard") == "invalid-memory" and debug == 0:
                    raise RuntimeError("Unchecked invalid-memory correctness tests are forbidden")
                name = f"{case['id']}-C{bits}-d{debug}-O{optimization}"
                work = CACHE / "runs/original" / name
                work.mkdir(parents=True, exist_ok=True)
                amx = work / "program.amx"
                amx.unlink(missing_ok=True)  # stale bytecode can never satisfy this run
                compiler = CACHE / f"build{bits}" / "pawncc"
                source = ROOT / "research/pawn/cases" / f"{case['id']}.p"
                compiled = execute([compiler, source, f"-C{bits}", f"-d{debug}", f"-O{optimization}",
                                    "-S1024", "-p", f"-i{ROOT / 'research/pawn/include'}",
                                    f"-i{CACHE / 'toolchains/pawn-stable/include'}", f"-o{amx}"], work / "compile")
                diagnostics = [int(x) for x in re.findall(r"(?:error|warning) (\d+):", compiled["output"])]
                errors = []
                if compiled["timeout"]:
                    errors.append("compiler timeout")
                expected_diagnostics = case.get("diagnostics_by_debug", {}).get(str(debug), case.get("diagnostics", []))
                if collections.Counter(diagnostics) != collections.Counter(expected_diagnostics):
                    errors.append(f"diagnostics {diagnostics} != {expected_diagnostics}")
                failed = case.get("compile_fails", False)
                if (compiled["returncode"] != 0) != failed:
                    errors.append("unexpected compiler exit status")
                record = {"name": name, "case": case["id"], "source_sha256": digest(source),
                          "bits": bits, "debug": debug, "optimization": optimization, "compile": compiled}
                if not failed and not errors:
                    if not amx.is_file():
                        errors.append("missing bytecode")
                    else:
                        record["bytecode_sha256"] = digest(amx)
                        ran = execute([CACHE / f"build{bits}/labrun", amx, *case.get("host_args", [])], work / "runtime")
                        record["runtime"] = ran
                        match = re.search(r"lab: bits=(\d+) checks=(\d+) failures=(\d+) result=(-?\d+) error=(\d+) sleeps=(\d+)", ran["output"])
                        if ran["timeout"] or not match:
                            errors.append("runtime timeout or missing complete host result")
                        else:
                            b, checks, failures, result, error, sleeps = map(int, match.groups())
                            expected_error = case.get("release_error", case.get("error", 0)) if debug == 0 else case.get("error", 0)
                            expected_result = case.get("release_result", case.get("result", 0)) if debug == 0 else case.get("result", 0)
                            if b != bits or checks != case["checks"] or failures != 0 or error != expected_error or sleeps != case.get("sleeps", 0):
                                errors.append("runtime observation differs from explicit expectation")
                            if expected_error == 0 and result != expected_result:
                                errors.append(f"return value {result} != {expected_result}")
                            if ran["returncode"] != (2 if expected_error else 0):
                                errors.append("unexpected host exit status")
                            if "host_checks" in case:
                                host = re.search(r"host: checks=(\d+) failures=(\d+) debug_breaks=(\d+)", ran["output"])
                                if not host or int(host[1]) != case["host_checks"] or int(host[2]) != 0:
                                    errors.append("host contract checks incomplete or failed")
                record["failures"] = errors
                record["status"] = "FAIL" if errors else "PASS"
                records.append(record)
                if errors:
                    print(name + ": " + "; ".join(errors))
    if not records:
        raise SystemExit("No matching cases")
    report = {"schema": 1, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "cases_manifest_sha256": digest(ROOT / "research/pawn/cases.json"),
              "test_inputs_sha256": execution_inputs_hash(),
              "toolchains_manifest_sha256": digest(EVIDENCE / "toolchains.json"),
              "harness_sha256": digest(__file__), "total": len(records),
              "passed": sum(r["status"] == "PASS" for r in records), "records": records}
    target = CACHE / "runs/original/results.json" if args.case else EVIDENCE / "pawn-original-results.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{report['passed']}/{report['total']} profiles passed; {target.relative_to(ROOT)}")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()

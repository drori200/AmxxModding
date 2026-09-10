#!/usr/bin/env python3
"""Fail-closed PAWN advancement gate. No AMXX work is performed by this module."""
import argparse
import collections
import hashlib
import json
import time
from pathlib import Path

from toolchains import (ROOT, CACHE, EVIDENCE, COMPILER_CONFIG, digest, tree_digest,
                        verify_sources, toolchain_lock, write_json)
from pawn_lab import profiles, execution_inputs_hash, selected_profiles, validate_record, snapshot
from pawn_examples import validate_report as validate_examples
import upstream_pawn

GATE = EVIDENCE / "pawn-gate.json"


def load(path, failures):
    absolute = ROOT / path
    if not absolute.is_file():
        failures.append(f"Missing required evidence: {path}")
        return {}
    try:
        return json.loads(absolute.read_text())
    except (ValueError, OSError) as error:
        failures.append(f"Unreadable evidence {path}: {error}")
        return {}


def input_hashes():
    paths = [p for p in (ROOT / "research/pawn").rglob("*") if p.is_file()]
    paths += [p for p in (ROOT / "research/tools").glob("*.py")
              if p.name.startswith(("pawn_", "upstream_pawn", "test_pawn")) or p.name == "toolchains.py"]
    paths += [p for p in EVIDENCE.glob("*.json")
              if p != GATE and (p.name.startswith("pawn-") or p.name in ("sources.json", "toolchains.json"))]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}


def validate_upstream_evidence(report):
    failures = []
    inputs = report.get("inputs", {})
    for role, executable in (("compiler", "pawncc"), ("runner", "pawnrun")):
        current = CACHE / f"build32/{executable}"
        recorded = Path(inputs.get(role, "/missing"))
        if (not recorded.is_file() or digest(recorded) != inputs.get(role + "_sha256") or
                digest(current) != inputs.get(role + "_sha256")):
            failures.append(f"Official-suite {role} differs from the current canonical tool")
    include = CACHE / "toolchains/pawn-stable/include"
    if inputs.get("headers_sha256") != upstream_pawn.tree_hashes(include):
        failures.append("Official-suite headers differ from current canonical includes")
    if inputs.get("optional_libraries_sha256") != upstream_pawn.tree_hashes(CACHE / "build32", "amx*.so*"):
        failures.append("Official-suite optional libraries differ from current canonical build")
    if inputs.get("optional_libraries_sha256") != upstream_pawn.tree_hashes(Path(inputs.get("runner", "/missing")).parent, "amx*.so*"):
        failures.append("Official-suite selected runner libraries are missing or changed")
    if inputs.get("config_sha256") != digest(COMPILER_CONFIG):
        failures.append("Official-suite explicit compiler configuration is absent or stale")
    if upstream_pawn.tree_hashes(Path(inputs.get("include", "/missing"))) != inputs.get("headers_sha256"):
        failures.append("Official-suite selected include tree is missing or changed")
    profile = report.get("profile", {})
    if (profile.get("cell_bits"), profile.get("debug"), profile.get("optimization_override"),
            profile.get("default_optimization"), profile.get("fortify_attested")) != (32, 2, None, 2, False):
        failures.append("Official-suite baseline configuration is not the selected checked 32-bit profile")
    manifest = json.loads((ROOT / "research/pawn/upstream-expectations.json").read_text())
    cases = {case["id"]: case for case in manifest["cases"]}
    if len(cases) != 161 or len(manifest["cases"]) != 161:
        failures.append("Official-suite expectation inventory is not exactly 161 unique cases")
    exceptional = []
    for record in report.get("results", []):
        case = cases.get(record["id"])
        if case is None:
            failures.append("Unknown official-suite case")
            continue
        if len(record.get("steps", [])) != len(case["steps"]):
            failures.append(f"Official case {record['id']} has missing or duplicate steps")
            continue
        # Exceptional outcomes never become a pass via a summary flag. Their
        # bounded advancement dispositions and independent review are still due.
        if record.get("status") not in ("verified", "expected_failure"):
            exceptional.append(record["id"])
        for step, observed in zip(case["steps"], record["steps"]):
            compiled = observed["compile"]
            binary = Path(compiled["cwd"]) / "result.amx"
            issues = upstream_pawn.validate_compile(dict(compiled), step["expect"], binary)
            if observed.get("original_argv") != step["compile"]:
                failures.append(f"Official case {record['id']} command selection changed")
            expected_command = upstream_pawn.compile_command(inputs.get("compiler"), step, 2, None,
                                                              inputs.get("include"), binary)
            if compiled["command"] != expected_command:
                failures.append(f"Official case {record['id']} compiler command differs from selected profile")
            for filename, sha in manifest["suite"]["original_files"].items():
                path = Path(compiled["cwd"]) / filename
                if not path.is_file() or digest(path) != sha:
                    failures.append(f"Official case {record['id']} preserved source changed: {filename}")
            if binary.exists() and digest(binary) != observed.get("amx_sha256"):
                failures.append(f"Official case {record['id']} bytecode changed")
            if record.get("status") in ("verified", "expected_failure") and issues:
                failures.append(f"Official case {record['id']} raw compile evidence fails its oracle")
            if "run" in step and record.get("status") in ("verified", "expected_failure"):
                if "runtime" not in observed:
                    failures.append(f"Official case {record['id']} runtime evidence is missing")
                else:
                    if observed["runtime"]["command"] != [inputs.get("runner"), str(binary)]:
                        failures.append(f"Official case {record['id']} runner differs from selected canonical host")
                    runtime_issues, variants = upstream_pawn.validate_runtime(dict(observed["runtime"]), step["runtime_expect"])
                    if runtime_issues or variants:
                        failures.append(f"Official case {record['id']} runtime requires a disposition")
            for process in [compiled] + ([observed["runtime"]] if "runtime" in observed else []):
                logfile = Path(process["log"])
                if (not logfile.is_file() or digest(logfile) != process["log_sha256"] or
                        logfile.read_bytes().decode(errors="replace") != process["output"]):
                    failures.append(f"Official case {record['id']} raw log missing or changed")
    if exceptional:
        failures.append(f"Official-suite exceptional cases need reviewed advancement dispositions: {exceptional}")
    if dict(collections.Counter(r.get("status") for r in report.get("results", []))) != report.get("summary"):
        failures.append("Official-suite summary contradicts individual outcomes")
    return failures


def evaluate_unchecked():
    failures = []
    try:
        verify_sources()
    except (ValueError, OSError, RuntimeError) as error:
        failures.append(f"Official compiler provenance verification failed: {error}")
    sources = load("research/evidence/sources.json", failures)
    for source in sources if isinstance(sources, list) else []:
        path = ROOT / source["path"]
        if not path.is_file() or digest(path) != source["sha256"]:
            failures.append(f"Source archive/document absent or changed: {source['id']}")
    tools = load("research/evidence/toolchains.json", failures)
    for bits in (16, 32, 64):
        config = tools.get("stable", {}).get(str(bits), {})
        source = ROOT / config.get("source", ".cache/research/missing")
        if source != CACHE / "toolchains/pawn-stable" or config.get("cell_bits") != bits:
            failures.append(f"C{bits} configuration does not select the canonical source and cell width")
        compiler_path = f".cache/research/build{bits}/pawncc"
        if compiler_path not in config.get("binaries", {}):
            failures.append(f"C{bits} compiler identity missing from tool manifest")
        flags_path = CACHE / f"build{bits}/compiler/CMakeFiles/pawncc.dir/flags.make"
        flags = flags_path.read_text() if flags_path.is_file() else ""
        if f"-DPAWN_CELL_SIZE={bits}" not in flags or "-std=gnu99" not in flags:
            failures.append(f"C{bits} generated build flags do not verify the selected cell width and C99")
        if not source.is_dir() or tree_digest(source) != config.get("source_tree_sha256"):
            failures.append(f"Canonical C{bits} source tree changed or missing")
        for name, expected in config.get("binaries", {}).items():
            binary = ROOT / name
            if not binary.is_file() or digest(binary) != expected:
                failures.append(f"Tool binary changed or missing: {name}")
        host = CACHE / f"build{bits}/labrun"
        if not host.is_file() or digest(host) != tools.get("hosts", {}).get(str(bits), {}).get("sha256"):
            failures.append(f"C{bits} lab host changed or missing")
        host_sources = tools.get("hosts", {}).get(str(bits), {}).get("sources_sha256", {})
        if not host_sources:
            failures.append(f"C{bits} lab host source provenance missing")
        for path, expected in host_sources.items():
            if not (ROOT / path).is_file() or digest(ROOT / path) != expected:
                failures.append(f"C{bits} lab host is stale after source change: {path}")

    cases = load("research/pawn/cases.json", failures)
    original = load("research/evidence/pawn-original-results.json", failures)
    for path, key in [("research/pawn/cases.json", "cases_manifest_sha256"),
                      ("research/tools/pawn_lab.py", "harness_sha256"),
                      ("research/evidence/toolchains.json", "toolchains_manifest_sha256")]:
        if original.get(key) != digest(ROOT / path):
            failures.append(f"Original-suite evidence is stale: {path}")
    if original.get("test_inputs_sha256") != execution_inputs_hash():
        failures.append("Original-suite executable inputs changed since its run")
    expected_profiles = selected_profiles(cases)
    observed = original.get("records", [])
    if len(observed) != len(expected_profiles) or {r["name"] for r in observed} != set(expected_profiles):
        failures.append("Original-suite results do not cover the complete selected profile matrix")
    if original.get("inputs_unchanged") is not True or original.get("inputs_before") != snapshot():
        failures.append("Original-suite actual inputs changed during or after its run")
    unresolved = []
    for record in observed:
        if record["name"] not in expected_profiles:
            continue
        errors = validate_record(record, *expected_profiles[record["name"]])
        if record.get("status") != ("FAIL" if errors else "PASS"):
            failures.append(f"Original-suite stored status contradicts raw evidence: {record['name']}")
        if errors:
            unresolved.append(record["name"])
    if unresolved:
        failures.append(f"{len(unresolved)} original profile failures need reviewed, bounded dispositions")

    upstream = load("research/evidence/pawn-upstream-results.json", failures)
    if not upstream.get("complete") or len(upstream.get("results", [])) != 161 or {r["id"] for r in upstream.get("results", [])} != set(range(1, 162)):
        failures.append("Official regression evidence is incomplete")
    if not upstream.get("source_integrity_after") or not upstream.get("toolchain_integrity_after"):
        failures.append("Official regression source/tool integrity is unverified")
    if upstream.get("inputs", {}).get("adapter_sha256") != digest(ROOT / "research/tools/upstream_pawn.py"):
        failures.append("Official regression adapter changed since its run")
    if upstream.get("inputs", {}).get("manifest_sha256") != digest(ROOT / "research/pawn/upstream-expectations.json"):
        failures.append("Official regression expectation manifest changed since its run")
    if upstream.get("summary", {}).get("unexpected_failure"):
        failures.append("Official regressions contain unexplained failures")
    failures.extend(validate_upstream_evidence(upstream))

    exercises = load("research/evidence/pawn-examples-results.json", failures)
    failures.extend(validate_examples(exercises))

    inventory = load("research/pawn/coverage-inventory.json", failures)
    dispositions = load("research/pawn/coverage-evidence.json", failures)
    rows = {r["id"]: r for r in dispositions.get("items", [])}
    expected_topics = {f"L{n:02d}" for n in range(1, 61)} | {f"I{n:02d}" for n in range(1, 27)}
    if len(inventory.get("inventory", [])) != 86 or {r["id"] for r in inventory.get("inventory", [])} != expected_topics:
        failures.append("Guide inventory has missing, duplicate or unexpected topics")
    if len(rows) != len(dispositions.get("items", [])) or not set(rows) <= expected_topics:
        failures.append("Coverage evidence has duplicate or unknown dispositions")
    missing = []
    for item in inventory.get("inventory", []):
        row = rows.get(item["id"], {})
        if row.get("status") not in ("verified", "bounded_limitation", "inapplicable"):
            missing.append(item["id"])
            continue
        if not row.get("rationale") or not row.get("evidence") or not row.get("independent_review"):
            missing.append(item["id"])
        for evidence in row.get("evidence", []):
            path = ROOT / evidence["path"]
            if not path.is_file() or digest(path) != evidence["sha256"]:
                failures.append(f"Coverage evidence changed for {item['id']}")
    if not inventory.get("inventory") or missing:
        failures.append(f"{len(missing)} guide topics lack complete reviewed evidence dispositions")
    if dispositions.get("unresolved_questions_required_by_amxx", ["review not recorded"]):
        failures.append("Unresolved PAWN questions required by the next phase remain")
    controls = load("research/evidence/pawn-audit-controls.json", failures)
    from toolchains import runtime_inputs
    if (controls.get("passed") is not True or controls.get("failures") != 0 or controls.get("errors") != 0
            or controls.get("harness_sha256") != digest(ROOT / "research/tools/test_pawn_audit.py")
            or controls.get("actual_inputs") != runtime_inputs()):
        failures.append("Gate instrument negative controls are failing or stale")
    review = load("research/pawn/advancement-review.json", failures)
    if review.get("outcome") != "approve" or review.get("reviewed_input_hashes") != input_hashes_without_review():
        failures.append("A current independent advancement review is missing or requires changes")
    inputs = input_hashes()
    return {"schema": 1, "status": "FAIL" if failures else "PASS",
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "failures": failures, "unresolved_profiles": unresolved,
            "unresolved_inventory_ids": missing, "input_hashes": inputs,
            "input_fingerprint": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
            "meaning": "A bounded advancement decision for recorded configurations, never universal mastery"}


def evaluate():
    # Malformed evidence must never escape as a successful gate invocation.
    before = input_hashes()
    try:
        report = evaluate_unchecked()
    except (KeyError, TypeError, ValueError, OSError, RuntimeError, AttributeError) as error:
        report = {"schema": 1, "status": "FAIL", "failures": [f"Invalid or incomplete gate evidence: {error}"],
                  "input_hashes": before}
    if input_hashes() != before:
        report["status"] = "FAIL"
        report["failures"].append("Gate inputs changed during validation")
    return report


def input_hashes_without_review():
    return {path: sha for path, sha in input_hashes().items() if path != "research/pawn/advancement-review.json"}


def require_current_pass():
    try:
        with toolchain_lock():
            return require_current_pass_locked()
    except (RuntimeError, ValueError, OSError) as error:
        raise SystemExit(f"AMXX phase locked: unable to validate PAWN gate: {error}") from error


def require_current_pass_locked():
    if not GATE.is_file():
        raise SystemExit("AMXX phase locked: no PAWN gate record. Run research:pawn:gate.")
    recorded = json.loads(GATE.read_text())
    current = evaluate()
    if recorded.get("status") != "PASS" or current["status"] != "PASS" or recorded.get("input_hashes") != current["input_hashes"]:
        raise SystemExit("AMXX phase locked: PAWN gate is failing or stale. See research/evidence/pawn-gate.json.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="write the current PASS/FAIL evidence record")
    args = parser.parse_args()
    report = evaluate()
    if args.record:
        write_json(GATE, report)
    print("PAWN gate: " + report["status"])
    for failure in report["failures"]:
        print("- " + failure)
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    with toolchain_lock():
        main()

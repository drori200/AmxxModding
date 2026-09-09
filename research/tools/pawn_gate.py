#!/usr/bin/env python3
"""Fail-closed PAWN advancement gate. No AMXX work is performed by this module."""
import argparse
import hashlib
import json
import time
from pathlib import Path

from toolchains import ROOT, CACHE, EVIDENCE, digest, tree_digest
from pawn_lab import profiles, execution_inputs_hash

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


def evaluate():
    failures = []
    sources = load("research/evidence/sources.json", failures)
    for source in sources if isinstance(sources, list) else []:
        path = ROOT / source["path"]
        if not path.is_file() or digest(path) != source["sha256"]:
            failures.append(f"Source archive/document absent or changed: {source['id']}")
    tools = load("research/evidence/toolchains.json", failures)
    for bits in (16, 32, 64):
        config = tools.get("stable", {}).get(str(bits), {})
        source = ROOT / config.get("source", ".cache/research/missing")
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
    expected_profiles = {f"{case['id']}-C{bits}-d{debug}-O{opt}"
                         for case in cases.get("cases", []) for bits in case["widths"]
                         for debug, opt in profiles(bits) if not (case.get("checked_only") and debug == 0)}
    observed = original.get("records", [])
    if len(observed) != len(expected_profiles) or {r["name"] for r in observed} != expected_profiles:
        failures.append("Original-suite results do not cover the complete selected profile matrix")
    unresolved = [r["name"] for r in observed if r.get("status") != "PASS"]
    if unresolved:
        failures.append(f"{len(unresolved)} original profile failures need reviewed, bounded dispositions")

    upstream = load("research/evidence/pawn-upstream-results.json", failures)
    if not upstream.get("complete") or {r["id"] for r in upstream.get("results", [])} != set(range(1, 162)):
        failures.append("Official regression evidence is incomplete")
    if not upstream.get("source_integrity_after") or not upstream.get("toolchain_integrity_after"):
        failures.append("Official regression source/tool integrity is unverified")
    if upstream.get("inputs", {}).get("adapter_sha256") != digest(ROOT / "research/tools/upstream_pawn.py"):
        failures.append("Official regression adapter changed since its run")
    if upstream.get("inputs", {}).get("manifest_sha256") != digest(ROOT / "research/pawn/upstream-expectations.json"):
        failures.append("Official regression expectation manifest changed since its run")
    if upstream.get("summary", {}).get("unexpected_failure"):
        failures.append("Official regressions contain unexplained failures")

    exercises = load("research/evidence/pawn-examples-results.json", failures)
    if len(exercises.get("audit", [])) != 47 or len(exercises.get("exercises", [])) != 40:
        failures.append("Prior-example audit or independent exercise matrix is incomplete")
    if not all(r.get("passed") for r in exercises.get("exercises", [])):
        failures.append("An independent exercise failed")
    for result in exercises.get("exercises", []):
        path = ROOT / f"research/pawn/prior/exercise-{result['exercise']:02d}.p"
        if result.get("source_sha256") != digest(path):
            failures.append("Independent exercise evidence is stale")
            break

    inventory = load("research/pawn/coverage-inventory.json", failures)
    dispositions = load("research/pawn/coverage-evidence.json", failures)
    rows = {r["id"]: r for r in dispositions.get("items", [])}
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


def input_hashes_without_review():
    return {path: sha for path, sha in input_hashes().items() if path != "research/pawn/advancement-review.json"}


def require_current_pass():
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
        GATE.write_text(json.dumps(report, indent=2) + "\n")
    print("PAWN gate: " + report["status"])
    for failure in report["failures"]:
        print("- " + failure)
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()

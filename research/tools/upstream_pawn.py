#!/usr/bin/env python3
"""Bounded, source-oracled adapter for CompuPhase's 161 manual REXX tests.

The REXX suite is a *manual* test driver: its exit status is not a verdict.
This adapter validates compiler diagnostics and runtime output independently.
Original sources are hashed and copied, never rewritten. See the adjacent
upstream-expectations.json for every oracle and all compatibility decisions.

Example:
  python3 research/tools/upstream_pawn.py \
    --source .cache/research/toolchains/pawntest \
    --compiler .cache/research/build32/pawncc \
    --runner .cache/research/build32/pawnrun \
    --include .cache/research/toolchains/pawn-stable/include

Exit 0: all requested cases verified (including intended failures).
Exit 1: unexpected mismatch, timeout, crash, or tool/source-integrity failure.
Exit 2: no unexpected failure, but unsupported, drift, or known-defect cases remain.
A JSON report and raw process logs are always retained once execution starts.
This historic suite's expected data are specific to 32-bit cells; other widths
must have separate, independently sourced portability tests.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time

from toolchains import COMPILER_CONFIG, toolchain_lock, verify_sources, write_json

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / 'research/pawn/upstream-expectations.json'
DIAGNOSTIC = re.compile(r'(?m)^([^\n]*?)\b(fatal error|error|warning)\s+(\d{3}):([^\n]*)')
RUNTIME_ERROR = re.compile(r'Run time error (\d+):')
NUMBER = re.compile(r'(?<![\w])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')
# These original runtime oracles require checked bytecode. Never execute an
# unchecked invalid access simply to see whether this VM happens to trap it.
CHECKED_RUNTIME_ONLY = {3, 55, 60, 84, 85, 115}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(directory: Path, pattern: str = '*') -> dict[str, str]:
    return {str(p.relative_to(directory)): sha256(p)
            for p in sorted(directory.rglob(pattern)) if p.is_file()}


def normalize(text: str) -> str:
    """Normalize presentation only; preserve line count/order and all words."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # amxcons.c's VT100 backend emits SGR colour restoration around print().
    # Remove only these formatting codes, never cursor-motion/control output.
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    text = re.sub(r'\nReturn value: -?\d+\n?\Z', '', text)
    return '\n'.join(re.sub(r'[ \t]+', ' ', line.strip())
                     for line in text.strip().splitlines())


def numeric_equal(actual: str, expected: str, tolerance: float) -> bool:
    a, e = normalize(actual), normalize(expected)
    if NUMBER.sub('<number>', a) != NUMBER.sub('<number>', e):
        return False
    av, ev = NUMBER.findall(a), NUMBER.findall(e)
    return len(av) == len(ev) and all(
        abs(float(x) - float(y)) <= tolerance for x, y in zip(av, ev))


def run_process(command: list[str], cwd: Path, logfile: Path,
                timeout: float, memory_mb: int, env: dict[str, str],
                stdin: str = '') -> dict:
    """Bound all native compiler/VM execution, including malformed input cases."""
    started = time.monotonic()
    output_limit = 16 * 1024 * 1024

    def limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(timeout), math.ceil(timeout) + 1))
        resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (output_limit,) * 2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    timed_out = False
    spawn_error = None
    returncode = 127
    with logfile.open('wb') as output:
        try:
            process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                       stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True, preexec_fn=limits)
            try:
                process.communicate(stdin.encode(), timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
            returncode = process.returncode
        except OSError as error:
            spawn_error = f'{type(error).__name__}: {error}'
            output.write((spawn_error + '\n').encode())
    raw = logfile.read_bytes()
    return {'command': command, 'cwd': str(cwd), 'returncode': returncode,
            'spawn_error': spawn_error,
            'timeout': timed_out, 'elapsed_seconds': round(time.monotonic() - started, 4),
            'log': str(logfile), 'log_sha256': hashlib.sha256(raw).hexdigest(),
            'output_limit_reached': len(raw) >= output_limit,
            'output': raw.decode('utf-8', errors='replace')}


def validate_compile(result: dict, expected: dict, binary: Path) -> list[str]:
    output = result['output']
    diagnostics = [{'kind': 'error' if kind == 'fatal error' else kind,
                    'code': int(code), 'text': prefix + kind + ' ' + code + ':' + message}
                   for prefix, kind, code, message in DIAGNOSTIC.findall(output)]
    result['diagnostics'] = diagnostics
    reasons = process_failures(result)
    actual = Counter((d['kind'], d['code']) for d in diagnostics)
    required = Counter((d['kind'], d['code']) for d in expected['required_diagnostics'])
    for key, count in required.items():
        if actual[key] < count:
            reasons.append(f'missing required {key[0]} {key[1]:03d}: expected at least {count}, found {actual[key]}')
        if expected.get('exact_required_counts') and actual[key] != count:
            reasons.append(f'incorrect multiplicity for {key[0]} {key[1]:03d}')
    for diagnostic in diagnostics:
        if diagnostic['code'] in expected['forbidden_diagnostics']:
            reasons.append(f'forbidden diagnostic {diagnostic["code"]:03d}')
    if expected['exit'] == 'zero':
        if result['returncode'] != 0:
            reasons.append(f'compilation did not succeed (exit {result["returncode"]})')
        if not binary.is_file() or binary.stat().st_size < 32:
            reasons.append('successful compile requires a fresh, nonempty AMX artifact')
    elif result['returncode'] == 0:
        reasons.append('intentionally invalid program unexpectedly compiled successfully')
    # Negative signal exit never counts as the expected compilation failure.
    if expected['extra_errors'] == 'reject':
        for key, count in actual.items():
            if key[0] == 'error' and count > required[key]:
                reasons.append(f'unexpected error {key[1]:03d}')
    if expected.get('extra_warnings') == 'reject':
        for key, count in actual.items():
            if key[0] == 'warning' and count > required[key]:
                reasons.append(f'unexpected warning {key[1]:03d}')
    if expected['exit'] == 'nonzero' and not any(d['kind'] == 'error' for d in diagnostics):
        reasons.append('expected diagnostic failure has no compiler error diagnostic')
    for pattern in expected.get('diagnostic_text', []):
        if not re.search(pattern, output):
            reasons.append(f'required diagnostic location/text absent: {pattern}')
    result['extra_diagnostics'] = [d for d in diagnostics
                                   if (d['kind'], d['code']) not in required]
    return reasons


def process_failures(result: dict) -> list[str]:
    reasons = []
    if result.get('spawn_error'):
        reasons.append('process could not start: ' + result['spawn_error'])
    if result['timeout']:
        reasons.append('process exceeded wall-clock timeout')
    elif result['returncode'] < 0:
        reasons.append(f'process terminated by signal {-result["returncode"]}')
    if result['output_limit_reached']:
        reasons.append('process reached bounded output limit')
    return reasons


def validate_runtime(result: dict, expected: dict) -> tuple[list[str], list[str]]:
    reasons = process_failures(result)
    output = result['output']
    errors = [int(code) for code in RUNTIME_ERROR.findall(output)]
    wanted = expected['error']
    result['runtime_errors'] = errors
    if wanted:
        if errors != [wanted]:
            reasons.append(f'expected exactly runtime error {wanted}, found {errors}')
        if result['returncode'] == 0:
            reasons.append('runtime error did not produce nonzero host exit status')
    else:
        if errors:
            reasons.append(f'unexpected runtime error(s): {errors}')
        if result['returncode'] != 0:
            reasons.append(f'runtime did not exit successfully ({result["returncode"]})')
    if 'source_line' in expected:
        locations = [int(x) for x in re.findall(r'File: [^\n]*, line: (\d+)', output)]
        # Canonical insert_dbgline() stores zero-based lines. pawnrun prints
        # that raw field; pawndbg converts it to a one-based displayed line.
        base = expected.get('reported_line_base', 1)
        wanted_location = expected['source_line'] - (1 - base)
        if locations != [wanted_location]:
            reasons.append(f'expected assertion source line {expected["source_line"]} '
                           f'(runner line {wanted_location}), found {locations}')
    if 'source_file' in expected:
        locations = re.findall(r'File: ([^\n]*), line: \d+', output)
        if locations != [expected['source_file']]:
            reasons.append(f'expected assertion source file {expected["source_file"]}, found {locations}')
    # Error diagnostics and their debug-location trailer belong to the host.
    # Everything printed by the script before the error remains checked.
    script_output = RUNTIME_ERROR.split(output, maxsplit=1)[0] if errors else output
    result['normalized_script_output'] = normalize(script_output)
    expected_output = normalize(expected['stdout'])
    tolerance = expected.get('numeric_absolute_tolerance')
    correct = (numeric_equal(script_output, expected_output, tolerance) if tolerance
               else normalize(script_output) == expected_output)
    defects = []
    if not correct:
        for variant in expected.get('known_variants', []):
            original, replacement = variant['replace']
            if normalize(script_output) == normalize(expected['stdout'].replace(original, replacement)):
                correct = True
                defects.append(variant['reason'])
                result['documented_variant_classification'] = variant.get(
                    'classification', 'known_upstream_defect')
                break
    if not correct:
        reasons.append('runtime output differs from the source-derived oracle')
        result['expected_script_output'] = expected_output
    return reasons, defects


def parse_cases(spec: str, valid: set[int]) -> set[int]:
    if spec == 'all':
        return valid
    selected: set[int] = set()
    for item in spec.split(','):
        limits = item.split('-')
        if len(limits) == 1:
            selected.add(int(item))
        elif len(limits) == 2:
            selected.update(range(int(limits[0]), int(limits[1]) + 1))
        else:
            raise ValueError('case selector must use comma-separated numbers or ranges')
    if not selected or not selected <= valid:
        raise ValueError('case selector contains no cases or unknown case numbers')
    return selected


def compile_command(compiler, step, debug, optimization, include, binary):
    """Authoritative command derivation shared with the evidence validator."""
    dropped = {a['argument'] for a in step.get('adaptations', []) if a['kind'] == 'omit_removed_argument'}
    compile_args = [x for x in step['compile'] if not x.startswith('-d') and x not in dropped]
    if optimization is not None:
        compile_args = [x for x in compile_args if not x.startswith('-O')]
        optimize = [f'-O{optimization}']
    else:
        optimize = [] if any(x.startswith('-O') for x in compile_args) else ['-O2']
    return [str(compiler), *compile_args, f'-T{COMPILER_CONFIG}', '-C32', f'-d{debug}',
            *optimize, f'-i{include}', f'-o{binary}']


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--runner', type=Path, required=True)
    parser.add_argument('--include', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/research/upstream/results.json')
    parser.add_argument('--work', type=Path, default=ROOT / '.cache/research/upstream/runs')
    parser.add_argument('--cases', default='all')
    parser.add_argument('--cells', type=int, choices=[32], default=32)
    parser.add_argument('--profile', choices=['checked', 'release'], default='checked')
    parser.add_argument('--optimization', type=int, choices=[0, 1, 2, 3], default=None,
                        help='Override original -O flags; otherwise retain them, using explicit O2 as default')
    parser.add_argument('--timeout', type=float, default=5.0)
    parser.add_argument('--memory-mb', type=int, default=512)
    parser.add_argument('--fortify', action='store_true',
                        help='Deprecated: self-attestation cannot prove active leak instrumentation')
    args = parser.parse_args()
    for key in ['source', 'compiler', 'runner', 'include', 'manifest', 'output', 'work']:
        setattr(args, key, getattr(args, key).resolve())
    if args.timeout <= 0 or args.memory_mb < 32:
        parser.error('timeout must be positive and memory-mb must be at least32')
    if args.fortify:
        parser.error('FORTIFY is not integrated: a flag cannot prove active leak instrumentation. '
                     'Run without --fortify to retain cases63/97 as explicitly unsupported.')
    verify_sources()
    manifest = json.loads(args.manifest.read_text())
    selected = parse_cases(args.cases, {c['id'] for c in manifest['cases']})
    expected_hashes = manifest['suite']['original_files']
    actual_hashes = tree_hashes(args.source)
    mismatches = [name for name, digest in expected_hashes.items() if actual_hashes.get(name) != digest]
    if mismatches:
        parser.error('original source integrity mismatch: ' + ', '.join(mismatches))
    for path in [args.compiler, args.runner]:
        if not path.is_file() or not os.access(path, os.X_OK):
            parser.error(f'not an executable: {path}')
    if not (args.include / 'default.inc').is_file():
        parser.error('include directory must contain matching canonical default.inc')
    # Prevent user-selected output locations from modifying preserved sources.
    protected = [args.source, args.include]
    for writable in [args.output, args.work]:
        if any(writable == p or p in writable.parents for p in protected):
            parser.error('output/work must be outside original source and include directories')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    workspace = args.work / run_id
    workspace.mkdir(parents=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update({'LC_ALL': 'C', 'AMXLIB': str(args.runner.parent)})
    env['LD_LIBRARY_PATH'] = str(args.runner.parent)
    report = {
        'schema_version': 1, 'generated_utc': run_id,
        'suite': manifest['suite'],
        'inputs': {'config_sha256': sha256(COMPILER_CONFIG), 'include': str(args.include),
                   'source': str(args.source), 'adapter_sha256': sha256(Path(__file__)), 'manifest_sha256': sha256(args.manifest),
                   'compiler': str(args.compiler), 'compiler_sha256': sha256(args.compiler),
                   'runner': str(args.runner), 'runner_sha256': sha256(args.runner),
                   'headers_sha256': tree_hashes(args.include),
                   'optional_libraries_sha256': tree_hashes(args.runner.parent, 'amx*.so*')},
        'profile': {'cell_bits': 32, 'debug': 2 if args.profile == 'checked' else 0,
                    'optimization_override': args.optimization, 'default_optimization': 2,
                    'timeout_seconds': args.timeout, 'memory_mb': args.memory_mb,
                    'fortify_attested': args.fortify,
                    'environment': {k: env[k] for k in ['LC_ALL', 'AMXLIB', 'LD_LIBRARY_PATH']}},
        'workspace': str(workspace), 'results': [],
    }
    for case in manifest['cases']:
        if case['id'] not in selected:
            continue
        result = {'id': case['id'], 'provenance': case['provenance'],
                  'notes': case['notes'], 'steps': [], 'reasons': [], 'limitations': []}
        if case['fixture_issue']:
            result['limitations'].append(case['fixture_issue'])
        if 'fortify' in case['requires'] and not args.fortify:
            result['limitations'].append('Compiler FORTIFY leak oracle is not instrumented/attested')
        defects = []
        oracle_drifts = []
        for index, step in enumerate(case['steps'], 1):
            directory = workspace / f'case{case["id"]:03d}-{index}'
            directory.mkdir()
            for name in expected_hashes:
                target = directory / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(args.source / name, target)
            binary = directory / 'result.amx'
            original = step['compile']
            adaptations = step.get('adaptations', [])
            command = compile_command(args.compiler, step, 2 if args.profile == 'checked' else 0,
                                      args.optimization, args.include, binary)
            compile_result = run_process(command, directory, directory / 'compile.log',
                                         args.timeout, args.memory_mb, env)
            issues = validate_compile(compile_result, step['expect'], binary)
            original_issues = list(issues)
            accepted_difference = None
            if issues:
                for variant in step.get('documented_compile_variants', []):
                    # The old oracle remains visible and unfulfilled. A
                    # version-specific alternative has its own strict checks.
                    if (re.search(variant['banner_pattern'], compile_result['output'])
                            and not validate_compile(compile_result, variant['expect'], binary)):
                        issues = []
                        accepted_difference = variant['reason']
                        oracle_drifts.append(variant['reason'])
                        break
            if issues:
                for defect in step.get('known_compile_defects', []):
                    # A compiler crash is never an expected diagnostic failure.
                    # Recognize only a separately minimized, bounded signature;
                    # it stays a defect and prevents all_requested_verified.
                    if (not compile_result['timeout']
                            and not compile_result['output_limit_reached']
                            and compile_result['returncode'] == defect['returncode']
                            and re.search(defect['banner_pattern'], compile_result['output'])
                            and re.search(defect['output_pattern'], compile_result['output'])):
                        issues = []
                        accepted_difference = defect['reason']
                        defects.append(defect['reason'])
                        break
            unsupported = step.get('unsupported_configuration')
            if unsupported:
                # A removed option is a compatibility result, not a passing
                # language test. Require the precise CLI rejection, so a crash
                # or unrelated failure cannot be concealed as unsupported.
                if (compile_result['returncode'] == unsupported['exit']
                        and not process_failures(compile_result)
                        and re.search(unsupported['output_pattern'], compile_result['output'])
                        and not binary.exists()):
                    issues = []
                    result['limitations'].append(unsupported['reason'])
            step_result = {'original_argv': original, 'compile': compile_result,
                           'adaptations': adaptations,
                           'compile_checks': {'passed': not issues, 'reasons': issues,
                                              'original_oracle_passed': not original_issues,
                                              'original_oracle_reasons': original_issues,
                                              'documented_difference': accepted_difference}}
            if binary.is_file():
                step_result['amx_sha256'] = sha256(binary)
            result['steps'].append(step_result)
            result['reasons'].extend(issues)
            if args.fortify and 'fortify' in case['requires']:
                fortify_files = [p for p in directory.iterdir()
                                 if p.is_file() and p.suffix.lower() in ['.log', '.mem']
                                 and p.name != 'compile.log' and p.stat().st_size]
                if fortify_files or re.search(r'memory leak|memory leakage|unfreed|leaked',
                                              compile_result['output'], re.I):
                    result['reasons'].append('FORTIFY/memory leakage report is present')
            if 'run' not in step or issues:
                continue
            if args.profile == 'release' and case['id'] in CHECKED_RUNTIME_ONLY:
                result['limitations'].append('Runtime intentionally excluded in d0: original oracle requires bounds/assert checks')
                continue
            runtime_result = run_process([str(args.runner), str(binary)], directory,
                                         directory / 'runtime.log', args.timeout,
                                         args.memory_mb, env, step['stdin'])
            runtime_issues, runtime_defects = validate_runtime(runtime_result, step['runtime_expect'])
            runtime_drifts = []
            if runtime_result.get('documented_variant_classification') == 'documented_oracle_drift':
                runtime_drifts, runtime_defects = runtime_defects, []
            step_result['runtime'] = runtime_result
            step_result['runtime_checks'] = {'passed': not runtime_issues,
                                             'reasons': runtime_issues, 'known_defects': runtime_defects,
                                             'oracle_drifts': runtime_drifts}
            result['reasons'].extend(runtime_issues)
            defects.extend(runtime_defects)
            oracle_drifts.extend(runtime_drifts)
        if result['reasons']:
            result['status'] = 'unexpected_failure'
        elif result['limitations']:
            result['status'] = 'unsupported_harness'
        elif defects:
            result['status'] = 'known_upstream_defect'
            result['known_defects'] = defects
        elif oracle_drifts:
            result['status'] = 'documented_oracle_drift'
            result['oracle_drifts'] = oracle_drifts
        elif any(s['expect']['exit'] == 'nonzero' or s.get('runtime_expect', {}).get('error', 0)
                 for s in case['steps']):
            result['status'] = 'expected_failure'
        else:
            result['status'] = 'verified'
        report['results'].append(result)
        print(f'{case["id"]:03d} {result["status"]}'
              + (': ' + '; '.join(result['reasons']) if result['reasons'] else ''), flush=True)
        report['summary'] = dict(Counter(r['status'] for r in report['results']))
        report['complete'] = False
        write_json(args.output, report)
    report['complete'] = len(report['results']) == len(selected)
    report['source_integrity_after'] = tree_hashes(args.source) == actual_hashes
    report['toolchain_integrity_after'] = (
        sha256(COMPILER_CONFIG) == report['inputs']['config_sha256']
        and sha256(Path(__file__)) == report['inputs']['adapter_sha256']
        and sha256(args.manifest) == report['inputs']['manifest_sha256']
        and args.compiler.is_file() and args.runner.is_file()
        and sha256(args.compiler) == report['inputs']['compiler_sha256']
        and sha256(args.runner) == report['inputs']['runner_sha256']
        and tree_hashes(args.include) == report['inputs']['headers_sha256']
        and tree_hashes(args.runner.parent, 'amx*.so*')
            == report['inputs']['optional_libraries_sha256'])
    report['all_requested_verified'] = (report['complete'] and report['source_integrity_after']
                                       and report['toolchain_integrity_after']
                                       and all(r['status'] in ['verified', 'expected_failure']
                                               for r in report['results']))
    write_json(args.output, report)
    print(json.dumps({'summary': report['summary'], 'report': str(args.output),
                      'all_requested_verified': report['all_requested_verified']}))
    if (not report['source_integrity_after'] or not report['toolchain_integrity_after']
            or report['summary'].get('unexpected_failure')):
        return 1
    return 0 if report['all_requested_verified'] else 2


if __name__ == '__main__':
    with toolchain_lock():
        sys.exit(main())

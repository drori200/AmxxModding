#!/usr/bin/env python3
"""Negative controls for the PAWN research instruments, not language coverage.

Synthetic result mutations test rejection logic; the compiler configuration
control executes an unchanged copy of the official compiler in a private folder.
"""
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile

import pawn_examples
import pawn_gate
import pawn_lab
import toolchains
from toolchains import ROOT, CACHE, EVIDENCE, COMPILER_CONFIG, CANONICAL_COMPILER, digest, write_json


def process(output='', rc=0):
    return {'output': output, 'returncode': rc, 'timeout': False, 'output_limit_reached': False}


class InstrumentControls(unittest.TestCase):
    def test_expected_diagnostic_is_not_a_crash(self):
        case = {'compile_fails': True, 'diagnostics': [17]}
        good = process('test.p(1) : error 017: undefined symbol\n', 1)
        self.assertEqual(pawn_lab.validate_compile(good, case, 2), [])
        for code in (-6, -11, 0):
            bad = dict(good, returncode=code)
            self.assertTrue(pawn_lab.validate_compile(bad, case, 2))

    def test_warning_only_cannot_satisfy_error(self):
        self.assertTrue(pawn_lab.validate_compile(process('warning 017: sample\n', 1),
                                                 {'compile_fails': True, 'diagnostics': [17]}, 2))

    def test_runtime_error_must_be_from_execution(self):
        footer = 'lab: bits=32 checks=0 failures=0 result=0 error=4 sleeps=0\n'
        good = process(footer + 'phase: init=0 register=0 exec_entered=1 stage=exec\n', 2)
        case = {'checks': 0, 'error': 4}
        self.assertEqual(pawn_lab.validate_runtime(good, case, 32, 2), [])
        for phase in ('phase: init=4 register=-1 exec_entered=0 stage=init\n',
                      'phase: init=0 register=4 exec_entered=0 stage=register\n', ''):
            self.assertTrue(pawn_lab.validate_runtime(process(footer + phase, 2), case, 32, 2))

    def test_duplicate_footer_wrong_result_and_timeout_rejected(self):
        output = 'lab: bits=32 checks=1 failures=0 result=42 error=0 sleeps=0\nphase: init=0 register=0 exec_entered=1 stage=exec\n'
        good = process(output)
        case = {'checks': 1, 'result': 42}
        self.assertEqual(pawn_lab.validate_runtime(good, case, 32, 2), [])
        for bad in (dict(good, output=output + output), dict(good, timeout=True),
                    dict(good, output=output.replace('result=42', 'result=41')),
                    dict(good, output_limit_reached=True)):
            self.assertTrue(pawn_lab.validate_runtime(bad, case, 32, 2))

    def test_invalid_memory_and_duplicate_selection(self):
        valid = {'cases': [{'id': 'x', 'widths': [32], 'hazard': 'invalid-memory', 'checked_only': True}]}
        self.assertEqual(len(pawn_lab.selected_profiles(valid)), 8)
        with self.assertRaises(ValueError):
            pawn_lab.selected_profiles({'cases': [dict(valid['cases'][0], checked_only=False)]})
        with self.assertRaises(ValueError):
            pawn_lab.selected_profiles({'cases': valid['cases'] * 2})
        with self.assertRaises(ValueError):
            pawn_lab.selected_profiles({'cases': [{'id': 'x', 'widths': [32, 32]}]})

    def test_raw_log_is_bound_to_observation(self):
        with tempfile.TemporaryDirectory(dir=CACHE) as folder:
            path = Path(folder) / 'process.txt'
            path.write_text('correct\n')
            result = dict(process('correct\n'), output_path=str(path), output_sha256=digest(path))
            self.assertEqual(pawn_lab.process_errors(result, True), [])
            path.write_text('different\n')
            self.assertTrue(pawn_lab.process_errors(result, True))

    def test_archive_extra_and_changed_file_are_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory(dir=CACHE) as folder:
            folder = Path(folder)
            archive = folder / 'source.zip'
            with zipfile.ZipFile(archive, 'w') as out:
                out.writestr('compiler/test.c', 'official fixture bytes')
            tree = folder / 'source'
            self.assertTrue(toolchains.zip_tree(archive, tree, True)['matches_archive'])
            source = tree / 'compiler/test.c'
            source.write_text('modified')
            with self.assertRaises(RuntimeError):
                toolchains.zip_tree(archive, tree, True)
            self.assertEqual(source.read_text(), 'modified')
            source.write_text('official fixture bytes')
            (tree / 'extra.c').write_text('extra')
            with self.assertRaises(RuntimeError):
                toolchains.zip_tree(archive, tree)

    def test_source_manifest_cannot_substitute_a_fork(self):
        sources = json.loads((EVIDENCE / 'sources.json').read_text())
        sources[0]['url'] = 'https://example.invalid/project-fork.zip'
        with patch.object(toolchains.json, 'loads', return_value=sources):
            with self.assertRaisesRegex(RuntimeError, 'official CompuPhase'):
                toolchains.verify_sources()

    def test_archive_path_cannot_redirect_source_verification(self):
        sources = json.loads((EVIDENCE / 'sources.json').read_text())
        sources[0]['path'] = '.cache/research/downloads/alternate.zip'
        with patch.object(toolchains.json, 'loads', return_value=sources):
            with self.assertRaisesRegex(RuntimeError, 'canonical cache path'):
                toolchains.verify_sources()

    def test_setup_lock_excludes_build_while_test_holds_read_lock(self):
        with tempfile.TemporaryDirectory(dir=CACHE) as folder:
            with patch.object(toolchains, 'CACHE', Path(folder)):
                with toolchains.toolchain_lock():
                    with self.assertRaisesRegex(RuntimeError, 'in use'):
                        with toolchains.toolchain_lock(exclusive=True):
                            self.fail('exclusive lock obtained during test')
                with toolchains.toolchain_lock(exclusive=True):
                    pass

    def test_amxx_guard_cannot_validate_during_exclusive_setup(self):
        with tempfile.TemporaryDirectory(dir=CACHE) as folder:
            with patch.object(toolchains, 'CACHE', Path(folder)):
                with toolchains.toolchain_lock(exclusive=True):
                    with self.assertRaisesRegex(SystemExit, 'AMXX phase locked.*in use'):
                        pawn_gate.require_current_pass()

    def test_explicit_config_ignores_ambient_compiler_config(self):
        with tempfile.TemporaryDirectory(dir=CACHE) as folder:
            folder = Path(folder)
            cc = folder / 'pawncc'
            shutil.copy2(CANONICAL_COMPILER, cc)
            self.assertEqual(digest(cc), digest(CANONICAL_COMPILER))
            (folder / 'pawn.cfg').write_text('UNEXPECTED=1\n')
            source = folder / 'config_probe.p'
            source.write_text('#if defined UNEXPECTED\n#error ambient configuration was read\n#endif\nmain() { return 42; }\n')
            args = [cc, source, '-p', '-C32', '-d2', '-O0', f'-o{folder / "test.amx"}']
            ambient = pawn_lab.execute(args, folder / 'ambient')
            explicit = pawn_lab.execute([*args, f'-T{COMPILER_CONFIG}'], folder / 'explicit')
            self.assertGreater(ambient['returncode'], 0, ambient['output'])
            self.assertIn('ambient configuration was read', ambient['output'])
            self.assertEqual(explicit['returncode'], 0, explicit['output'])

    def test_exercise_prediction_and_timeout_are_not_pass_flags(self):
        result = {'exercise': 1, 'debug': 0, 'optimization': 0,
                  'compile': process(), 'runtime': process('expected'),
                  'expected_output': 'expected', 'expected_diagnostics': [], 'passed': True}
        self.assertEqual(pawn_examples.exercise_errors(result, 'expected'), [])
        self.assertTrue(pawn_examples.exercise_errors(result, 'different'))
        result['runtime']['timeout'] = True
        self.assertTrue(pawn_examples.exercise_errors(result, 'expected'))

    def test_examples_duplicate_matrix_and_stale_inputs_rejected(self):
        # Empty process data is intentionally invalid too. Assert the separate
        # matrix/freshness failures, so a different failure cannot satisfy this control.
        records = [{'exercise': 1, 'debug': 0, 'optimization': 0, 'compile': process()}] * 40
        report = {'audit': [], 'exercises': records, 'inputs_before': {}, 'inputs_unchanged': True}
        reasons = pawn_examples.validate_report(report, False)
        self.assertIn('independent exercises must cover exactly 40 unique selected profiles', reasons)
        self.assertIn('prior/example inputs, predictions or toolchain changed since run', reasons)

    def test_malformed_gate_evidence_returns_fail(self):
        with patch.object(pawn_gate, 'evaluate_unchecked', side_effect=TypeError('invalid schema')):
            self.assertEqual(pawn_gate.evaluate()['status'], 'FAIL')

    def test_recorded_pass_cannot_override_failing_current_gate(self):
        with tempfile.TemporaryDirectory(dir=CACHE) as folder:
            gate = Path(folder) / 'gate.json'
            gate.write_text('{"status":"PASS","input_hashes":{}}')
            with patch.object(pawn_gate, 'GATE', gate), patch.object(pawn_gate, 'evaluate', return_value={'status': 'FAIL', 'input_hashes': {}}):
                with self.assertRaisesRegex(SystemExit, 'AMXX phase locked'):
                    pawn_gate.require_current_pass()


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(InstrumentControls)
    started = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue())
    report = {'purpose': 'Research instrument acceptance/rejection controls; not language proficiency evidence',
              'harness_sha256': digest(__file__), 'actual_inputs': toolchains.runtime_inputs(),
              'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'passed': result.wasSuccessful(), 'seconds': time.monotonic() - started, 'log': stream.getvalue()}
    write_json(EVIDENCE / 'pawn-audit-controls.json', report)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())

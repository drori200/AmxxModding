#!/usr/bin/env python3
"""Compare selected compiler-internal widths while holding emitted cells fixed.

The canonical compiler defaults its internal cell type to 64 bits (sc.h:43-45).
That type is distinct from -C, the emitted bytecode cell width. This comparison
checks whether the lab's explicit narrower internal types caused retained errors.
It never changes a production compiler or substitutes a patched compiler.
"""
import json
import time
from pathlib import Path
from toolchains import ROOT, CACHE, EVIDENCE, digest, runtime_inputs, toolchain_lock, verify_sources, write_json
from pawn_lab import compile_command, execute, validate_compile, validate_runtime


def main():
    verify_sources()
    before = runtime_inputs()
    work = CACHE / 'compiler-config-audit' / str(time.time_ns())
    manifest = json.loads((ROOT / 'research/pawn/cases.json').read_text())
    cases = {c['id']: c for c in manifest['cases']}
    selected = [('signed_arithmetic', 16, 0), ('strings', 16, 0), ('evaluation', 16, 0),
                ('boundaries', 32, 3), ('signed_arithmetic', 32, 0), ('minimal', 16, 0)]
    results = []
    for name, emitted_bits, opt in selected:
        for internal_bits in (emitted_bits, 64):
            directory = work / f'{name}-internal{internal_bits}-C{emitted_bits}-O{opt}'
            directory.mkdir(parents=True)
            amx = directory / 'program.amx'
            command = compile_command(cases[name], emitted_bits, 2, opt, amx)
            command[0] = str(CACHE / f'build{internal_bits}/pawncc')
            compiled = execute(command, directory / 'compile')
            errors = validate_compile(compiled, cases[name], 2, True)
            record = {'case': name, 'compiler_internal_cell_bits': internal_bits, 'emitted_cell_bits': emitted_bits,
                      'vm_cell_bits': emitted_bits, 'debug': 2, 'optimization': opt,
                      'source_sha256': digest(ROOT / f'research/pawn/cases/{name}.p'),
                      'compiler_sha256': digest(command[0]), 'compile': compiled, 'compile_errors': errors}
            if not errors and amx.is_file():
                record['bytecode_sha256'] = digest(amx)
                record['runtime'] = execute([CACHE / f'build{emitted_bits}/labrun', amx], directory / 'runtime')
                record['runtime_errors'] = validate_runtime(record['runtime'], cases[name], emitted_bits, 2, True)
            results.append(record)
            print(name, f'internal{internal_bits}/C{emitted_bits}', 'compile:', compiled['returncode'],
                  'runtime:', record.get('runtime', {}).get('returncode'), record.get('runtime_errors', []))
    report = {'purpose': __doc__, 'inputs_before': before, 'inputs_unchanged': before == runtime_inputs(),
              'compiler_default_source': 'pawn-stable.zip:compiler/sc.h:43-45', 'results': results}
    write_json(work / 'results.json', report)
    write_json(EVIDENCE / 'pawn-compiler-config-comparison.json', report)


if __name__ == '__main__':
    with toolchain_lock():
        main()

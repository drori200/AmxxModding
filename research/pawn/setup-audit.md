# PAWN compiler and gate audit

The PAWN research compiler comes from CompuPhase's official source release. The
advancement gate still **fails**. Compiler provenance, correctness of a test
instrument, and proficiency across the guide inventory are separate obligations.

## Official compiler origin

The [CompuPhase release page](https://www.compuphase.com/pawn/pawn.htm) links the
[4.1.7487 source archive](https://www.compuphase.com/pawn/pawn-4.1.7487.zip). A fresh
HTTPS download on 2026-09-10 matched SHA-256
`05cf630baef59912a9ffaf2745652187038d8d5be1a3aab870d13ea0bd31c7bc`.
All **164 extracted files** match its bytes; no compiler source patch is applied.
The hash is a locally recorded fingerprint, not an upstream signature.

The archive's `compiler/svnrev.h` and compiled banner identify **4.1.7483**.
The advertised archive version and actual revision remain distinct. This audit
does not invent a reason for CompuPhase's inconsistent labels. The separately
pinned official development snapshot is retained with its build failure.

See [fresh download and binary evidence](../evidence/pawn-compiler-origin-recheck.json),
[all pinned source checks](../evidence/pawn-official-provenance.json), and
[toolchain manifest](../evidence/toolchains.json). The prior task's SA:MP-oriented
compiler is preserved as historical material. It is not selected for this gate.
The test host is custom C code linked to the official VM; it is identified as a
test instrument. Locally repaired VM experiments are separately labeled and do
not replace the canonical compiler or baseline VM.

## Compiler configuration correction

`compiler/sc.h:43-45` defaults the compiler's internal maximum cell type to
**64 bits**. The command-line `-C16`, `-C32` or `-C64` independently selects the
emitted bytecode width. A matching VM must use that emitted width.

The first setup unnecessarily narrowed the compiler's internal type alongside
the VM. A controlled comparison held source, emitted cell width, optimization
and VM constant while changing only that compiler build. The 32-bit boundary
fixture's optimizer assertion disappeared with the upstream default internal
type. That failure cannot be attributed to the default canonical compiler.
The selected 16-bit signed-arithmetic, string and comparison failures persisted.

The corrected baseline uses `.cache/research/build64/pawncc` for all three output
widths, with explicit `-C` and a matching `labrun` or `pawnrun`. Internal 16/32-bit
compiler builds remain configuration experiments. The original reports and
manifest are preserved as `pawn-pre-default-compiler-*.json`.
[Comparison commands and results](../evidence/pawn-compiler-config-comparison.json)
can be reproduced with `python3 -B research/tools/pawn_compiler_config.py`.

## Mistakes found in the lab and corrections

| Finding | Correction and evidence |
| --- | --- |
| State fixture used `@entry`, which declared an ordinary public function | Use canonical `entry()` state callbacks. Preserve the original fixture in `pawn-setup-audit-initial.json`. |
| Constant-group fixture omitted the tag colon and applied `sizeof` to a constant | Use `const Mode:` and remove the invalid expression. These were fixture errors. |
| Whole-string assignment to a symbolic field conflicted with this compiler | Retain the guide/compiler disagreement as `defects/symbolic_string_assignment.p`; the positive field fixture uses explicit character stores. |
| A compiler crash after an expected diagnostic could pass a negative test | Reject signal exits and require a normal nonzero exit with an error diagnostic. |
| VM initialization and execution shared one undifferentiated error field | Emit and require successful initialization/registration plus execution entry before accepting an expected runtime error. |
| Host array/string pointers could be inspected after an allocation helper failed | Guard their use with the returned error code. |
| Ambient compiler defaults could alter profiles | Every current primary harness explicitly supplies the versioned empty `empty.cfg`. An actual compiler control tests a poisoned ambient `pawn.cfg`. |
| Manifests and summary flags were trusted too broadly | Recheck actual sources, tools, headers, libraries, commands, raw logs, bytecode, profile identities and independent predictions. Recompute test oracles. |
| Download extraction overwrote prior source edits | Compare all extracted bytes with the archive and reject changes or extras without overwriting them. Bind identities to canonical cache paths. |
| Concurrent setup could replace tools under tests or advancement checks | Use shared test/guard locks and an exclusive setup lock; overlapping operations fail before mutation. |
| Repeated runs overwrote logs | Use a distinct directory for each run and retain raw output hashes. Evidence updates are atomic. |
| Gate log comparison translated CRLF from an upstream console test | Compare decoded raw bytes for that adapter; preserve its original output representation. |

The instrument controls include synthetic deliberately corrupted observations.
They test rejection logic, not PAWN semantics. Separate real compiler and runtime
runs supply language evidence. [Control results](../evidence/pawn-audit-controls.json)
and the [test source](../tools/test_pawn_audit.py) identify the exact scope.

## What is still unresolved

The original matrix retains failing portability profiles and compiler/VM defects.
Each requires a bounded explanation and independent disposition. Recognition of
one defect does not explain every failure. The official suite retains documented
oracle differences, unsupported harness facilities and a compiler defect; none
are silently recast as successful language tests.

All **86 guide-topic dispositions** remain to be completed and reviewed. Many
have mapped executable cases, but a mapping does not establish full topic
coverage. The gate also requires a current independent advancement review and
resolution of consequential questions needed by the AMXX phase. The current
[gate record](../evidence/pawn-gate.json) is the authoritative decision.

AMXX research and server execution remain locked. The prior production build
check verified 50 plugins; this audit changes research tooling and ignore rules.
No runtime validation of production plugins is claimed.

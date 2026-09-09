# Corrections to the prior PAWN material

The earlier task and its original artifacts remain preserved in place. The
[artifact manifest](prior/original-artifacts.json) identifies their paths and
hashes; [47 extracted snippets](prior/prior-examples-audit.json) preserve source
text and explicit audit wrappers. Only one extracted snippet is a standalone
complete program. The others are fragments, even when a wrapper makes them
executable. A fragment's missing context is not automatically a language error.

The preserved compiler is the community `pawn-lang/compiler` fork at commit
`134ad7a836c581546665340aedb59efd4636e269`, whose README targets SA:MP and whose
CMake metadata reports 3.10.10. Its older documentation is dated February 2006.
It does not establish behavior of CompuPhase 4.1.7483. No durable custom canonical
execution corpus was located in the inspected prior workspace; this does not
prove that no transient execution ever occurred.

## Consequential corrections

| Prior teaching claim or example | Correction for the pinned canonical baseline | Executable evidence |
| --- | --- | --- |
| “Modulo stays positive” | Division floors; a nonzero remainder follows the divisor's sign. The old wording omits negative divisors. | [signed_arithmetic.p](cases/signed_arithmetic.p) |
| Assertion followed only by an upper-bound check | Release-safe validation must reject both negative indexes and indexes at or above the count before access. | [release_safe_index.p](cases/release_safe_index.p) |
| Untagged `operator+` expected to return `Fixed:` | Parameter tags do not declare the result tag. Declare `Fixed:operator+` explicitly. | [operator_tag.p](cases/operator_tag.p), prior warning-213 audit |
| Brace initializer used as a cell array | Canonical braces select packed characters. Square brackets select cell elements. Some August 2025 guide examples still use the older form. | [array_aliasing.p](cases/array_aliasing.p), prior short slide 11 |
| Double-quoted string indexed as unpacked cells | Double quotes produce packed strings; use character indexing or explicitly unpacked literals. The retained literal files avoid ambiguous PDF quote typography. | [strings.p](cases/strings.p) |
| `enum` record layout and `N char` sizing | Those prior forms are not accepted by this canonical compiler. Canonical symbolic fields and character-sized declarations need their own replacement examples. | Preserved negative audit; replacement coverage is still pending |
| `state:` used as a tag | `state` is reserved. Use a nonreserved tag name. | Preserved short-slide-16 negative audit |
| Reverse argument evaluation treated as a guarantee | The Language Guide leaves argument evaluation order undefined. Explicitly sequence dependent side effects. | [evaluation.p](cases/evaluation.p), independent exercise 5 |

For 7 and −7 divided by 3 and −3, the expected `(quotient, remainder)` pairs are
`(2,1)`, `(-3,2)`, `(-3,-2)`, and `(2,-1)` respectively. The August 2025
[Language Guide, pp. 89–90](https://codeberg.org/compuphase/pawn/raw/commit/73b9ae62319c213936f179345addf1fc9ac728f1/doc/Pawn_Language_Guide.pdf)
explicitly states the divisor-sign rule. The misleading positive-only wording is
in the older guide and slides, not that current passage.

The array discrepancy is observable, not cosmetic. In the old short slide 11,
the bytes 10, 20, 30, and 40 form the packed 32-bit cell `0x0a141e28`. Adding five
to each *cell* therefore does not produce the intended four updated scores.
The corrected examples use `[10, 20, 30, 40]` when four cell elements are intended.

Tags are compile-time classifications rather than runtime object types. Casts
can suppress a tag mismatch without converting the stored numeric value. A clean
compile after adding a cast therefore does not prove an intended conversion.
The explicit arithmetic and conversion operators in the independent exercises
test results as well as diagnostics.

## What the replacement evidence establishes

The original suite separates compile-time diagnostics, executed assertions,
runtime errors, and release-safe guards. Five independently designed exercises
combine arithmetic, aliasing, strings, operators, state transitions, macro
expansion, short-circuit logic, and recursion. Their expected outputs were retained
before the current rerun. Earlier wrapper errors and non-triggering defect probes
remain visible.

This audit does not retroactively validate every sentence of the earlier decks.
The [86-topic inventory](coverage-inventory.json) identifies the remaining
obligations. Complete corrected examples linked here have executable files;
incomplete replacements are explicitly identified instead of presented as verified
teaching material.

# Canonical toolchain provenance

The [official release page](https://www.compuphase.com/pawn/pawn.htm) advertised
4.1.7487 when accessed on 2026-09-08. The downloaded
[archive](https://www.compuphase.com/pawn/pawn-4.1.7487.zip) has SHA-256
`05cf630baef59912a9ffaf2745652187038d8d5be1a3aab870d13ea0bd31c7bc`.
Its `compiler/svnrev.h` identifies revision 7483 dated 2025-08-20, and the
compiled program prints `Pawn compiler 4.1.7483`. The filename is not a reliable
compiler-version oracle. Both identities are retained in the manifest.

The reference uses August 2025 editions of the
[Language Guide](https://codeberg.org/compuphase/pawn/raw/commit/73b9ae62319c213936f179345addf1fc9ac728f1/doc/Pawn_Language_Guide.pdf)
and [Implementer's Guide](https://codeberg.org/compuphase/pawn/raw/commit/73b9ae62319c213936f179345addf1fc9ac728f1/doc/Pawn_Implementer_Guide.pdf).
Their commit and PDF hashes are pinned in [sources.json](../evidence/sources.json).
They are contemporary documentation, not proof that every example matches the
archive byte for byte. In particular, some array examples retain older syntax.

## Configurations actually built

The compiler's internal maximum cell type and its bytecode target are separate.
`compiler/sc.h:43-45` defaults the internal type to 64 bits. The selected canonical
compiler is now `.cache/research/build64/pawncc`, preserving that default; explicit
`-C16`, `-C32` or `-C64` selects output for the matching VM. The earlier internal
16/32-bit compiler builds remain configuration experiments. A 32-bit optimizer
failure disappeared with the default internal type, so it is not a defect claim
against the default compiler. See the [setup audit](setup-audit.md) and
[controlled comparison](../evidence/pawn-compiler-config-comparison.json).

| Configuration | Compiler target | VM | Scope |
| --- | --- | --- | --- |
| Baseline | `-C32` | 32-bit cells, portable C interpreter | Original and official regression cases |
| Portability | `-C64` | 64-bit cells, portable C interpreter | Original cases and bounded defect probes |
| Minimal | `-C16` | 16-bit cells, minimal C host | Supported pure-language cases and bounded defect probes |

These are cell widths on an x86-64 Linux host. They do not establish execution
on a 16-bit processor, a 32-bit operating system, a big-endian target, an assembly
interpreter, or a JIT. The minimal host disables dynamic loading and code
relocation. Canonical `pawnrun` separately supplies core/console facilities and
loads optional modules for the official suite. The manifests record exact
compiler flags, banners, headers, source trees, and executable hashes.

`-d0` removes runtime checking; `-d1` enables checking without symbolic metadata;
`-d2` supplies symbolic metadata and checking. Original tests exercise optimization
levels 0–3 at 32-bit cells and selected matching portability profiles. A profile
is not certified merely because it was built: several have retained failures.

## Build issues and explicit adjustments

1. GCC 16.2.1 defaults to a language mode where `constexpr` is reserved. The
   archive uses that word as a C function name. Explicit C99 builds it without
   changing upstream source.
2. Curses-based console emulation changed the captured output into a bounded
   terminal image. `HAVE_CURSES_H=0` selects the stream console for reproducible
   stdout checks. Earlier affected logs remain historical observations.
3. Upstream CMake omits `linux/getch.c` from the non-curses `amxString` library,
   leaving unresolved symbols. Provisioning links that module from the original
   sources plus `getch.c`; the exact command and resulting hash are recorded.
4. Dyncall is unavailable in this configuration. Foreign-call functionality is
   not inferred from the presence of a Process module binary.

The separate official development snapshot
[79620fcfff474c622fdb11d78027598235b8f11f](https://codeberg.org/compuphase/pawn/commit/79620fcfff474c622fdb11d78027598235b8f11f)
fails to compile in `compiler/sc1.c`, where `dostate` references an undeclared
`name`. Its failed build is recorded separately. It has not replaced the baseline,
and no execution comparison with that unbuilt compiler is claimed.

## Portability defects

The default portable interpreter uses fixed-width stores in several cell
instructions. The retained [differential probes](../evidence/pawn-defect-probes.json)
show 16-bit fill/swap corruption and loss of high bits in a 64-bit fill. A local
diagnostic VM replaces five affected cell stores with cell-width stores; the
same three bytecode fixtures then pass. The unmodified archive remains intact.
This is a bounded causal experiment, not a generally validated replacement VM.

Optimization-level-3 compiler failures and packed-immediate errors are separate
issues that must identify both compiler-internal and emitted cell widths. Earlier
32-bit-internal failures do not establish failures under the default 64-bit-internal compiler. Tests and logs retain both triggering and non-triggering probes. Neither
the language's nominal width support nor the compiler's option list is proof of
working portability across all configurations.

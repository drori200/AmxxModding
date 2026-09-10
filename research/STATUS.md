# Resumable checkpoint — 2026-09-10

## Objective and current milestone

Implement the complete PAWN-first research plan: audit prior claims, validate the
official canonical toolchain and gate, complete the versioned PAWN reference and
executable coverage, then only after advancement research and test AMXX/ReAPI and
community integrations in an isolated lab and local server. Deliver durable sources,
logs, a claim/source/test ledger, and a cited, visually verified PDF while preserving
production behavior. After the user verifies that product, build and evaluate the
CS 1.6 coding agent on unseen tasks. The full approved instructions, including
usage thresholds and mandatory commit/push checkpoints, are in [OBJECTIVE.md](OBJECTIVE.md).

Current milestone: checkpoint the PAWN foundation audit and compiler-selection
correction. **The PAWN advancement gate remains FAIL; AMXX research is locked.**

## Verified changes and evidence

- Fresh download from the official CompuPhase HTTPS endpoint matched the pinned
  SHA-256; all 164 extracted source files match the archive. See
  [origin recheck](evidence/pawn-compiler-origin-recheck.json) and
  [source verification](evidence/pawn-official-provenance.json).
- Archive advertised as 4.1.7487; actual revision/banner 4.1.7483. The discrepancy
  remains explicit. No fork or patched compiler is selected.
- Canonical compiler selection is `.cache/research/build64/pawncc`, preserving
  the compiler's default internal 64-bit type. `-C16/-C32/-C64` determines emitted
  cells, with a VM built for that emitted width. Earlier internal-16/32 compiler
  configurations and full reports are preserved separately. The controlled
  [configuration comparison](evidence/pawn-compiler-config-comparison.json)
  resolves the earlier 32-bit boundary optimizer failure under the default type.
- Fixture corrections and test-harness acceptance/freshness fixes are documented
  in [setup-audit.md](pawn/setup-audit.md). The 16 instrument controls passed.
- Original suite: **508/542 profiles match their explicit expectations**:
  49/58 at C16, 364/364 at C32, 95/120 at C64. Failures are retained.
- Prior examples: 47 audited snippets (1 standalone, 46 wrapped fragments),
  38 compile and 9 fail compilation. All **40 independent exercise profiles** pass.
- Official regression suite: all 161 cases processed; 105 verified,
  51 expected failures, 2 documented oracle differences and 3 unsupported harness
  cases. No unexpected mismatch; exceptions still require reviewed dispositions.
- Production check from the preceding milestone verified 26 project and 24 kit
  plugins. No production or isolated-server runtime success is claimed.

The authoritative latest results are in `research/evidence/pawn-*-results.json`,
with exact commands and retained process output. Original source archives and
build outputs remain in ignored `.cache/research/`. Regeneration instructions are
in [README.md](README.md). A fresh checkout must regenerate cache artifacts before
its gate can pass; historical JSON alone is insufficient.

## Open requirements and next action

1. The independent foundation review completed: no consequential flaw was found
   in the compiler-selection and guard-lock corrections. Its bounded scope and
   reviewed hashes are in `pawn-foundation-checkpoint-review.json`. The comparison
   was refreshed after its historical snapshot warning. This is not advancement
   approval. No review agent needs to be resumed for this completed assignment.
2. Investigate the **34 remaining original portability failures** with bounded
   reproducers and source/bytecode evidence. Do not attribute all failures to the
   known five VM stores without a causal comparison.
3. Review official-suite exceptions 29, 61, 63, 71 and 97. The gate has no generic
   waiver for them; implement only precise, reviewed dispositions where justified.
4. Complete evidence dispositions for all **86 guide topics**, close consequential
   PAWN questions needed by AMXX, and obtain the independent advancement review.
5. AMXX phase, final report/PDF, final production checks and the user-verified
   coding agent remain pending. Preserve this full scope.

**Next concrete action:** investigate the C16 signed-arithmetic
failure using the preserved bytecode and an explicitly separate diagnostic VM.
Acceptance requires an evidence-backed explanation or a minimized unresolved
reproducer, not merely a passing modified interpreter.

## Reproduction and resumption

```sh
python3 -B research/tools/toolchains.py --verify-only
python3 -B research/tools/test_pawn_audit.py
python3 -B research/tools/pawn_gate.py --record
```

The gate currently returns exit 1 intentionally. Run a full suite again only when
its relevant inputs have changed or its evidence is absent. See README.md for
setup, all suite commands and the official suite's selected compiler path.
The separate official development snapshot remains recorded as a build failure.

The example rerun and gate invocation completed before checkpoint preparation;
no compiler/VM test process was left running. Revalidate agent and process states
instead of relying on this historical statement. The bounded review has also
finished. All earlier temporary process
IDs are historical unless an authoritative tool confirms otherwise.

## Usage and synchronization

At **2026-09-10 07:03:56 UTC** (10:03:56 Israel), the account tool reported
26% used in the five-hour window and 4% in the weekly window. Reported resets:
2026-09-10 11:53:53 UTC and 2026-09-17 06:53:53 UTC, respectively. The user reports
using a reset shortly beforehand; these are tool readings, not an independent
audit of reset propagation or billing. Cumulative goal tokens are separate.

Recheck usage on resumption. Begin a checkpoint at 80% used, prioritize finishing
it at 90%, and checkpoint earlier for context capacity or milestone completion.
Do not purchase credits or redeem resets automatically.

This checkpoint must be committed and pushed to the project remote. The assistant's
checkpoint response must report the new commit and verified remote status. If
synchronization fails, retain the local record and report the exact failure.

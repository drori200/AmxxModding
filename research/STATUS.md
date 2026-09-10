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

Current milestone: the PAWN foundation audit and compiler-selection checkpoint
has been published to GitHub; save this resumption record and pause substantive
research at the usage threshold. **The PAWN advancement gate remains FAIL; AMXX
research is locked.** No language suites were repeated during this synchronization.

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

The example rerun and gate invocation completed before checkpoint preparation.
At the September 10 resumption, a process listing found no `pawncc`, `pawnrun`,
or `research/tools/` process. The agent listing confirms that
`foundation_checkpoint_review` completed. The old `pawn_inventory_review` handle
reported `pending_init` and was interrupted; it is not a live review to await.
Revalidate handles on the next resumption; all earlier process IDs are historical.

## Usage and synchronization

At the **2026-09-10 resumption**, the account tool reported 89% used in the
five-hour window and 14% in the weekly window. After publishing and verifying the
existing checkpoint, it reported **92% five-hour / 14% weekly**. Reported resets:
2026-09-10 11:53:53 UTC (14:53:53 Israel) and 2026-09-17 06:53:53 UTC,
respectively. These are account-tool readings, not per-task billing measurements
or an independent audit of the user's earlier reset. Cumulative goal tokens are
separate. No reset credit was redeemed.

Recheck usage on resumption. Begin a checkpoint at 80% used, prioritize finishing
it at 90%, and checkpoint earlier for context capacity or milestone completion.
Do not purchase credits or redeem resets automatically.

**Checkpoint publication succeeded.** A fresh login shell authenticated as
`drori200` through GitHub CLI 2.100.0 outside the sandbox. The sandbox can execute
`gh`, but its GitHub API requests fail; its authentication failure must not be
treated as proof that the user's token is invalid. Network operations require
approved execution outside the sandbox under the current environment policy.

`git push -u origin codex/pawn-foundation-checkpoint` succeeded, and
`git ls-remote --exit-code origin refs/heads/codex/pawn-foundation-checkpoint`
returned `b45b6a484da59218ee84f44fc06ead62d58ae8e5`, matching the local checkpoint.
The branch now tracks `origin/codex/pawn-foundation-checkpoint`.

Earlier synchronization failures are retained here as resolved history:

- `git push -u origin codex/pawn-foundation-checkpoint` failed with
  `fatal: could not read Username for 'https://github.com': No such device or address`.
- The connected GitHub integration can read the public repository, but its
  `create_tree` write was rejected with HTTP 403, `Resource not accessible by integration`.
- Neither earlier attempt published a checkpoint; the successful CLI push and
  explicit remote-hash check above are the publication evidence.

Commit and push this status update as the final handoff, and verify its remote
tip against `git rev-parse HEAD`. The final response must report that new commit
and its verified push status; a status file cannot contain its own commit hash.

**Capacity pause:** do not start another substantial task at the current usage.
On resumption, check live account limits before continuing the C16 investigation
specified above. A reset timestamp alone does not prove capacity was restored.
The full research objective remains active and incomplete. This goal turn made
concrete progress by resolving authentication and publishing the existing evidence;
it is not a wait on a live research process or a claim that the PAWN gate passed.

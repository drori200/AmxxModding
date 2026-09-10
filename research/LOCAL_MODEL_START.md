# Start here: local Qwen handoff

You are continuing an existing PAWN-first research project. This file is a short
starting prompt; [LOCAL_MODEL_HANDOFF.md](LOCAL_MODEL_HANDOFF.md) contains the
detailed history, evidence map, commands, remaining requirements, and work order.
The user's complete approved objective is [OBJECTIVE.md](OBJECTIVE.md).

## Non-negotiable current facts

- **The PAWN advancement gate fails. AMXX research and server execution are
  blocked.** Production build tooling already exists and is a separate activity.
- The selected compiler is the unmodified official CompuPhase source release
  advertised as 4.1.7487; its actual metadata/banner is 4.1.7483.
- Use `.cache/research/build64/pawncc` for the canonical compiler. Its internal
  maximum cell type is 64 bits. Explicit `-C32` produces baseline bytecode for
  the 32-bit-cell VM. Compiler-internal width, bytecode width, VM width, and host
  architecture are different properties.
- Latest retained original matrix: 508/542 profiles match their expectations.
  All 364 C32 profiles pass; 9 C16 and 25 C64 profiles remain unresolved.
- All 86 guide-topic evidence dispositions and independent advancement approval
  are still outstanding. The final PDF and final evaluated coding agent do not exist.
- A file or manifest saying PASS is not sufficient: inspect what was tested,
  verify the actual inputs and raw outputs, and retain limitations.

## Begin a session

1. Read [STATUS.md](STATUS.md), the objective, and handoff sections 1–3.
2. Inspect the actual branch, worktree, available files, and live processes.
   Preserve user changes and existing evidence. Work from the repository root.
3. If using a metered service, check its actual available usage. The prior
   account readings and reset times are historical. A local model's memory and
   context limits are separate from Codex's account limits.
4. With an intact cache, run `python3 -B research/tools/pawn_gate.py` to inspect
   current validity without replacing the recorded gate. Expect exit 1 while
   the recorded blockers remain. For a fresh checkout, follow handoff section 7.
5. Select one bounded task from section 9. The next substantive research task is
   the C16 signed-arithmetic failure. Do not start AMXX or rebuild everything
   simply because this is a new session.

## Working rules

Use file search to retrieve the relevant source and evidence. Read the handoff
section needed for the current task; do not fill a small context window with all
logs. Separate observed facts, source-defined contracts, hypotheses, and plans.
Predict test outcomes before observing them. Explain a failure before changing
expectations. Keep diagnostic patches outside the official source tree.

Run compiler/VM probes through the bounded harness. Preserve source/configuration
hashes, commands, diagnostics, output, exit codes, and timeouts. Stop duplicate
work only after checking an authoritative process or agent handle.

At a milestone or before losing context, update STATUS.md with completed work,
exact evidence, unresolved questions, and the next action. Review the staged
changes, commit task-owned files, push the established task branch, and verify
the remote commit. The user authorized these checkpoint commits and pushes.
Do not force-push or include credentials, binaries, or caches.

Independent review means a separately reasoned review of the evidence, not a
self-written approval. If no independent reviewer is available, leave the review
requirement open. Build the final CS 1.6 coding agent only after the user verifies
the completed research product. Using Qwen to continue research is not completion
of that final agent deliverable.

For each work unit, report: objective; files changed; exact checks and outcomes;
what the evidence establishes; remaining uncertainty; checkpoint commit and push
status; next action with acceptance criteria.

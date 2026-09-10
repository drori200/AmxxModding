Implement the approved PAWN-first research plan in the current project. Deliver a versioned development reference, reproducible research lab, evidence-backed advancement gate, and cited, visually verified PDF. Preserve production behavior and user-owned files.

Use the current workspace and retained evidence as the starting point. Audit and reuse valid completed work; preserve earlier artifacts and publish corrections explicitly. Confidence statements, compilation counts and reviewer agreement are not proof of correctness.

Work within available usage limits. Preserve progress through clear, resumable checkpoints committed and pushed to GitHub.

1. Usage management and GitHub checkpoints

Check available account-usage information at the start of a work session, after substantial work and before expensive research or test runs. Distinguish account usage limits from conversation-context capacity. Report unavailable measurements honestly.

When any applicable usage window reaches 80% used, finish the current bounded task and create a checkpoint before starting another substantial task. At 90% used, prioritize completing and pushing the checkpoint over new work. Checkpoint earlier if remaining context or usage may be insufficient for a reliable handoff.

Also checkpoint after meaningful milestones and before a planned pause. If usage information is unavailable, use smaller bounded tasks and milestone checkpoints rather than assuming unlimited capacity. Do not automatically purchase credits or redeem resets.

Every checkpoint must update research/STATUS.md with:
- The full objective and current milestone.
- Completed changes and the evidence actually verified.
- Current gate status, failures, limitations and unresolved decisions.
- Relevant toolchain versions, configurations and evidence locations.
- Commands needed to reproduce or continue the work.
- Any live process handles, pending reviews or unfinished operations.
- The next concrete action and its acceptance criteria.
- Available usage information and reset time, when known.

For every checkpoint, review and commit the task-owned changes, then push the commit to the project’s GitHub remote. This instruction authorizes those commits and pushes. Use the established task branch, or a codex/ branch where appropriate. Preserve unrelated user changes, inspect the staged diff and never force-push.

Commit the durable source, documentation, manifests and evidence needed to resume. Keep downloaded dependencies, generated binaries, secrets and disposable caches out of Git. Provide reproducible commands and provenance for excluded artifacts.

Verify that the remote branch contains the checkpoint commit. Report its commit ID and push status. If committing or pushing fails, preserve the local checkpoint and report the exact failure; do not describe it as synchronized.

Reserve enough capacity to finish this checkpoint process. Pause substantive work when remaining capacity cannot support another bounded task. Usage exhaustion does not mean the objective is complete.

On resumption, read the latest checkpoint and inspect the actual worktree and external state before continuing. Revalidate recorded process handles and avoid restarting completed work or duplicating active operations.

2. Validate the PAWN foundation

Verify that the research compiler comes from official CompuPhase sources. Record download origins, archive hashes, source integrity, compiler banners, headers, build options and VM configurations. Preserve the discrepancy between the advertised 4.1.7487 archive and revision 7483 metadata. Compare official development sources separately.

Distinguish compiler-internal types from emitted bytecode cell widths and VM cell widths. Preserve CompuPhase’s default compiler configuration for the baseline, emit explicit 32-bit cells and use a matching VM. Keep narrower compiler-internal configurations as separately labeled experiments.

Audit the harness and gate for incorrect acceptance, stale evidence, missing or duplicate profiles, configuration contamination and concurrent tool replacement. Execute negative controls proving that invalid evidence is rejected. Resolve consequential setup mistakes before trusting affected results.

3. Complete PAWN verification and the advancement gate

Audit prior claims and examples, including signed division/remainder, release-safe validation, operator result tags and differences introduced by community compiler forks.

Derive coverage from the versioned Language and Implementer’s Guides. Distinguish language semantics, optional libraries, compiler behavior, unspecified behavior and implementation defects. Keep AMXX and other host-specific APIs outside this phase.

Adapt the official regression suite with explicit diagnostic, output, runtime-error and timeout expectations. Add original tests and previously unseen combined-feature exercises. Compile and execute every complete instructional example; label fragments and deliberate failures.

Exercise the 32-bit baseline, matching 64-bit portability configurations and supported minimal 16-bit cases across relevant debug, release and optimization settings. Isolate hazardous probes with process limits. Never run unchecked invalid-memory examples as ordinary correctness tests.

Pass the gate only when every inventory obligation has adequate versioned evidence, expected outcomes are verified, corrections are tested, remaining limitations have bounded conclusions and reproducers, and no unresolved PAWN question required by AMXX remains. Relevant changes must invalidate affected evidence and advancement decisions.

4. Begin AMXX research only after the PAWN gate passes

Target Counter-Strike 1.6, AMXX 1.10 and ReAPI. Establish the compatibility bridge from canonical PAWN to the project’s AMXX compiler.

Research versioned APIs and test consequential lifecycle, ownership, callback, hook, entity, player-slot, resource, persistence and error-recovery contracts.

Study AMXXPack, AMXX Modding Kit and ReAPI as required integrations. Survey Orpheu, CSDM, Zombie Plague and other relevant community utilities using original-source evidence, distinguishing historical importance from current suitability.

Implement representative integrations in a separate research lab. Prepare an isolated local server using available resources and verify module loading, lifecycle behavior, integrations, resources and map changes. Preserve the existing game installation and production plugins.

5. Deliver and verify the research product

Provide a navigable reference, corrected examples, compatibility tables, API coverage, integration recipes, unresolved questions and one authoritative requirements-to-source-to-test ledger.

Retain reproducible commands, manifests, expectations and logs. Keep research commands and artifacts separate from production builds. AMXX execution must check the current PAWN gate.

Produce one cited PDF and verify its citations and rendered pages. Confirm research plugins cannot enter production distribution and production builds remain valid. Report completed coverage and remaining limitations precisely.

6. After I verify the research product, build the coding agent

Create an agent for CS 1.6 plugin development grounded in the validated reference and workflows. Evaluate it on previously unseen tasks covering correctness, compatibility, lifecycle behavior, resource ownership, debugging and appropriate uncertainty. Report demonstrated capabilities and remaining weaknesses.

Execution principles

Require review independent of the implementation author for consequential claims and advancement decisions. Resolve disagreements through source evidence and reproducible tests.

Delegate bounded tasks when independent scrutiny or parallel work improves the result. Account for delegated work when managing available usage. Avoid overlapping assignments and unnecessary context duplication. The primary agent remains accountable for integration and verification.

Follow unmet prerequisites. Repeat tests when relevant changes or unresolved discrepancies justify it. Do not reduce the approved scope to obtain a passing result, bypass a failing gate or claim mastery beyond the evidence.

# Research status

The active goal remains the complete PAWN-first reference, executable lab, cited
and visually verified PDF, then AMXX/ReAPI/community research and isolated server
validation. The coding agent is a later step after the user verifies the product.

1. **Current: PAWN gate and setup audit.** Official compiler origin was rechecked
   against a fresh CompuPhase download. Test-harness acceptance holes and fixture
   errors were corrected. The compiler now retains CompuPhase's default internal
   64-bit cell type while emitting explicit 16/32/64-bit bytecode for matching VMs.
2. **PAWN advancement remains FAIL.** Topic coverage, bounded defect dispositions
   and the final independent advancement review remain incomplete. The test counts
   do not authorize advancement. See [setup audit](pawn/setup-audit.md) and the
   [current gate](evidence/pawn-gate.json).
3. **AMXX research and server execution are locked.** The AMXX command checks the
   current PAWN gate before any work. Existing production tooling is separate.
4. **Pending deliverables:** expanded navigable reference, full claim/source/test
   ledger, completed lab coverage, AMXX phase after gate approval, final cited PDF
   and rendered-page verification, final production isolation check.

Prior artifacts are preserved. Earlier evidence under
`pawn-pre-default-compiler-*.json` records the superseded compiler-internal
configuration; it is not relabeled as evidence for the corrected selection.

The preceding production check verified 26 project and 24 kit plugins. No live
server runtime success is claimed. This audit has not deployed anything.

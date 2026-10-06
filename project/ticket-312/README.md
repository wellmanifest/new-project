# Ticket 312: Immutable reusable CI contracts

- **ID**: ticket-312
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

Native scanner adoption fails on an unresolved reusable CI caller. Derive actual caller/leaf check names from SHA-pinned reviewed workflow bytes, shared by generation and checking. Keep target-owned declarations, unknown-source refusal and independent publication boundaries. Follow-up: Planfile NP-008, GitHub issue #449.

- [x] AC-01: Positive and negative offline regressions pass.
- [x] AC-02: Native governance and package gates pass.
- [ ] AC-03: Independent exact-head merge and immutable release are observed.

Reviewed copies describe check names; they neither execute the callee nor grant merge approval. Dynamic, nested or unbound workflow sources remain unsupported.

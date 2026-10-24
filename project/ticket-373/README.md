# ticket-373: Assess ticket impact during README creation

- **Owner**: agent:codex-ticket-radar
- **Status**: IN_PROGRESS

Resumed 2026-10-24 by agent:claude (renewed lease after the accepted
2026-10-23 handoff): main merged into the branch so CI checks only this
ticket's range, which the pre-369/372 base could not. Delivery class
corrected from M/60 to S/30: the measured change is one component, two files
(`scripts/ticket_storage.py` +81, `tests/ticket-radar-allocation.test.py` +144).
- **Workflow state**: VALIDATION
- **Parent**: maskservice PLF-17343

SESSION_EXECUTION_AUTHORIZATION: user requests finding ticket-radar usage and fixing creation of project/ticket-*/README.md. The user explicitly authorized the bounded60minute protected admission; actual controller grant is recorded outside the repository. Independent publication remains required.

Create the initial Ticket Radar section through the external Subactor product after the declared material scope is available. Show impact score, complexity, estimated minutes, planning budget, split recommendation and diagnostics. Keep the advice separate from execution/merge authority. Missing or invalid runtime output is explicit and does not fabricate an assessment. Cover files and SQLite stores, templates and fallback scaffolding. No historical ticket rewrite or automatic dependency installation.

- [x] AC-01: File allocation includes a bounded predicted assessment for its actual declared scope.
- [x] AC-02: SQLite creation passes the same README section to the pinned writer; no extra tracked artifact is required.
- [ ] AC-03: Missing runtime, invalid/mismatched output and timeouts are visible; tests, governance and protected review pass.

Validation: 14 targeted tests pass, including real file allocation, actual pinned Registry SQLite creation/readback, malformed/unavailable runtime responses and idempotent refresh. Governance passes with zero errors and warnings. The older SQLite suite has the same two failures and one error on this change and the accepted base, due existing writer-lease/legacy-allocation fixtures; see receipt:ticket-373/sqlite-baseline-comparison. Protected review remains pending.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 52/100 |
| Complexity | M |
| Estimated effort | 54 min |
| Planning budget | 60 min |
| Split recommended | no |

Diagnostics: RADAR-ACCEPTANCE-MISSING.
<!-- ticket-radar:end -->

# Ticket 451: Preserve integrated legacy worktrees during first native adoption

- **ID**: ticket-451
- **Owner**: agent:codex / codex-bootstrap-legacy-worktrees-20261117t1250z
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-17

## Cel i Zakres

SESSION_EXECUTION_AUTHORIZATION: the user requested investigation, repair,
testing and independent protected publication of blocked autonomous delivery.
This bounded standard maintenance fixes the first-allocation obstacle without
changing ownership of preserved historical worktrees or publication authority.

Observe canonical registered worktrees whose clean commits are strict ancestors
of the bootstrap base. Preserve every checkout, branch and ignored local file.
Recheck exact inventory, Git bindings and clean state before accepting initial
admission or refreshing an existing installer receipt. Existing lease, WIP,
controller, native reservation and published-source checks remain required.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Real first allocation preserves an integrated legacy checkout;
  dirty, ambiguous, detached, noncanonical and live-leased work is refused.
- [x] AC-02: Receipt refresh shares these checks and rejects concurrent drift.
- [ ] AC-03: Governance, package parity, required CI, independent publication
  and immutable release pass before target adoption.

## Ryzyka i Uwagi

Ancestry and cleanliness establish preservation eligibility only. They never
transfer ownership, release a lease or authorize deleting a historical checkout.
No new runtime dependency. Target-specific evidence stays outside this hub.

The bounded slice is S/30 active minutes: one shared read-only observation and
two existing callers, with no new command, receipt schema or dependency. The
initial M/45 estimate included downstream adoption and external verification;
those remain separate delivery stages. Scope and implementation budgets are
unchanged; the hub policy is unchanged.

## Validation

The new real-allocation regression failed before the fix. Both bootstrap suites
now pass 58 cases; receipt refresh passes 23 cases. The existing end-of-proof
mutation regression and four focused preservation/drift cases pass. Native
governance and bundled parity pass. Coverage from copied subprocess fixtures
does not establish dead tests; none were removed. Required source-hub checks,
exact-head CI, independent review and immutable release remain mandatory.

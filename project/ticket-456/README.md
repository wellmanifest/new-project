# Ticket 456: Add explicit owner handoff for local canonical leases (NP-052)

- **ID**: ticket-456
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-11-18

SESSION_EXECUTION_AUTHORIZATION: user authorized autonomous implementation,
delegation, testing and protected publication. NP-052 adds explicit
handoff for a local canonical lease. The protected outer invoker must authenticate
the old owner; actor labels and FD JSON alone never authenticate. Handoff binds
explicit consent and the exact lease/intent/HEAD/branch/
worktree/dirty snapshot and a monotonic new session/fence with bounded TTL.
Expiry, PID absence or labels alone never transfer ownership.

Scope is limited to the handoff controller, adversarial tests, managed package
and release metadata/docs. No idle takeover algorithm change, runtime lease
effect, foreign checkout cleanup or consumer adoption.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Explicit old-owner consent validates exact owner/session/CAS,
  intent/scope, HEAD, branch, canonical worktree and dirty snapshot before an
  atomic no-follow archive+journal and monotonic new lease.
- [ ] AC-02: Replay is idempotent only for the exact result; changed state,
  symlink/noncanonical paths, frozen ownership, wrong owner, dirty/head drift,
  expiry without consent and unknown requests fail closed.
- [ ] AC-03: Real Git/controller regressions, managed governance, release
  projections and qualified tests pass without changing idle takeover policy.

## Ryzyka i Uwagi
- Risk: a handoff could become an implicit timeout takeover. Mitigation: bind
  every observed byte and CAS to explicit old-owner consent, archive before
  replacement, preserve the journal and refuse ambiguous or changed state.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-456/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 94 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

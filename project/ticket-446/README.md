# Ticket 446: Expose safe terminal lease repository and owner refusal diagnostics

- **ID**: ticket-446
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-15

## Cel i Zakres
Expose safe and precise identity refusal causes observed in PLF-22388.
SESSION_EXECUTION_AUTHORIZATION comes from the user's instruction to continue
code, tests and independent merges. Deployments, operator permission changes
and applying this controller to existing host leases are excluded.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Existing owner, repository and lease-scope guards retain their
  acceptance rules and report a distinct static refusal cause.
- [x] AC-02: Unexpected private exception details remain hidden in CLI stderr and refused
  leases remain byte-identical in real Git fixture regressions.
- [ ] AC-03: Required verification and exact-head independent merge succeed.

## Ryzyka i Uwagi
- Diagnostic changes could disclose private exception details: expose only
  an explicit allowlist of static labels and retain the generic fallback.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-446/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 52/100 |
| Complexity | M |
| Estimated effort | 51 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

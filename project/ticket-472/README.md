# Ticket 472: Enable the cancelled outcome in the default ticket activity policy

- **ID**: ticket-472
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-23

## Cel i Zakres
Enable the `cancelled` terminal outcome (`verification: owner-decision`, `releasesReservation: true`) in the shipped default `governance/ticket-activity.json` policy, document its contract in `docs/information/work-registration.md`, and update `tests/ticket-activity.test.sh` to assert the default-enabled behavior.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/ticket-activity.json` lists `"cancelled": {"verification": "owner-decision", "releasesReservation": true}` under `terminalOutcomes`.
- [x] AC-02: `docs/information/work-registration.md` documents the `cancelled` outcome (`owner-decision`, `closed-unmerged` PR binding, reservation release, resumption re-activation).
- [x] AC-03: `tests/ticket-activity.test.sh` and `./project/governance-check.sh` pass cleanly.

## Ryzyka i Uwagi
- Risk 1: Older resolvers prior to wellman ticket-125 reject unknown terminal outcomes and fail closed; documented in `docs/information/work-registration.md`.
- Continuity: Taken over via `idle_takeover.py takeover` (fencing token 4, `agent:antigravity`) from idle `agent:claude` snapshot `32f9dcc61ed1`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-472/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 44/100 |
| Complexity | M |
| Estimated effort | 41 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

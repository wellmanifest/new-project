# Ticket 473: Keep allocated worktrees out of the shared ticket index

- **ID**: ticket-473
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-24

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION. NP-058 i zgłoszenie #676. Alokacja
powiązanego worktree zapisuje stan konkretnego ticketu. Współdzielony
`project/TICKETS.md` zostaje w stanie z bazy gałęzi, aby równoległe
alokacje nie wprowadzały konfliktu w PR.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Alokacja powiązanego worktree zachowuje bajty indeksu z bazy.
- [x] AC-02: Wygenerowany jawnie indeks uwzględnia wskazany ticket i pomija
  niescalone tickety z innych gałęzi.

## Ryzyka i Uwagi
Indeks można odświeżyć zgodnie z procedurą repozytorium przez
`project/readme.sh`. Alokacja bez powiązanego worktree nadal korzysta
z tego generatora.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-473/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 48/100 |
| Complexity | M |
| Estimated effort | 47 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

# Ticket 445: Support Wellman scaffold profiles in bootstrap work-start and adoption-plan ticket root creation

- **ID**: ticket-445
- **Owner**: tom-sapletta-com (SESSION_EXECUTION_AUTHORIZATION)
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-15

## Cel i Zakres

1. **Profile scaffoldowe Wellmana w `bootstrap_scaffold_at_head` (`scripts/work_start_check.py`)**: ujednolicenie walidacji minimalnego commitu scaffoldowego `.governance/manifest.json` z zamkniętym zbiorem `WELLMAN_SCAFFOLD_PROFILES` (`profile:baseline`, `profile:domain-pack`, `profile:runtime-service`, `profile:agent-executor`, `profile:deployment`, `profile:embedded-fleet`, `profile:full`) wprowadzonym w `ticket-423`.
2. **Bezpieczne tworzenie katalogu nadrzędnego `project/` w `project/new-ticket.sh`**: gdy alokowany worktree startuje z bazy Git nieposiadającej jeszcze śledzonego katalogu `project/` (np. przy `--bootstrap-adoption-digest`, `--standard-adoption-plan` lub jawnym `--path`), skrypt weryfikuje brak symlinku / zwykłego pliku pod `project` i tworzy katalog nadrzędny przed atomowym `mkdir "$ticket_dir"`.
3. **Wydanie standardu `0.20.153`**: spójna aktualizacja `VERSION`, `CHANGELOG.md`, `governance/manifest.default.json`, `governance/manifest.hub.json` oraz `packages/wellman/pyproject.toml`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `bootstrap_scaffold_at_head` w `scripts/work_start_check.py` akceptuje wszystkie kanoniczne identyfikatory `WELLMAN_SCAFFOLD_PROFILES` i odrzuca profile spoza listy oraz manifesty natywne.
- [x] AC-02: `project/new-ticket.sh` bezpiecznie tworzy brakujący katalog nadrzędny `project/` w nowym worktree dla wszystkich ścieżek alokacji plikowej, zachowując atomową odmowę `GOV-TICKET-LOCK-003` dla istniejącego `$ticket_dir` lub niebezpiecznego symlinku `project`.
- [x] AC-03: Testy regresyjne (`tests/scaffold_bootstrap_test.py`, `tests/adoption_legacy_scaffold_test.py`), parytet wersji `0.20.153` i bramka `project/governance-check.sh` przechodzą bez błędów.

## Ryzyka i Uwagi
- Risk 1: Symlink pod `project` mógłby przekierować tworzenie katalogu ticketa poza checkout — zmitygowano jawną weryfikacją `[[ -L "$ticket_parent" || ( -e "$ticket_parent" && ! -d "$ticket_parent" ) ]]` przed `mkdir -p "$ticket_parent"`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-445/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 80 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

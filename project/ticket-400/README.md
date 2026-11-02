# Ticket 400: resolve 16 upstream SubLLM template findings and release v0.20.131

- **ID**: ticket-400
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-02

## Cel i Zakres
Rozwiązanie 16 zgłoszeń doradczych z audytu SubLLM w szablonach i skryptach bazowych standardu wellmanifest/new-project oraz wydanie wersji v0.20.131.

Zakres zmian:
1. `agent_host_check.py`: walidacja typów słownikowych przed wywołaniem `.get()` w `python_declaration()` i `lifecycle_value()`.
2. `decision_record.py`: uodpornienie parsowania i serializacji DSL przed znakami specjalnymi.
3. `decision_record.py`: poprawne uwzględnianie zarówno bloków fenced jak i bare DECISION.
4. `error/GOV-AGENT-HOST.md`: wskazanie właściwej ścieżki checkera u adoptera (`.governance/agent_host_check.py`).
5. `error/GOV-PACKAGING.md`: aktualizacja ścieżek wywołania checkera u adoptera.
6. `error/GOV-PHYS.md`: poprawienie linku do kontraktów fizycznych na stabilny adres GitHub.
7. `error/GOV-VERSION.md`: odporny snippet odczytu wersji z importem `Path` i szukaniem w górę drzewa katalogów.
8. `governance_check.py`: poprawienie ścieżki adaptera ticketu dla TicketRecord.
9. `governance_check.py`: poprawienie klucza preflight cache przy braku parametru `--base`.
10. `policy_dsl_check.py`: walidacja stanów i przejść w grafie IR.
11. `prune_merged_worktrees.py`: bezpieczne atomowe transakcje usuwania gałęzi po weryfikacji przodka.
12. `remediation_intent.py`: unikanie zduplikowanych identyfikatorów akcji w `planningOrder`.
13. `remediation_intent.py`: uodpornienie dostępu do `finding["id"]` przed brakującymi kluczami.
14. `remediation_intent.py`: zachowanie pojedynczej ucieczki JSON `\u0020` w `_atomic_json_string`.
15. `schemas`: poprawienie wyrażeń regularnych URI z `[^\\s]+` na `\\S+`.
16. `worktree_overlap_check.py`: użycie opcji `-z` (NUL delimiter) w git diff i merge-tree oraz obsługa znaków nowej linii w nazwach plików.
17. Wydanie `v0.20.131` w `VERSION`, manifestach i `pyproject.toml`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Wszystkie 16 zgłoszeń doradczych SubLLM zostało zaadresowanych w bazowych skryptach, schematach i dokumentacji.
- [x] AC-02: Wersja została podbita do 0.20.131 w `VERSION`, `packages/wellman/pyproject.toml`, `governance/manifest.hub.json` oraz `governance/manifest.default.json`.
- [x] AC-03: Pełny zestaw testów jednostkowych i integracyjnych (`pytest`, `tests/*.sh`, `tests/*.py`) przechodzi bez błędów.
- [x] AC-04: `./project/governance-check.sh` oraz `wellman check` raportują zero błędów (`GOV-PASS`).

## Ryzyka i Uwagi
- Brak ryzyka regresji; skrypty zachowują pełną wsteczną kompatybilność, a pliki w `packages/wellman/src/wellman/_bundled/` są zsynchronizowane binarnie z `scripts/`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-400/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 72/100 |
| Complexity | L |
| Estimated effort | 80 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->

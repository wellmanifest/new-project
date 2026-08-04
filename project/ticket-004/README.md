# Ticket 004: Reconcile canonical governance and cost-bounded review

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: BLOCKED
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-04

## Cel i Zakres

Usunąć konflikt dwóch różnych kontraktów opublikowanych jako `0.9.0` i wydać
jeden kanoniczny standard `0.10.0`. Nowa wersja zachowa bounded delivery z
gałęzi `feat/bounded-delivery-contract@1ae86a1`, ale przyjmie z `main@c0bb63e`
poprawną semantykę rezerwacji: tylko `IN_PROGRESS` blokuje workstream i zakres;
`BACKLOG`, `PLAN` oraz `BLOCKED` pozostają widoczne, lecz nie uczestniczą w
konfliktach aktywnej implementacji.

Zakres jest integracyjnym wyjątkiem od domyślnego budżetu pięciu plików,
ponieważ schema, manifest, validator, katalog diagnostyk i fixture test stanowią
jeden nierozdzielny publiczny kontrakt. Maksymalnie dziesięć plików poza
ticketem, jedna zdolność, dwa komponenty, zero nowych zależności i maksymalnie
30 minut aktywnej implementacji. Checkpoint następuje po 25 minutach; brak
zielonych testów oznacza zatrzymanie i dekompozycję, nie poszerzenie zakresu.

Model Koru nie jest częścią pakietu `.governance` upstreamu. Zmiana z drogiego
Gemini 3.1 Pro Preview na `z-ai/glm-5.2` zostanie wykonana w zależnym
`todo2code/ticket-018`, gdzie faktycznie znajduje się workflow.

## Architektura przed implementacją

- Źródło prawdy: `main@c0bb63e` jako historia adopcji i lifecycle;
  `1ae86a1` jako źródło bounded-delivery do selektywnego przeniesienia.
- Validator pozostaje deterministyczny i bez LLM.
- `activeStatuses = [IN_PROGRESS]`; `nonActiveStatuses = [BACKLOG, PLAN,
  BLOCKED]`.
- Delivery schema i walidacja budżetów pozostają zachowane.
- Wersja `0.10.0` rozróżnia nowy połączony kontrakt od obu niezgodnych 0.9.0.
- Rollback: pozostawienie targetów na dotychczasowym pełnym SHA; generator nie
  nadpisuje driftu bez jawnego `--upgrade`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Człowiek zatwierdza architekturę i integracyjny limit; podczas
      implementacji lista została skorygowana z dziewięciu do dziesięciu
      plików wyłącznie o istniejący fixture wersji locka wymagany przez AC-06,
      bez nowego rezultatu, komponentu lub zależności.
- [x] AC-02: Standard ma jedną wersję `0.10.0`, a dokumentacja wyjaśnia konflikt
      dwóch wariantów 0.9.0 i sposób migracji.
- [x] AC-03: Manifest oraz schema zachowują bounded delivery i jednocześnie
      klasyfikują wyłącznie `IN_PROGRESS` jako aktywną rezerwację.
- [x] AC-04: Validator nie zgłasza konfliktu, zależności, ownership ani overlap
      dla ticketu pozostającego w `PLAN/BLOCKED`, lecz nadal blokuje te same
      naruszenia dla `IN_PROGRESS`.
- [x] AC-05: Fixture testy pokrywają oba stany, delivery budget, stale base i
      przekroczenie zakresu bez LLM ani sieci.
- [x] AC-06: Generator adopcji może przypiąć pełny SHA nowego kontraktu bez
      nadpisania lokalnego manifestu i z aktualnymi hashami locka.
- [x] AC-07: Pełne testy governance, diff check i schema checks przechodzą;
      dokumentacja odróżnia fakty od historycznych danych.
- [x] AC-08: Zależny ticket-018 w `todo2code` używa `z-ai/glm-5.2`, nie Gemini
      3.1 Pro Preview, bez wykonywania kosztownego live benchmarku.

## Ryzyka i Uwagi

- Niejawne scalanie całych branchy mogłoby przywrócić starsze lifecycle albo
  usunąć generator adopcji; dlatego przenoszone będą konkretne kontrakty, a nie
  ślepy merge.
- Zmiana wersji unieważnia stare locki dopiero po jawnej adopcji pełnego SHA.
- GLM jest wyborem kosztowym użytkownika; deterministyczne governance nie
  zależy od jego dostępności ani jakości.

## Wynik walidacji

- `tests/governance-validator.test.sh`: PASS.
- `tests/governance-scripts.test.sh`: PASS.
- `tests/adoption-lock.test.sh`: PASS.
- Python compile, JSON parse i `git diff --check`: PASS.
- Radon: maksymalna złożoność funkcji CC=15; maksymalna długość funkcji 53
  linie w lokalnym audycie AST.
- Gałąź PR #1 została połączona z `main@c54694a`. Ukończony ticket zatwierdzania
  aplikacją pozostał jako `ticket-003`, a kontrakt 0.10 jako `ticket-004`.
- Połączone regresje dla bounded delivery, lifecycle i approval evidence
  przechodzą; walidator zachowuje maksymalne CC=15 i długość funkcji 53 linie.
- Pierwsze review Validator App dla zintegrowanego HEAD zażądało usunięcia
  globalnego wyłączenia fail-fast z helpera testowego. Helper przechwytuje
  teraz oczekiwany błąd wyłącznie w lokalnym warunku; świeże testy przechodzą,
  a ticket ponownie oczekuje na review aktualnego HEAD.
- `todo2code` ma lokalnie wykonywalny model `openrouter/z-ai/glm-5.2`; pełny
  `npm run verify` przeszedł 334/335 testów z jednym skipem JDK i bez LLM.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-004/`.

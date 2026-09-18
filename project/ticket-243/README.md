# Ticket 243: fast local governance preflight cache

- **ID**: ticket-243
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-18

## Cel i Zakres
Optymalizacja lokalnego cyklu deweloperskiego i testowego poprzez dodanie preflight cache
oraz pomiaru czasów faz (`--timing`) w `scripts/governance_check.py`.
Zapobiega wielokrotnemu powtarzaniu tych samych, deterministycznych weryfikacji przy niezmienionym kodzie
i politykach, zachowując bezwzględny wymóg pełnej weryfikacji exact-head w środowisku CI.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Dodanie opcji `--timing` raportującej czasy wykonania poszczególnych faz walidatora governance.
- [x] AC-02: Implementacja deterministycznego preflight cache w `.subactor/cache/governance-preflight.json` (lub `--cache-file`) kluczowanego unikalnym hashem wejść (base SHA, head SHA, dirty digest, skróty manifestu/locka/profili/reguł, argumenty).
- [x] AC-03: Błyskawiczna unieważnialność przy jakiejkolwiek modyfikacji plików, parametrów lub stanu repozytorium; ominięcie cache przy `--no-cache`, `--enforce-approval`, `--actor ci` oraz w środowiskach CI (`CI=true`, `GITHUB_ACTIONS=true`).

## Ryzyka i Uwagi
- Risk 1: Fałszywy cache-hit przy nieuwzględnionych zmianach w drzewie roboczym.
  Mitygacja: Rygorystyczny `dirty_digest` obejmujący stan `git status --porcelain=v1` wraz ze skrótami sha256 zmodyfikowanych i nieśledzonych plików.
- Risk 2: Osłabienie walidacji w CI.
  Mitygacja: Twarde wyłączenie cache w CI i przy weryfikacji approval evidence.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-243/`.


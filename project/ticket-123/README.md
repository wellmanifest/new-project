# Ticket 123: Standardize multi-agent change leases and publication fencing

- **ID**: ticket-123
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-25

## Cel i Zakres
Zdefiniować adoptowalny, deterministyczny kontrakt koordynacji wielu agentów,
który serializuje mutacje repozytorium i publikacji przez compare-and-swap,
monotoniczną rewizję lease oraz fencing token. Standard ma blokować zapis ze
starego lease, zamknięcie lub supersede PR podczas publication freeze oraz
cleanup bez terminalnego receipt. Runtime kontrolera pozostaje poza
`wellmanifest` i należy do systemu adoptującego.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Zamknięty schemat `wellmanifest.change-lease/v1` opisuje lease,
      żądanie przejścia i receipt z CAS, fencing tokenem, exact head i
      publication freeze.
- [x] AC-02: Deterministyczny checker odrzuca stale revision/token, nielegalne
      przejścia, zmianę planu podczas freeze oraz close/supersede bez
      terminalnego dowodu replacementu.
- [x] AC-03: Standard, stabilny kod błędu i checker są dystrybuowane adopterom
      jako managed payload, a bramka repozytorium jest przypisana do istniejącej
      normatywnej reguły kompletności checkerów `C-CI-003`. Rozszerzone reguły
      operacyjne są osobnym zależnym slice.
- [x] AC-04: Testy pozytywne, konkurencyjne i adversarial oraz pełna governance
      repozytorium przechodzą na dokładnej bazie ticketu.

## Ryzyka i Uwagi
- Ryzyko: sam domain pack nie może być rozproszonym lockiem. Mitygacja:
  standard jawnie rozdziela conformance od runtime i wymaga, aby adopter
  egzekwował token w zaufanym effect boundary.
- Ryzyko: wygasający lease może przerwać poprawną pracę. Mitygacja: heartbeat
  tworzy nową rewizję bez rozszerzania scope, planu ani authority.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-123/`.

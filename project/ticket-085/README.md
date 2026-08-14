# Ticket 085: Standardize CQRS domain contract skeleton

- **ID**: ticket-085
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-14

## Cel i Zakres

Ustanowić deterministyczny, opcjonalnie aktywowany kontrakt CQRS dla
repozytoriów standardów Wellmanifest. `operations/index.json` ma być jedynym
źródłem prawdy o komendach i zapytaniach, a katalogi `events/` i `error/`
obowiązkowymi, append-only katalogami faktów oraz publicznych odmów. Modele
JSON Schema lub Protobuf pozostają wyłącznie kształtem transportowym danych i
nie mogą przejmować semantycznej władzy nad C/Q.

Zakres obejmuje zamknięty wpis `domainContracts` w manifeście, walidację
minimalnego grafu C/Q/Event/Error, domyślne ścieżki własności oraz dokumentację
adopcji. Tryb domyślny pozostaje wyłączony dla zwykłych repozytoriów; każdy
standard domenowy włącza `mode: cqrs` we własnym ticketcie adopcyjnym.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Manifest przyjmuje wyłącznie `domainContracts.mode` równe `none`
      albo zamknięty kontrakt `cqrs` ze stałymi kanonicznymi ścieżkami.
- [ ] AC-02: W trybie `cqrs` brak katalogu/rejestru, zduplikowana definicja C/Q
      albo zerwane odwołanie command-query-event-error kończy bramkę błędem.
- [ ] AC-03: Poprawny minimalny standard CQRS przechodzi walidację, a istniejące
      manifesty bez pola i domyślny `mode: none` zachowują kompatybilność.
- [ ] AC-04: Dokumentacja i szablon agenta jednoznacznie wskazują
      `operations/index.json` jako jedyne źródło prawdy C/Q oraz rozdzielają
      semantykę domeny od modeli transportowych.

## Ryzyka i Uwagi
- Największym ryzykiem jest wymuszenie szkieletu domenowego na zwykłych
  aplikacjach. Mitygacja: jawny opt-in `mode: cqrs`, przy zachowaniu obsługi
  starszych manifestów i domyślnego `mode: none`.
- Drugim ryzykiem jest powstanie kilku konkurencyjnych źródeł prawdy.
  Mitygacja: walidator odrzuca klucze `commands`/`queries` w katalogach zdarzeń
  i błędów, a relacje sprawdza wyłącznie względem rejestru operacji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-085/`.

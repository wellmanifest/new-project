# Ticket 002: Integracja adopcji manifestu z goal

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: BLOCKED
- **Workflow state**: BLOCKED
- **Utworzono**: 2026-08-04

## Cel i Zakres

Ułatwić bezpieczną adopcję standardu w istniejących projektach korzystających
z `goal`: generator otrzymuje bezpieczny tryb `--check`, dokumentacja opisuje
jednokomendowy workflow, a repozytorium `semcod/goal` dostarcza wrapper
`goal governance adopt` pobierający wyłącznie pełne SHA standardu.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `create_adoption_lock.py --check` nie zapisuje plików, pokazuje
  plan i zwraca niezerowy kod dla driftu.
- [x] AC-02: `goal governance adopt` wymaga pełnego SHA, weryfikuje checkout i
  przekazuje `--check`/`--upgrade` bez użycia shella.
- [x] AC-03: Testy pokrywają pierwszą adopcję, stan aktualny, drift, upgrade i
  odrzucenie niepełnego SHA.
- [x] AC-04: Dokumentacja podaje prostą ścieżkę dla istniejącego projektu oraz
  jawnie blokuje adopcję produkcyjną przed publikacją 0.9.0.
- [ ] AC-05: Po publikacji pełnego SHA co najmniej dwa wybrane repozytoria
  zależne przechodzą preflight i kontrolowaną adopcję.

## Ryzyka i Uwagi

- Ryzyko: ruchomy branch mógłby podmienić standard. Mitygacja: pełny
  40-znakowy SHA i weryfikacja checkoutu.
- Ryzyko: `--check` mógłby częściowo zapisać pliki. Mitygacja: plan jest
  obliczany przed ścieżką zapisu i testuje się niezmienność drzewa docelowego.
- Ograniczenie: bieżące 0.9.0 nie ma jeszcze opublikowanego SHA/tagu, więc
  produkcyjne repozytoria nie zostaną teraz zmodyfikowane.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-002/`.

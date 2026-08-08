# Ticket 039: Publish atomic adoption contract as v0.13.0

- **ID**: ticket-039
- **Owner**: agent:codex
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-08

## Cel i zakres

Opublikować atomowy kontrakt adopcji z zakończonego ticketu 038 jako nową,
niezmienną wersję `0.13.0`. Zmiana dodaje opcjonalne publiczne pole intent/v3
i nowe zachowanie walidatora, dlatego otrzymuje minor release; istniejące
`v0.12.0` zachowuje dotychczasowe znaczenie.

`VERSION`, domyślny manifest, release changelog oraz aktywne asercje testowe
muszą wskazywać `0.13.0`. Annotowany tag i GitHub Release mogą powstać dopiero
dla chronionego merge SHA, który przeszedł pełny Linux contract w czystym,
odłączonym checkoutcie. Todo2code przypnie ten pełny SHA, nie tag ani branch.

## Kryteria odbioru

- [ ] AC-01: `VERSION`, domyślny manifest i aktywne asercje bieżącej wersji
  wskazują `0.13.0`; bazowa strona regresji upgrade pozostaje `0.12.0`.
- [ ] AC-02: `CHANGELOG.md` zamyka `Unreleased` jako `0.13.0` i opisuje
  standardAdoption, hash-bound managed set oraz zachowane zwykłe bramki.
- [ ] AC-03: Pełny Linux CI contract oraz chroniony Windows check przechodzą
  dla dokładnego HEAD PR.
- [ ] AC-04: Czysty detached checkout merge SHA przechodzi pełny Linux
  contract przed publikacją.
- [ ] AC-05: Annotowany tag `v0.13.0` i opublikowany GitHub Release wskazują
  ten sam pełny, chroniony merge SHA.
- [ ] AC-06: Istniejące tagi i Release nie są przesuwane, nadpisywane ani
  usuwane.

## Ryzyka i uwagi

- Jeśli tag lub Release już istnieje, publikacja zatrzymuje się bez overwrite.
- Jeśli `main` zmieni się przed publikacją, czysty checkout i testy zostaną
  powtórzone dla aktualnego merge SHA.
- `0.13.0` nie może błędnie przepisać `0.12.0` używanego jako baza realnej
  regresji upgrade.
- Tag powstaje dopiero po chronionym merge i exact-head approval.

## Poza zakresem

- Brak dalszej zmiany schematu lub algorytmu z ticketu 038.
- Brak adopcji w todo2code; wykona ją ticket-050 po opublikowaniu pełnego SHA.
- Brak tagów ruchomych, force-update lub prerelease.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-039/`.

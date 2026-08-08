# Ticket 039: Publish atomic adoption contract as v0.13.0

- **ID**: ticket-039
- **Owner**: agent:codex
- **Status**: DONE
- **Workflow state**: DONE
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

- [x] AC-01: `VERSION`, domyślny manifest i aktywne asercje bieżącej wersji
  wskazują `0.13.0`; bazowa strona regresji upgrade pozostaje `0.12.0`.
- [x] AC-02: `CHANGELOG.md` zamyka `Unreleased` jako `0.13.0` i opisuje
  standardAdoption, hash-bound managed set oraz zachowane zwykłe bramki.
- [x] AC-03: Pełny Linux CI contract oraz chroniony Windows check przechodzą
  dla dokładnego HEAD PR.
- [x] AC-04: Czysty detached checkout merge SHA przechodzi pełny Linux
  contract przed publikacją.
- [x] AC-05: Annotowany tag `v0.13.0` i opublikowany GitHub Release wskazują
  ten sam pełny, chroniony merge SHA.
- [x] AC-06: Istniejące tagi i Release nie są przesuwane, nadpisywane ani
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

## Zatwierdzenie interaktywne

Użytkownik odpowiedzią „tak” 2026-08-08 zatwierdził implementację i publikację
immutable `v0.13.0` zgodnie z `intent.json`. Zgoda sesyjna nie zastępuje
exact-head merge approval.

## Dowody publikacji

- PR #56: exact-head Validator App APPROVED dla
  `a5c40a5e51a06e74bb2e9678811633f19c4e039c`.
- Chronione checki `test` i `windows-governance`: PASS.
- Merge/release SHA: `12158ef0c009428deddceebb1049ddc3cb898eb3`.
- Czysty detached checkout merge SHA: pełny Linux contract PASS; drzewo czyste.
- Annotowany tag `v0.13.0`: obiekt
  `ecdf676ef8289b4996f0c0b2cec417228af5eb52`, peeled commit równy release SHA.
- GitHub Release: https://github.com/wellmanifest/new-project/releases/tag/v0.13.0
- Release jest opublikowany, nie jest draftem ani prerelease’em i wskazuje
  dokładny merge SHA.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-039/`.

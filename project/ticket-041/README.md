# Ticket 041: Publish managed complexity repair

- **ID**: ticket-041
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-08

## Cel i Zakres

Opublikować zakończony, behavior-preserving refaktor ticketu 040 jako
niezmienną wersję poprawkową `0.13.1`. Publiczny kontrakt v0.13.0 nie zmienia
się; patch release zastępuje jedynie zarządzane źródła Pythona wariantem, który
przechodzi downstream Koru bez wyłączeń i bez zmiany progów.

`VERSION`, domyślny manifest, changelog oraz asercje bieżącej wersji muszą
wskazywać `0.13.1`, podczas gdy testowe strony historycznych upgrade'ów
zachowują swoje wersje bazowe. Annotowany tag i GitHub Release mogą powstać
dopiero dla chronionego merge SHA po pełnym Linux contract w czystym detached
checkoutcie. Todo2code przypnie pełny SHA wydania, nigdy tag ani branch.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `VERSION`, domyślny manifest i aktywne asercje bieżącej wersji
  wskazują `0.13.1`; historyczne wersje bazowe regresji pozostają niezmienione.
- [x] AC-02: `CHANGELOG.md` opisuje behavior-preserving redukcję złożoności i
  brak zmiany kontraktu adopcji.
- [ ] AC-03: Pełny Linux CI contract i chroniony Windows check przechodzą dla
  dokładnego HEAD PR.
- [ ] AC-04: Czysty detached checkout merge SHA przechodzi pełny Linux contract
  i pinned Vallm 0.1.94 scan przed publikacją.
- [ ] AC-05: Nowy annotowany tag `v0.13.1` i opublikowany GitHub Release
  wskazują ten sam chroniony merge SHA.
- [ ] AC-06: `v0.13.0` i wszystkie wcześniejsze tagi/Release pozostają
  niezmienione; publikacja zatrzymuje się, jeśli `v0.13.1` już istnieje.

## Ryzyka i Uwagi

- Ryzyko: mechaniczne zastąpienie wszystkich `0.13.0` uszkodzi bazową stronę
  regresji upgrade. Mitygacja: zmieniać tylko asercje bieżącej wersji i
  zachować jawne historyczne pary.
- Ryzyko: tag powstanie dla niezwalidowanego lub zmienionego SHA. Mitygacja:
  publikować dopiero po merge, ponownym czystym teście i sprawdzeniu braku tagu.
- Poza zakresem: dalszy refaktor, zmiana schematu/walidatora, zależności,
  downstream adoption, moving tag, force-update lub prerelease.

## Dowody walidacji przed publikacją

- Release preparation commit:
  `d998367e7a8de068d532372b5cf9d7b87d645278`.
- `VERSION`, manifest domyślny, lock-adoption assertion i bieżące asercje
  walidatora wskazują `0.13.1`; historyczny fixture pozostaje
  `0.12.0 → 0.13.0`.
- Pełny skonfigurowany Linux CI contract przechodzi lokalnie.
- Windows, exact-head Validator, czysty merge checkout, tag i Release pozostają
  obowiązkowymi kolejnymi bramkami.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Zatwierdzenie

Użytkownik zatwierdził publikację immutable `v0.13.1` 2026-08-08. Ticket
przeszedł do `IN_PROGRESS / EDIT` przed zmianą plików wydania.

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-041/`.

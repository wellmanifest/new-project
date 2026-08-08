# Ticket 037: Publish immutable 0.12.0

- **ID**: ticket-037
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-08

## Cel i zakres

Opublikować zmianę własności z ticketu 036 jako nową, niezmienną wersję
`0.12.0`. Wersja, domyślny manifest, changelog i asercje testowe muszą wskazywać
ten sam numer, a downstream ma przypinać pełny SHA wydania.

`v0.11.0` zachowuje dotychczasowe znaczenie. Nowy tag i GitHub Release mogą
powstać dopiero dla chronionego merge SHA, który przeszedł testy w czystym,
odłączonym checkoutcie.

## Kryteria odbioru

- [ ] AC-01: `VERSION`, domyślny manifest i wszystkie aktywne asercje wersji
  wskazują `0.12.0`.
- [ ] AC-02: `CHANGELOG.md` zamyka `Unreleased` jako `0.12.0` i opisuje dokładną
  własność `CHANGELOG.md` oraz `.env.example`.
- [ ] AC-03: Pełny Linux CI contract i chroniony Windows check przechodzą dla
  dokładnego HEAD PR.
- [ ] AC-04: Annotowany tag `v0.12.0` i GitHub Release wskazują ten sam pełny
  SHA z chronionego `main`.
- [ ] AC-05: Czysty detached checkout merge SHA przechodzi pełny Linux CI
  contract przed utworzeniem taga.
- [ ] AC-06: Żaden istniejący tag ani Release nie jest przesunięty, nadpisany
  lub usunięty.

## Ryzyka i mitygacje

- Jeśli tag lub Release już istnieje, publikacja zatrzymuje się bez overwrite.
- Jeśli `main` zmieni się przed publikacją, czysty checkout i testy są
  powtarzane dla aktualnego merge SHA.
- Tag powstaje dopiero po chronionym merge i exact-head approval.
- Downstream nie przyjmuje nazwy brancha ani samego numeru wersji jako źródła
  adopcji; wymagany jest pełny SHA.

## Poza zakresem

- Brak dalszych zmian semantyki własności lub runtime walidatora.
- Brak adopcji w `semcod/todo2code`; pozostaje ona w ticket-050 tego repozytorium.
- Brak przesuwania lub przepisywania istniejących tagów.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-037/`.

## Zatwierdzenie interaktywne

Użytkownik odpowiedzią „tak” 2026-08-08 zatwierdził implementację i publikację
immutable `v0.12.0` zgodnie z `intent.json`. Zgoda sesyjna nie zastępuje
exact-head merge approval.

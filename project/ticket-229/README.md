# Ticket 229: Route stalled approval to managed publication recovery

- **ID**: ticket-229
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-14

## Cel i Zakres
Połączyć istniejące diagnostyki approval z konkretną receptą odzyskania
postępu publikacji: preflight, przekazanie do kontrolera, readback przed retry
i osobne dowody push/PR/review/merge/release/deploy. Bez nowych bramek.
Autoryzacja sesji: użytkownik zlecił optymalizację standardów i publikację
przez PR oraz chroniony merge. Nie jest to autoryzacja samodzielnego approval.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Wszystkie istniejące kody approval prowadzą do jednej recepty
  z rozróżnieniem braku dispatch, oczekiwania, błędu i nieaktualnego HEAD.
- [ ] AC-02: Testy chronią nawigację i granice authority; standard nie dodaje
  bramki ani obowiązkowego magazynu, nie zmienia dozwolonych efektów.

## Ryzyka i Uwagi
- Ryzyko: uznanie zielonego CI albo exit 0 za merge. Recepta wymaga
  readback dokładnego PR/HEAD i istniejących chronionych dowodów.
- Poza zakresem: Taskand-gpt6, kasowanie pracy, naprawa historycznej delty
  Taskand, instalacja nowych kontrolerów i ręczna zmiana kopii adopcyjnych.

## Rejestracja i walidacja

- Projektowy pilot Planfile: PLF-010; stan jest lokalną projekcją, nie approval.
- Kanoniczna recepta: `error/GOV-APPROVAL.md`; kontekst i ograniczenia:
  `docs/information/controlled-change-streaming.md`.
- Test regresyjny przed poprawką odrzucił brak powiązania approval z runbookiem.
  Brama hubu po poprawce: zero błędów; pełny zestaw jest sprawdzany przed PR.
- Dodatkowy checker docs z pinu `ebe7501063ef4f3e63ded610c2d3183010ca636e`
  zgłasza DOCS_METADATA dla normatywnego runbooka w `error/`. To jawna luka
  między standardami, nie zgoda na ominięcie wymaganej bramki publikacji.
  Dowody robocze: prywatny audyt `approval-recovery-229-20260914.K6rDCY`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-229/`.

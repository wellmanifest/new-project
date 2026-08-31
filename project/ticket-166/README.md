# Ticket 166: Release corrected adoption projection

- **ID**: ticket-166
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-31

## Cel i Zakres
Publikacja naprawy projekcji checków jako nowej, niezmiennej wersji standardu.
Wydany wcześniej tag `v0.19.15` wskazuje commit sprzed merge PR #270, dlatego
adopter nie może użyć go jako źródła tej poprawki.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Wszystkie deklarowane wersje standardu wskazują `0.19.16`.
- [ ] AC-02: Testy adopcji oczekują nowej wersji, a tag/release po merge wiąże
  dokładny commit z `v0.19.16`.

## Ryzyka i Uwagi
- Risk 1: Tag może zostać utworzony wyłącznie po chronionym merge aktualnego
  head; release weryfikowany jest przez generator adopcji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-166/`.

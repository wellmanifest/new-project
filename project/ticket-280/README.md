# Ticket 280: Physical interface contracts: declared semantics changes need hardware acceptance

- **ID**: ticket-280
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-30

## Cel i Zakres
Zmiany wartości o znaczeniu fizycznym (piny, poziom aktywny, pull-up, zestaw
modułów profilu, skala, zakres, czasy) przechodziły testy repozytorium, choć
urządzenie przestawało działać: 29.09 odwrócona polaryzacja krańcówek Tic249
(maskservice/c2004 9075af5) i profil StackNet bez modułu pompy
(maskservice/stacknet eba4b09). Adopter deklaruje takie pliki w
`.governance/physical-contracts.json`, a intent musi nazwać każdą zmienioną
właściwość z wartością przed i po oraz planem odbioru na sprzęcie
(P-PHYS-001..003, GOV-PHYS-001/002). Wynik:
[physical-interface-contracts.md](../../docs/information/physical-interface-contracts.md).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Zmiana pliku z zadeklarowanego kontraktu bez `physicalChanges` daje GOV-PHYS-001; adopter bez deklaracji nie jest dotknięty.
- [x] AC-02: Nieczytelna deklaracja daje GOV-PHYS-002 (fail closed); wpis z before == after albo bez acceptance jest odrzucany.
- [x] AC-03: Reguły P-PHYS-* są zmapowane w rule-enforcement, kody mają dokumentację w `error/GOV-PHYS.md`.

## Ryzyka i Uwagi
- Bramka nie rozpoznaje, którą właściwość zmienia diff; wymusza nazwanie zmian i plan odbioru. Sama obserwacja na sprzęcie (P-PHYS-002) pozostaje manualna do czasu receiptu sprzętowego.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-280/`.

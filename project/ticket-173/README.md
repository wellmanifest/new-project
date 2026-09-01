# Ticket 173: Release resumable work continuity

- **ID**: ticket-173
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01

## Cel i Zakres

Opublikować scalony kontrakt ciągłości pracy z ticketu 172 jako nowy,
niezmienny standard `0.19.19`, który mogą adoptować pozostałe repozytoria.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Wersja, oba manifesty i fixtury adopcji wskazują `0.19.19`.
- [x] AC-02: Pełna bramka standardu przechodzi dla kompletnego pakietu z
  checkpoint schema, runtime i runbookiem.
- [ ] AC-03: Po protected merge tag `v0.19.19` i GitHub Release wskazują
  dokładny commit default branch zawierający merge ticketu 172.

## Ryzyka i Uwagi
- Risk 1: Istniejących tagów nie wolno przesuwać; korekta wymaga kolejnej
  wersji. Release nie może wyprzedzić protected merge tego ticketu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-173/`.

# Ticket 149: Resolve ticket reservations from dynamic registries

- **ID**: ticket-149
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-30

## Cel i Zakres

Usunąć z allocatora ticketów twarde założenia o statusie `IN_PROGRESS`,
lokalizacji manifestu i dozwolonych workstreamach. Allocator ma rozwiązywać te
wartości z bieżącego rejestru governance, tak samo jak główny validator.

Historyczny carrier może zachować tekst stanu po terminalnym merge receipt;
nie może jednak wymuszać utrzymywania drugiej listy statusów w skrypcie.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: allocator rozwiązuje manifest adoptera i manifest huba bez
      stałej ścieżki zależnej od typu repozytorium.
- [x] AC-02: aktywne statusy i identyfikatory workstreamów pochodzą wyłącznie
      z manifestu; zmiana rejestru zmienia zachowanie bez zmiany skryptu.
- [x] AC-03: nieznany workstream, brak manifestu i niepoprawny rejestr są
      odrzucane fail-closed przed utworzeniem katalogu ticketu.
- [x] AC-04: test regresyjny potwierdza niestandardowy aktywny status oraz
      zwolnienie historycznego statusu spoza rejestru.
- [x] AC-05: pełna bramka governance i testy skryptów przechodzą.

## Ryzyka i Uwagi

- Manifest jest źródłem prawdy o słowniku lifecycle; brak lub uszkodzenie tego
  źródła zatrzymuje alokację zamiast uruchamiać zaszyty fallback.
- Zmiana nie uznaje Markdownu za merge receipt i nie nadaje authority.

## Dowody walidacji

- `bash tests/governance-scripts.test.sh` — PASS, łącznie z brakującym i
  uszkodzonym rejestrem, nieznanym workstreamem oraz niestandardowym aktywnym
  statusem.
- wszystkie `tests/*.test.sh` — PASS.
- `./project/governance-check.sh --actor agent` — `GOV-PASS`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-149/`.

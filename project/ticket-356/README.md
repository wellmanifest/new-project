# Ticket 356: Deduplicate bootstrap allocation scope for issue 480

- **ID**: ticket-356
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-10-20

## Cel i zakres

SESSION_EXECUTION_AUTHORIZATION: użytkownik zlecił kontynuację napraw,
testów i scalania. Zakres tego ticketu to błąd #480: duplikowanie
`allowedPaths` w pierwszej alokacji po adopcji. Zmiana źródłowa dotyczy
wyłącznie `project/new-ticket.sh` i testu rzeczywistej alokacji.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Powtórzone `TODO.md` i `project/TICKETS.md` dają po jednym
  wpisie w `allowedPaths`, zachowując porządek.
- [x] AC-02: Lokalny `scopeHash` odpowiada dokładnie zapisanej liście,
  a chroniona bramka nie zgłasza GOV-INTENT-002.
- [x] AC-03: Po dopuszczeniu źródła zmiana przechodzi chronione CI,
  niezależny przegląd i scalanie.

## Ryzyka i Uwagi
- Zmiana rozwiązuje issue #480 bez łamania istniejących adopcji.
- Testy scaffold_bootstrap_test weryfikują pełny cykl alokacji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-356/`.

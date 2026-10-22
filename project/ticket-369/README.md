# Ticket 369: A bare governance-check on a ticket branch validates its committed range (issue 520)

- **ID**: ticket-369
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #520: `./project/governance-check.sh` bez `--base` na gałęzi ticketu nie
widział zacommitowanej implementacji, więc brak kontraktu `delivery`
(GOV-DELIVERY-001) przechodził lokalnie jako `GOV-PASS` (ticket-364 / PR #513).
Wrappery przekazują `--infer-ticket-base`, który wiąże bazę z
`git merge-base HEAD origin/<target>`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture: merge-base z celem, który poszedł dalej; inne gałęzie i odłączony HEAD bez zmian; brak `origin/<target>` → GOV-BASE-001; kilka celów wymaga `targetBranch` ticketu; `main()` wiąże tylko gołe wywołania z flagą, przed kluczem cache; oba wrappery przekazują flagę; kopia Wellman identyczna. Odtworzenie: ticket bez `delivery` → GOV-DELIVERY-001 (wcześniej GOV-PASS). Testy cache, runtime safety i governance validator przechodzą.
- [x] AC-02: runbook `GOV-INTENT` (Verification), test w CI, wersja 0.20.116.

## Ryzyka i Uwagi
- Lokalne wywołania na gałęziach ticketów mogą zgłosić błędy, które wcześniej były ukryte; to zamierzony efekt. OneDev i CI (odłączony HEAD, jawne `--base`) bez zmian.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-369/`.

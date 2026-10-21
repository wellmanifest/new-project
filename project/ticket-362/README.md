# Ticket 362: Reconcile the stale autonomous-merge host block when no nolimits block exists (issue 507)

- **ID**: ticket-362
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-21

## Cel i Zakres
Issue #507 (część 1): `render()` wymagał dokładnie jednego bloku `wellmanifest:nolimits`, a pliki hostów floty
mają tylko przestarzały blok `autonomous-merge` (merge na zielonych testach, `gh pr merge --admin`).
Próbka 216 plików: wszystkie bez `nolimits`, żaden z remedium `LIM-MERGE-003` poza blokiem.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: plik bez `nolimits` jest uzgadniany (idempotentnie, CRLF); podgląd 3 plików z issue: main `refused`, ticket `changed=True`, pliki bez zmian.
- [x] AC-02: częściowe znaczniki i remedium poza `nolimits` nadal odrzucane; 10 testów.

## Ryzyka i Uwagi
- Rollout na pliki floty (część 2 issue) wymaga osobnych ticketów per repozytorium i decyzji właściciela pliku hosta spoza Git.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-362/`.

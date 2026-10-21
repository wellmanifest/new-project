# Ticket 363: Warn about the stale autonomous-merge host block (issue 507 part 3)

- **ID**: ticket-363
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-21

## Cel i Zakres
Issue #507 (część 3): ostrzeżenie bramki dla przestarzałego bloku `autonomous-merge` w plikach hosta,
by rollout (część 2) był widoczny per repozytorium. Sygnatura `wellmanifest/merge@ticket-008`
występuje we wszystkich 216 zaobserwowanych kopiach.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: stary blok → `GOV-HOST-MERGE-001` (warning, 0 błędów); uzgodniony blok, brak bloku, tekst poza blokiem i symlink → brak uwag.
- [x] AC-02: kod w `governance/diagnostics.json` z runbookiem (6 sekcji); kopia bundled identyczna; test podpięty w CI.

## Ryzyka i Uwagi
- Ostrzeżenie pojawi się u adopterów po aktualizacji standardu; nie blokuje bramek.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-363/`.

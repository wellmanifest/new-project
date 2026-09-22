# Ticket 263: Publish immutable standard release with multi-agent WIP capacity

- **ID**: ticket-263
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-22

## Cel i Zakres

Opublikować immutable `wellmanifest/new-project` 0.20.46 zawierający
podniesienie domyślnego limitu aktywnych ticketów workstreamu z 3 do 8,
aby równolegle mogły pracować profile Devin, Codex, Claude, Agy i podobne.
Wydanie obejmuje wyłącznie zsynchronizowanie `VERSION`, obu manifestów
kanonicznych i changeloga; nie zmienia lease, zakresów ani ochrony worktree.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `VERSION`, `manifest.default.json` i `manifest.hub.json` deklarują
      0.20.46, a changelog opisuje zmianę.
- [ ] AC-02: pełna bramka governance i testy adopcji przechodzą dla exact-head.
- [ ] AC-03: chroniony proces publikuje tag `v0.20.46` i finalny GitHub Release
      dopiero po scaleniu exact-head.

## Ryzyka i Uwagi
- Ryzyko niespójnych projekcji: mitygowane jednym diffem i walidacją wersji.
- Istniejących tagów nie wolno przesuwać; błąd wymaga kolejnego patch release.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-263/`.

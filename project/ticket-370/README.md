# Ticket 370: Project CI workflows are owned by the infrastructure workstream in the default manifest (issue 521)

- **ID**: ticket-370
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-22

## Cel i Zakres
Issue #521: w domyślnym manifeście żaden workstream nie posiadał
`.github/workflows/ci.yml` i innych workflow projektu, więc żaden ticket nie mógł
zmienić CI adoptera (GOV-WORK-START-001 „owned by no workstream”, dockuri#78).
`infrastructure` posiada teraz `.github/workflows/**`; workflow governance
zostają przy `governance`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: fixture z prawdziwym `manifest.default.json`: `ci.yml` i `release.yaml` przyjęte w `infrastructure`; workflow governance nadal w `governance`; `application` dostaje komunikat „owned by infrastructure”. Testy adoption-lock, bootstrap reusable plan, adoption upgrade, ticket allocation worktree, governance scripts i agent hosts przechodzą.
- [x] AC-02: wersja 0.20.117.

## Ryzyka i Uwagi
- Workflow governance są objęte przez oba workstreamy; ich zmiany nadal blokuje digest w locku (GOV-SYNC-001).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-370/`.

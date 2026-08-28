# Ticket 136: Enforce remote branch lifecycle in hub CI

- **ID**: ticket-136
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i zakres

Uruchamiać istniejący deterministyczny walidator remote branch lifecycle także
w CI samego huba `wellmanifest/new-project`. Obecnie walidator jest testowany i
używany przez adopterski reusable workflow, ale własny `ci.yml` sprawdza tylko
jego test jednostkowy, więc orphan branche nie blokują zielonego wyniku.

## Kryteria odbioru

- [ ] AC-01: każde uruchomienie `governance-standard-ci` pobiera ograniczony
  snapshot ustawienia `deleteBranchOnMerge`, branchy i otwartych PR.
- [ ] AC-02: istniejący `branch_lifecycle_check.py` blokuje orphan branch,
  brak wewnętrznego headu PR lub wyłączone automatyczne kasowanie po merge.
- [ ] AC-03: test regresyjny odrzuca usunięcie live wiring z `ci.yml`.

## Ryzyka

- Nowa bramka zablokuje publikację, jeśli pozostanie stary orphan branch;
  dlatego przed wdrożeniem branch inventory został sklasyfikowany, a zdalny
  stan doprowadzony do samego `main`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-136/`.

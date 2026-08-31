# Ticket 164: Project adopter checks from local workflows

- **ID**: ticket-164
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-31

## Cel i Zakres
Adopcja ma projektować deklarację wymaganych checków z workflow repozytorium
docelowego. Nie może pozostawiać dziedziczonej deklaracji CI standardu, bo ta
odwołuje się do workflow, którego pakiet nie instaluje.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Generator adopcji zastępuje odziedziczoną deklarację checków
  projekcją z workflow docelowego, również w trybie `--check`.
- [ ] AC-02: Adopter z samym zarządzanym workflow governance przechodzi
  deklarację required-checks bez odwołania do hubowego `ci.yml`.

## Ryzyka i Uwagi
- Risk 1: Repozytorium z własną deklaracją checków nie może zostać nadpisane;
  projekcja dotyczy wyłącznie jednoznacznie odziedziczonej deklaracji huba.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-164/`.

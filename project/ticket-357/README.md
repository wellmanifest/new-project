# Ticket 357: Package the pinned Policy DSL runtime for adopters (issue 479)

- **ID**: ticket-357
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-20

## Cel i Zakres
Naprawa issue #479: adopcja nie instalowała przypiętego runtime Policy DSL, a bramka
walidowała każdy `CONTRIBUTING.md` adoptera (`GOV-POLICY-DSL-001`). Pakiet instaluje
teraz checker i lock w ścieżkach deklarowanych przez lock, a bramka parsuje
`CONTRIBUTING.md` tylko gdy zawiera fence `dsl`.

Zakres rozszerzono po alokacji o `scripts/governance_check.py` i jego kopię bundled:
samo spakowanie runtime nie wystarcza, bo parser odrzuca dokument bez `DOCUMENT`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `package-manifest.json` instaluje `.governance/policy_dsl_check.py` i `.governance/policy-dsl.lock.json`.
- [x] AC-02: `CONTRIBUTING.md` bez fence `dsl` nie daje `GOV-POLICY-DSL-001`; fence przy brakującym runtime nadal fail-closed (`tests/policy_dsl_adoption_test.py`).

## Ryzyka i Uwagi
- Lease alokacji ma `scopeHash` z pierwotnego zakresu (lease advisory); rozszerzenie zakresu udokumentowane tutaj.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-357/`.

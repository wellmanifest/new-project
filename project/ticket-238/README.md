# Ticket 238: add common lockfiles to integration workstream and reconcile Policy DSL

- **ID**: ticket-238
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
1. Dodanie powszechnych plików lockfile (`uv.lock`, `poetry.lock`, `package-lock.json`, `Cargo.lock`, `go.sum`, `pnpm-lock.yaml`, `yarn.lock`) do `ownedPaths` oraz `requiredForPaths` workstreamu `integration` oraz do `delivery.dependencyManifestPaths` w `governance/manifest.default.json` (Issue #360).
2. Uspójnienie Policy DSL w `CONTRIBUTING.md` do wersji 24, dodanie jawnych tranzycji do `BLOCKED`, poprawa stanu `NEXT EDIT` w `C-LEASE-001`, oraz zamiana nielogicznego bloku `DONE WHEN` na reguły `C-DONE-001` i `C-DONE-002` zarejestrowane w `governance/rule-enforcement.json` i `dsl-manifest.json` (Issue #356).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/manifest.default.json` zawiera `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `uv.lock`, `poetry.lock`, `go.sum`, `Cargo.lock` w `coordination.workstreams.integration.ownedPaths`, `coordination.integration.requiredForPaths` oraz `delivery.dependencyManifestPaths`.
- [x] AC-02: `CONTRIBUTING.md` posiada poprawną składnię Policy DSL v1 (przechodzi `scripts/policy_dsl_check.py validate-markdown`).
- [x] AC-03: `governance/rule-enforcement.json` i `dsl-manifest.json` zawierają reguły `C-DONE-001` i `C-DONE-002` oraz zaktualizowane digesty SHA-256 (przechodzi `scripts/audit_rule_enforcement.py --require-complete`).
- [x] AC-04: `tests/rule-enforcement.test.sh` oraz `./project/governance-check.sh` zwracają PASS.

## Ryzyka i Uwagi
- Brak ryzyka dla środowiska wykonawczego — zmiany dotyczą wyłącznie kontraktów zarządczych i manifestów polityk.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-238/`.

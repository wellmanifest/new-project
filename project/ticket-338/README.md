# Ticket 338: Adopt wellmanifest/semver standard pack and embedded-fleet profile

- **ID**: ticket-338
- **Owner**: agent:gemini
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-13

## Cel i Zakres
Związanie standardu `wellmanifest/semver` w ekosystemie `wellmanifest/new-project`:
1. Rejestracja pakietu standardu `wellmanifest/semver` w `governance/standard-packs.json` oraz powiązanie profilu `embedded-fleet`.
2. Utworzenie vendored projekcji `subprojects/semver/` związanej lockiem `governance/semver.lock.json` ze skrótami SHA-256 każdego artefaktu (schematy, policy, conformance, README).
3. Dodanie referencji do standardu w `template/files/AGENTS.template.md` oraz `AGENTS.md`.
4. Dodanie testu weryfikacyjnego adopcji `tests/semver-adoption.test.py` oraz wpięcie do `tests/standard-pack-check.test.sh`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/standard-packs.json` rejestruje pack `wellmanifest/semver` i włącza go do profilu `embedded-fleet`.
- [x] AC-02: `governance/semver.lock.json` wiąże dokładne skróty SHA-256 artefaktów z HEAD repozytorium `wellmanifest/semver`.
- [x] AC-03: `subprojects/semver/` zawiera spójną vendored projekcję standardu (schematy JSON, POLICY.md, dsl-manifest, conformance.py, policy.json, README.md).
- [x] AC-04: Test `tests/semver-adoption.test.py` weryfikuje integralność locka i artefaktów oraz przechodzi w `tests/standard-pack-check.test.sh`.
- [x] AC-05: `AGENTS.md` i `template/files/AGENTS.template.md` zawierają link do `embedded-release.schema.json`.

## Ryzyka i Uwagi
- Risk 1: Rozbieżność sum kontrolnych (digest drift) między repozytorium źródłowym a projekcją w new-project.
  - Mitygacja: lockfile wiąże dokładne sumy SHA-256 artefaktów oraz rewizję źródłową `wellmanifest/semver` i jest automatycznie walidowany przez `tests/semver-adoption.test.py`.

## Granica katalogu
Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Kod wykonywalny, skrypty i testy należą do zwykłych katalogów źródłowych, nie do `project/ticket-338/`.

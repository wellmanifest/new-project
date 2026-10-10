# Ticket 327: enforce version parity across VERSION, manifests and code

- **ID**: ticket-327
- **Owner**: agent:gemini
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-10

## Cel i Zakres
Zapewnienie spójności i niezmienności deklaracji wersji w ekosystemie projektów zarządzanych przez `wellmanifest/new-project`:
1. Wdrożenie deterministycznej walidacji `GOV-VERSION-001` w bramce `scripts/governance_check.py`, weryfikującej zgodność pliku `VERSION` z deklaracjami w manifestach pakietów (`pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`) oraz kodzie źródłowym (`__init__.py`).
2. Rozszerzenie `governance/diagnostics.json` oraz stworzenie dokumentacji `error/GOV-VERSION.md`.
3. Aktualizacja `governance/rule-enforcement.json` łącząca `GOV-VERSION-001` z regułą normatywną `P-CORE-027`.
4. Dodanie `setup.py` i `setup.cfg` do `coordination.workstreams.integration` w `governance/manifest.default.json`, aby workstream integracyjny miał uprawnienia do synchronizacji wszystkich deklaracji wersji.
5. Aktualizacja szablonu `template/projects/python-package.template.md`, aby promował dynamiczne czytanie wersji zamiast zahardkodowanego literału `__version__ = "0.1.0"`.
6. Dodanie testu weryfikacyjnego `tests/version-parity.test.sh`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `scripts/governance_check.py` zawiera funkcję `check_version_parity` sprawdzającą spójność deklaracji wersji z `VERSION` i emitującą `GOV-VERSION-001` przy wykryciu rozjazdu.
- [x] AC-02: `governance/diagnostics.json` definiuje kod `GOV-VERSION-001`, a `error/GOV-VERSION.md` zawiera runbook i opis reguły.
- [x] AC-03: `governance/rule-enforcement.json` mapuje `GOV-VERSION-001` na regułę `P-CORE-027`, a `audit_rule_enforcement.py` i `audit_diagnostics.py` przechodzą bez błędów.
- [x] AC-04: `governance/manifest.default.json` przypisuje `setup.py` i `setup.cfg` do workstreamu `integration`.
- [x] AC-05: Szablon `template/projects/python-package.template.md` nie zawiera hardkodowanego `__version__ = "0.1.0"`.
- [x] AC-06: Nowy test `tests/version-parity.test.sh` weryfikuje wykrywanie niespójności wersji przez bramkę governance.

## Granica katalogu
Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Kod wykonywalny, skrypty i testy należą do zwykłych katalogów źródłowych, nie do `project/ticket-327/`.

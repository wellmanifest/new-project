# ticket-318: Standardize default workstreams and configurable delivery profile XS timebox

- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Cel i Zakres
1. Dodanie standardowych ścieżek narzędziowych i dokumentacyjnych (`.reuse/**`, `.redup/**`, `.benchmarks/**`) do strumienia `governance` oraz `OVERVIEW.md` do strumienia `integration` w `governance/manifest.default.json`. Zapobiega to błędom `GOV-WORKSTREAM-003` podczas adopcji standardu reuse, generowania pokwitowań redup oraz tworzenia specyfikacji v2 w root.
2. Zezwolenie na konfigurację limitu czasu `maxActiveMinutes` dla profilu `XS` w `governance_check.py` z zachowaniem wstecznie kompatybilnego domyślnego limitu 10 minut, gdy profil nie deklaruje wartości.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `manifest.default.json` rejestruje `.reuse/**`, `.redup/**`, `.benchmarks/**` w `governance` oraz `OVERVIEW.md` w `integration`.
- [x] AC-02: `governance_check.py` czyta `maxActiveMinutes` z profilu przed fallbackiem do domyślnego limitu 10 minut.
- [x] AC-03: Pełny zestaw testów oraz walidacja `project/governance-check.sh` kończy się sukcesem (PASS).

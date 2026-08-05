# Ticket Changelog (ticket-010)

## [0.1.0] - 2026-08-04

- Utworzono plan kontraktu pakietu i meta-walidacji.
# Ticket 010 changelog

- Dodano wersjonowany `governance/package-manifest.json` jako źródło prawdy dla adopcji.
- Generator pobiera kontrakt i wszystkie artefakty z tego samego pełnego SHA.
- Dodano negatywne przypadki brakującego źródła i zduplikowanego celu.
- Dodano meta-walidację Draft 2020-12 i walidację przykładowych dokumentów.
- Testy `adoption-lock` i `governance-validator` zakończyły się wynikiem PASS.
- Pełna lokalna regresja obejmująca `governance-scripts`,
  `governance-validator`, `adoption-lock`, kontrolę JSON i `git diff --check`
  zakończyła się wynikiem PASS.

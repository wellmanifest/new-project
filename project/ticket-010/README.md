# Ticket 010: Manifest pakietu i meta-walidacja schematów

- **ID**: ticket-010
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-04

## Cel i zakres

Zastąpić ryzyko ręcznie utrzymywanej listy artefaktów wersjonowanym kontraktem
pakietu oraz walidować schematy Draft 2020-12 i przykładowe dokumenty w CI.

## Kryteria odbioru

- [x] Jedno źródło prawdy wymienia wszystkie zarządzane artefakty.
- [x] Test odrzuca brakujący lub nadmiarowy artefakt.
- [x] Schematy przechodzą meta-walidację Draft 2020-12.
- [x] Przykładowe manifesty, locki, intencje i evidence są walidowane.

## Stan publikacji

Implementacja jest gotowa do walidacji i publikacji. Status `DONE` wymaga
zaufanego approval powiązanego z dokładnym SHA brancha/PR.

## Walidacja

- `bash tests/adoption-lock.test.sh` - PASS
- `bash tests/governance-validator.test.sh` - PASS

# Ticket 010: Manifest pakietu i meta-walidacja schematów

- **ID**: ticket-010
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
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

PR #10 przeszedł chronione CI oraz approval Validator App dla dokładnego HEAD
`9f52b2c6654d5035f70cc4616c3c4c5601dcc281` i został scalony do `main` jako
`956f3505d329aca4934da9857f5a060f0a62dc60`.

## Walidacja

- `bash tests/adoption-lock.test.sh` - PASS
- `bash tests/governance-validator.test.sh` - PASS

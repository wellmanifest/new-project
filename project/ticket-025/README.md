# Ticket 025: CI uruchamia test governance-env

- **ID**: ticket-025
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-05

## Cel i zakres

`tests/governance-env.test.sh` istnieje, przechodzi i chroni
`scripts/governance_env.py` z ticketu 020 — ale **nie uruchamia go żaden
workflow**. `ci.yml` wymienia cztery zestawy z pięciu obecnych.

To ta sama klasa błędu, którą zamykały tickety 018 i 021: lista zakresu jest
przepisana ręcznie i przestaje nadążać za rzeczywistością. Tam był to scaffolder
i alokacja numerów, tu lista kroków w CI.

## Wdrożone

- `ci.yml` uruchamia `tests/governance-env.test.sh`.
- Dodany krok **weryfikujący samą listę**: dla każdego `tests/*.test.sh`
  sprawdza, czy w `ci.yml` istnieje odpowiadający krok `bash <suite>`.
  Brakujący zestaw kończy job błędem z nazwą pliku.

Krok celowo czyta katalog i porównuje z workflow, zamiast trzymać drugą listę.
Lista pozostaje ręczna — bo kolejność i nazwy kroków mają znaczenie dla czytelności
— ale jej **kompletność jest już maszynowo egzekwowana**.

## Kryteria odbioru

- [x] AC-01: `tests/governance-env.test.sh` jest uruchamiany przez `ci.yml`.
- [x] AC-02: Zestaw obecny w `tests/`, a nieobecny w `ci.yml`, zatrzymuje job.
- [x] AC-03: Komunikat wskazuje konkretny brakujący plik.
- [x] AC-04: Pozostałe zestawy regresyjne przechodzą.

## Dowód wykonania

- Strażnik na bieżącym drzewie: `missing=0`.
- Mutacja — usunięcie kroku `governance-env`: `caught: tests/governance-env.test.sh`,
  `missing=1`. Po przywróceniu ponownie `0`.
- `bash tests/governance-env.test.sh` — `governance environment runtime tests passed`.

## Poza zakresem

- `windows-governance.test.ps1` nie jest objęty strażnikiem; ma inny interpreter
  i osobny job. Rozszerzenie na `.ps1` wymagałoby innego dopasowania i jest
  osobnym rozstrzygnięciem.

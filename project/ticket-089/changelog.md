# Ticket Changelog (ticket-089)

## [0.1.0] - 2026-08-16

- Initial governance scaffold created.
- No human participant identity or content was generated.

## [0.2.0] - 2026-08-16

- Implementacja przygotowana i zweryfikowana poza repozytorium; ticket pozostaje
  BLOCKED, więc nie została zapisana do drzewa roboczego.
- Zakres łatek: `scripts/check_required_checks.py` (+270), `tests/required-checks.test.sh`
  (+97), `scripts/governance_check.py` (+57), `governance/package-manifest.json` (+12),
  nowy `governance/required-checks.schema.json` (89 linii).
- Test rozszerzony o syntetycznego adoptującego materializowanego z
  `package-manifest.json`. Trzy nowe przypadki: układ `.governance/` z dwoma
  workflow i nadpisanym `name:` przechodzi; klucz joba zamiast nazwy
  wyświetlanej jest odrzucany; instancja z odziedziczonymi wartościami hubu
  jest odrzucana.
- Regresja hubu: brak. Istniejące przypadki testowe przechodzą bez zmian.

## [0.3.0] - 2026-08-16

- Zapisano ograniczenie kolejności: `subactor/validator-agent` czyta
  `governance/required-checks.json` ścieżką hubu, więc u 22 adoptujących plik
  nie jest znajdowany i walidator spada na rejestr. Fałszywa deklaracja jest
  dziś nieszkodliwa wyłącznie dzięki temu drugiemu błędowi ścieżki.
- Wynika z tego, że `REQUIRED_CHECKS_PATH` wolno przestawić dopiero po
  uzupełnieniu i zweryfikowaniu instancji. Zmiana samej ścieżki zamieniłaby
  nieszkodliwą deklarację w blokadę publikacji w 21 repozytoriach.

## [0.4.0] - 2026-08-16

- Zapisano implementację: `required-checks.json` jest `extendable`, schemat
  instancji jest `managed`, bramka szuka pliku obok skryptu i czyta `name:`
  joba, `governance_check.py` wywołuje bramkę, a lock adoptujący nie traktuje
  drugiej pary extendable jak manifestu z bazą zarządzaną.
- AC-01–AC-06 zweryfikowane; `tests/required-checks.test.sh`,
  `tests/adoption-lock.test.sh` i `tests/governance-validator.test.sh` zielone.

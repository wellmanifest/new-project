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

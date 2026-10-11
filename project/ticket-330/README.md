# Ticket 330: bump release version projection to 0.20.92

- **ID**: ticket-330
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-11

## Cel i Zakres
Podbicie deklaracji wersji wydania standardu `wellmanifest/new-project` oraz narzędzia `wellman` do `0.20.92` z zachowaniem pełnej spójności (version parity) dla zmian włączonych w PR #467 (adopcja `session-recovery`), PR #468 (`GOV-VERSION-001`) i PR #469 (automatyczne ignorowanie artefaktów budowania pakietów).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Wersja w `VERSION`, `packages/wellman/pyproject.toml`, `governance/manifest.hub.json` oraz `governance/manifest.default.json` została zaktualizowana atomowo do `0.20.92`.
- [x] AC-02: Weryfikacja spójności wersji przez `tests/version-parity.test.sh` i walidację schematów przechodzi pomyślnie.
- [x] AC-03: Skrypt `./project/governance-check.sh` przechodzi bez błędów i bez ostrzeżeń (`GOV-PASS`).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-330/`.

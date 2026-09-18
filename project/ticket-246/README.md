# Ticket 246: establish canonical schema host and schema immutability governance

- **ID**: ticket-246
- **Owner**: agent
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres

Ustanowienie kanonicznego hosta schematów `https://wellmanifest.com/schemas/` dla całej floty Wellmanifest,
zdefiniowanie reguł routingu przestrzeni nazw i aliasów wstecznej kompatybilności dla starszych schematów
(`wellmanifest.dev`, `wellmanifest.org`, `github.com`, `urn:`), a także formalne utrwalenie zasady
niezmienności semantycznej schematów (schema immutability invariant) zamykając Issue #348:

1. Każda zmiana semantyki walidacji schematu wymaga podniesienia wersji identyfikatora dokumentu (`new-project.intent/v4`) lub adresowania treścią/rewizją – zakaz mutowania semantyki in-place pod tym samym `$id` i wersją.
2. Zdefiniowanie okna wspieranych wersji pakietu (`new-project >= 0.20.0`, maintenance `0.18.10`).
3. Zapisanie formalnej decyzji SSOT w `governance/canonical-schema-hosts.ssot.json` wg schematu `wellmanifest.ssot/decision/v1`.
4. Dodanie testu weryfikacyjnego `tests/canonical-schema-hosts.test.py` (4/4 PASS).

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Ustanowienie kanonicznego hosta `https://wellmanifest.com/schemas/` i opisanie routingu w `docs/information/canonical-schema-hosts.md`.
- [x] AC-02: Dokument decyzji SSOT `governance/canonical-schema-hosts.ssot.json` jest poprawny z zerem findings w walidatorze SSOT.
- [x] AC-03: `python3 tests/canonical-schema-hosts.test.py` przechodzi (4/4 testów OK).
- [x] AC-04: Zasada niezmienności semantycznej schematów zabezpiecza flotę przed cichą dywergencją reguł pod identycznym `$id`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-246/`.

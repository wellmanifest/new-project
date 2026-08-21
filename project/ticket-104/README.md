# Ticket 104: Reject trailing whitespace in managed text artifacts

- **ID**: ticket-104
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-21

## Cel i Zakres

Usunąć trailing whitespace dostarczany obecnie do każdego adoptera w
zarządzanym `AGENTS.md` i dodać regresję skanującą wszystkie źródła pakietu o
strategii `managed` lub `extendable`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Źródłowy `AGENTS.template.md` nie zawiera trailing whitespace.
- [x] AC-02: Test hostów odrzuca trailing whitespace w dowolnym zarządzanym lub
  rozszerzalnym źródle wymienionym w `governance/package-manifest.json`.
- [x] AC-03: Pełny zestaw testów, Ruff, governance i `git diff --check`
  przechodzą bez błędów.
- [ ] AC-04: Validator-agent zatwierdza dokładny head PR i scala zmianę.

## Ryzyka i Uwagi
- Risk: skan mógłby objąć plik binarny; aktualny manifest zawiera wyłącznie
  tekstowe źródła kontraktu, a test raportuje dokładną ścieżkę i linię.

## Validation evidence

- Red test przed poprawką: `template/files/AGENTS.template.md:82`.
- 11/11 `tests/*.test.sh`: PASS.
- Ruff oraz `git diff --check`: PASS.
- Exact-base governance od `7bed5902`: 0 errors, 0 warnings.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-104/`.

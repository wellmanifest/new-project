# Ticket 093: Governance-check wrappers work on hub and adopter layouts

- **ID**: ticket-093
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-19

## Cel i Zakres

`project/governance-check.sh` i `.bat` zakładają układ adoptera
(`.governance/governance_check.py`). Na hubie `wellmanifest/new-project`
ten plik nie istnieje; skrypt musi użyć `scripts/governance_check.py` i
manifestu w `governance/`.

Zakres: trzy pliki wrappera/loadera. Nie otwieramy ticket-089.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Na hubie wrapper wywołuje `scripts/governance_check.py`.
- [x] AC-02: Na adopterze wrapper nadal wywołuje `.governance/governance_check.py`.
- [x] AC-03: Loader work-classification znajduje `governance/work-classification.dsl.json`, gdy brak pliku w `.governance/`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-grok.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny
należy do `project/governance-check.*` i `scripts/governance_check.py`.

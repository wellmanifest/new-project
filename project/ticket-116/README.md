# Ticket 116: Document GOV-INTENT runbook in diagnostics

- **ID**: ticket-116
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-24

## Cel i Zakres
Provide comprehensive runbook documentation for the `GOV-INTENT` diagnostic family (`GOV-INTENT-001`, `GOV-INTENT-002`, `GOV-INTENT-003`) in `error/GOV-INTENT.md` and link it in `governance/diagnostics.json`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `error/GOV-INTENT.md` documents meaning, safe resolution, and verification for `GOV-INTENT-001`–`GOV-INTENT-003`.
- [x] AC-02: `governance/diagnostics.json` links `documentation: "error/GOV-INTENT.md"` for `GOV-INTENT-001`, `002`, `003`.
- [x] AC-03: Governance checks pass with 0 errors and 0 warnings.

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-antigravity.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-116/`.

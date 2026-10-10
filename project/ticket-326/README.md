# Ticket 326: adopt wellmanifest/session-recovery standard pack

- **ID**: ticket-326
- **Owner**: agent:gemini
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-10

## Cel i Zakres
Związanie standardu `wellmanifest/session-recovery` w ekosystemie `wellmanifest/new-project`:
1. Rejestracja pakietu standardu `wellmanifest/session-recovery` w `governance/standard-packs.json` z profilem wymagań.
2. Utworzenie vendored projekcji `subprojects/session-recovery/` związanej lockiem `governance/session-recovery.lock.json` ze skrótami SHA-256 każdego artefaktu.
3. Dodanie referencji do standardu w `template/files/AGENTS.template.md` oraz `AGENTS.md`.
4. Dodanie testu weryfikacyjnego adopcji `tests/session-recovery-adoption.test.py`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `governance/standard-packs.json` rejestruje pack `wellmanifest/session-recovery` i włącza go do profilu `agent-executor`.
- [x] AC-02: `governance/session-recovery.lock.json` wiąże dokładne skróty SHA-256 artefaktów z HEAD repozytorium `wellmanifest/session-recovery`.
- [x] AC-03: `subprojects/session-recovery/` zawiera spójną vendored projekcję standardu (schema, policy, conformance, readme).
- [x] AC-04: Test `tests/session-recovery-adoption.test.py` weryfikuje integralność locka i artefaktów.
- [x] AC-05: `AGENTS.md` i `template/files/AGENTS.template.md` zawierają link do `session-recovery.schema.json`.

## Granica katalogu
Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Kod wykonywalny, skrypty i testy należą do zwykłych katalogów źródłowych, nie do `project/ticket-326/`.

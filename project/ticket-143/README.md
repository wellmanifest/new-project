# Ticket 143: Durable ignored targets and CI host bootstrap

- **ID**: ticket-143
- **Owner**: codex
- **GitHub issue**: #244
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Goal and scope

Close three adoption/CI gaps found by the live Koru pilot: ignored managed
targets must be rejected before adoption, the pytest bridge must activate the
delivered Git hook in a fresh clone, and GitHub pull-request runs must resolve
the exact base SHA even when checkout is shallow.

## Acceptance criteria

- [x] AC-01: adoption reports every ignored managed target and performs no writes.
- [x] AC-02: pytest governance activates the declared hook before the gate.
- [x] AC-03: a shallow GitHub PR fixture uses the event base SHA and changed paths.
- [x] AC-04: focused and full deterministic Linux suites pass.

## Risk

Automatic lifecycle activation may mutate clone-local Git configuration. It is
bounded to the hook path declared in the installed contract and never changes
tracked content or the index.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-143/`.

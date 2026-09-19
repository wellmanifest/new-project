# Ticket 248: Skip pytest governance for collect-only probes

- **ID**: ticket-248
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-19

## Goal and scope

The managed pytest governance bridge currently executes the repository gate
even for `pytest --collect-only`. Collection is a read-only inventory operation
used by project discovery and IDEs; it must not execute a gate, resolve Git
state, or fail because a target does not have a gate script. Sessions capable
of executing tests retain the existing fail-closed gate behavior.

SESSION_EXECUTION_AUTHORIZATION: the user requested continuation after the
Koru pilot showed that this correction belongs at the `wellmanifest/new-project`
HOME rather than in an adopter.

## Acceptance criteria

- [ ] AC-01: A collect-only pytest session returns before gate and Git
      resolution, including when no gate script exists.
- [ ] AC-02: A non-collect pytest session continues to invoke the gate and
      propagates a negative verdict.
- [ ] AC-03: The managed pytest-plugin regression suite and governance gate
      pass.
- [ ] AC-04: The managed payload version advances with an entry describing the
      corrected behavior.

## Risk

The exemption must be strictly limited to pytest's `collectonly` option. The
regression fixture covers both the early-return path and ordinary enforcement.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-248/`.

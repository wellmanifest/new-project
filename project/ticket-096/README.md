# Ticket 096: Keep the overlap guard reachable after terminal pre-commit success

- **ID**: ticket-096
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-20

## Cel i Zakres

Fix `scripts/install-worktree-guard.sh` so `--wire-hook` keeps the generated
overlap fragment reachable when an existing pre-commit hook ends with a
terminal `exit 0`. The installer currently appends after that command, making
the guard dead code while reporting successful wiring.

The change is limited to the installer and its existing end-to-end regression
suite. Existing non-terminal hooks retain append-last behavior; a terminal
success exit is moved after the chained guard call without interpreting or
rewriting any other hook logic.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: The autonomous repair request is recorded as bounded session
      authorization without creating a human-owned participant file.
- [ ] AC-02: Wiring a pre-existing hook whose last effective command is
      `exit 0` places exactly one guard invocation before that exit.
- [ ] AC-03: A real overlapping commit is rejected through that composed hook;
      a disjoint commit and repeated installation remain successful/idempotent.
- [ ] AC-04: Existing created-hook, custom `core.hooksPath`, workspace and
      merge-based overlap fixtures remain green on Linux and Windows gates.
- [ ] AC-05: Governance, the focused overlap suite and the complete hub test
      contract pass before exact-head Validator review.

## Ryzyka i Uwagi

- Only a final effective line equal to `exit 0` is relocated. The installer
  does not attempt to parse arbitrary shell control flow or bypass deliberate
  early exits.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-096/`.

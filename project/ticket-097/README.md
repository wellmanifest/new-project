# Ticket 097: Repair previously unreachable worktree hook chains

- **ID**: ticket-097
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-20

## Cel i Zakres

Extend the authoritative worktree-guard installer so re-running it repairs the
legacy composition emitted before ticket-096: one standard guard invocation
appears after a terminal `exit 0` and is therefore unreachable. New installs
are already correct; this ticket adds the bounded migration path required by
existing adopters such as `subactor/core`.

The installer may relocate only the exact legacy suffix: one effective guard
call is the final command and its previous effective command is exactly
`exit 0`. Other existing calls remain byte-stable and no arbitrary shell flow
is interpreted.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Bounded session authorization and the dependency on integrated
      ticket-096 are recorded without human-owned content.
- [ ] AC-02: Re-running `--wire-hook` relocates exactly one known legacy guard
      suffix before terminal `exit 0` and reports the repair.
- [ ] AC-03: Correctly wired hooks and non-legacy existing calls remain
      idempotent and byte-stable.
- [ ] AC-04: The focused real-commit fixture, all hub suites, Bash syntax and
      exact-base governance pass before protected publication.

## Ryzyka i Uwagi

- The installer must not infer reachability for arbitrary early exits. The
  migration is restricted to the exact suffix previously emitted by this
  standard and fails closed to "left unchanged" outside that shape.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-097/`.

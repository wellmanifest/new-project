# Ticket 125: Recover declared managed targets missing from accepted base

- **ID**: ticket-125
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-25

## Cel i Zakres

Allow an atomic standard upgrade to restore a target that the accepted base
package and lock both declared as `managed`, but whose accepted Git tree proves
the file was absent. Recovery must be explicit, exact-path, exact-base-digest,
upgrade-only and consumed exactly once. Existing target bytes must remain
ineligible for this recovery path.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `standardAdoption` accepts only a strict optional
  `managedTargetRestorations[{path,baseDigest}]` contract on upgrades.
- [x] AC-02: A declaration passes only when the base package and lock declare
  the path as managed, the accepted Git base lacks it, `baseDigest` equals the
  base lock, and the restored head bytes equal the new lock.
- [x] AC-03: Missing, wrong, duplicate, unused and existing-base declarations
  fail closed; undeclared missing managed targets keep returning `GOV-SYNC-001`.
- [x] AC-04: Full deterministic tests, syntax checks and exact-base governance
  pass.
- [x] AC-05: The exact PR head is independently approved and merged through
  Validator; release remains a separate bounded ticket.

## Ryzyka i Uwagi

- Risk: a broad exception could conceal repository corruption. Mitigation:
  exact accepted-base absence, both old/new managed declarations, old lock
  digest equality, new lock content equality and mandatory one-time use.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-125/`.

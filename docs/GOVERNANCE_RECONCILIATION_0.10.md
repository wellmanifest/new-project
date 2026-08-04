# Governance reconciliation 0.10.0

## Why 0.10.0 exists

Two commits described different public contracts as `0.9.0`:

- `main@c0bb63e` introduced immutable adoption provenance and made only
  `IN_PROGRESS` reserve a workstream and write scope;
- `feat/bounded-delivery-contract@1ae86a1` introduced architecture-first,
  maximum-30-minute delivery contracts, but retained the older active-status
  behavior.

Copying either tree wholesale would discard a protection supplied by the
other. Version 0.10.0 is the first canonical contract containing both sets of
behavior. It was assembled from reviewed capabilities, not by merging either
branch over the other.

## Effective lifecycle

`IN_PROGRESS` is the only active reservation. `BACKLOG`, `PLAN` and `BLOCKED`
are valid non-active states. They remain visible and schema-checked, but do not
produce active-ticket conflict, unfinished-dependency, ownership or overlap
diagnostics. Misspelled and undeclared states still fail with
`GOV-STATUS-001`.

This distinction prevents plans waiting for approval or external coordination
from deadlocking an unrelated implementation. It does not weaken protection
for concurrent `IN_PROGRESS` work: workstream limits, dependency/conflict
edges, owned paths and concrete/pattern overlap remain fail-closed.

## Bounded delivery

An implementation intent records one outcome, accepted base SHA, target
branch, non-goals, `XS|S` complexity, no more than 30 active minutes and a
checkpoint before the limit. Architecture, rollback and explicit budgets are
decided before `EDIT`. A stale base, unresolved architecture, extra outcome or
budget overflow stops the slice; it does not silently broaden approval.

The default contract permits at most five implementation files and two
affected components. A larger shared-contract migration requires an explicit,
human-approved integration ticket and must preserve the same deterministic
evidence.

## Adoption

1. Review and publish one exact commit containing version 0.10.0.
2. Run `scripts/create_adoption_lock.py --check` against that full SHA.
3. Review the managed-file plan and local-manifest compatibility.
4. Run the explicit upgrade and verify every SHA-256 lock entry.
5. Compare target diagnostics and execute its deterministic and stack tests.

Branch names, abbreviated SHAs and `remote-branch` provenance are insufficient
for final adoption. The target lock must identify the full reviewed commit with
`publicationStatus: published`.

Rollback is non-destructive: retain or restore the previous exact lock and
managed artifacts. The generator refuses unreviewed local drift instead of
overwriting it.

## LLM boundary

Governance validation has no network or LLM dependency. Model findings may be
advisory evidence, but an agent or model cannot self-approve. Target-specific
model choices, including cost-driven replacements, belong to the target
workflow and do not change this contract.

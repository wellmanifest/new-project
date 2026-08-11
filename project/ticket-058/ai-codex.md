---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-058
---
# Participant: codex (AI agent)

## Understanding

The package has a safe write-time conflict guard, but its ownership model still
makes adoption impossible for repositories whose established automation uses
the generic root `project.sh` name. `hillm` reproduces the deferred ticket-024
case exactly: preflight reports `UPDATE project.sh`, and accepting the package
would replace 139 lines with a 38-line governance convenience wrapper. The
canonical managed gate already has a collision-resistant path under `project/`,
so the root aliases do not need managed ownership.

## Execution plan

1. Reclassify only the two root aliases as seed package entries.
2. Add adoption fixtures for an existing custom pair and a newly seeded pair,
   including lock and idempotence assertions.
3. Point target and hub agent instructions plus Goal adoption docs to the
   canonical managed gate.
4. Run focused and complete Linux contracts plus changed-surface static checks.
5. Re-run exact-SHA Goal adoption on a clean `hillm` pilot and its native tests.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Captured `hillm` baseline: 81 tests pass, 7 skip; its existing Ruff contract
  has 77 pre-existing violations and the tracked tree remains clean.
- Exact candidate `44026dc` preflight is read-only but reports
  `UPDATE project.sh` and missing target-owned `project/TICKETS.md`.
- Verified target and standard wrappers differ materially (139 versus 38
  lines), while ticket 024 already records the same unresolved collision in a
  second downstream repository.
- Changed only the two root aliases to seed strategies; the canonical gates
  remain managed and target instructions now distinguish the boundary.
- Added collision-preservation, absent-seed, local-extension, lock-membership
  and upgrade regressions. Focused tests and the complete Linux CI contract
  pass on implementation `98c403c`.
- Repeated exact-SHA Goal adoption on fresh `hillm`: preflight became 25
  creates with no collision, adoption needed no upgrade, and the original
  script hash/mode stayed unchanged.
- Verified explicit/inferred/canonical governance gates pass, Python remains
  Docker-free, and native tests plus the known Ruff baseline do not regress.
- Recorded but did not mix in a pre-existing product-test event-ledger side
  effect; removed only the rows produced by this validation from both clones.
- Completed the bounded repair locally without external delivery.

## Blockers

- None inside the recorded intent.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.

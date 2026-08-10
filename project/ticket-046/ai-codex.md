---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-046
---
# Participant: codex (AI agent)

## Understanding

The 0.14.0 migrator verifies the legacy target manifest against its installed
lock, but then discards that authenticated document and reconstructs the old
base from the standard repository default. A valid Goal manifest customized
under the earlier fully-managed contract therefore fails the new extension
check. The safe base is the exact locked target projection: it is already the
content whose integrity the old lock establishes.

The current user request also explicitly authorizes autonomous execution.
The standard currently confuses execution authorization with protected merge
approval and therefore asks twice for the former. The safe correction is to
derive bounded session authorization from a user request that already says to
execute, while keeping destructive, secret, external-coordination and trusted
merge authority outside that derivation.

## Execution plan

1. Record this explicit execution/autonomy authorization and the expanded
   bounded machine intent.
2. Align hub and managed agent policy so an execution request does not cause a
   redundant confirmation pause, without weakening hard safety or merge trust.
3. Add a failing Goal-shaped legacy migration fixture with target-owned
   workstreams and absent fields introduced by the pristine standard default.
4. Select the verified legacy target projection as the previous base while
   preserving all existing hash and structural checks.
5. Run focused mutations, the full Linux contract and diff/security review.
6. Publish one PR, wait for Linux/Windows and exact-head Validator approval,
   then merge without creating a release tag.

## Actual changes

- Reproduced the failure without modifying target repositories.
- Made the authenticated installed legacy target projection the previous base;
  historical pristine defaults are no longer reconstructed.
- Added a Goal-shaped unavailable-revision migration and tampered-hash negative
  fixture while retaining fresh and extendable upgrade coverage.
- Replaced unconditional confirmation pauses with bounded session execution
  authorization in hub policy, procedure and both agent instruction surfaces.
- Preserved separate authority for destructive/out-of-scope actions and the
  external exact-head trusted merge contract.
- Passed the focused regression and full maintained Linux hub contract.
- Published through Goal 2.1.289 as PR #73; Linux, Windows and the independent
  Validator App approved exact HEAD `20a450b`, merged as `main@cc898c1`.

## Authorization boundary

- The current request authorizes implementation inside this intent.
- It does not authorize destructive/out-of-scope operations, secret access,
  force push or treating agent-authored evidence as trusted merge approval.

## Acceptance evidence plan

- AC-01..AC-04: focused adoption fixtures and negative hash mutations.
- AC-05: exact Goal-shaped fixture plus complete fail-fast Linux contract.
- AC-06: protected GitHub checks and current-head Validator App review.
- AC-07..AC-09: semantic assertions over hub and managed agent contracts.

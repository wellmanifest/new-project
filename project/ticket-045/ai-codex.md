---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-045
---
# Participant: codex (AI agent)

## Understanding

The user wants publication to consistently use `goal -a` and asked to continue
the planned work after the audit showed that `new-project` does not currently
require it. The standard must not turn `goal -a` into a bypass around its own
PR, exact-head approval and immutable-release rules.

The available Goal implementation already defines governed delivery modes:
`direct-main`, `publish-only` and `pull-request`. The safe default for an
implementation change is `pull-request` combined with `--no-publish`. Registry
or release side effects belong to a later, trusted merge-bound phase.

The system-installed Goal and the repository virtualenv both report 2.1.284,
but only the repository build exposes `--delivery-mode`. Therefore the
standard must require a capability probe in addition to any version pin.

## Execution plan

1. Add stable `C-PUBLISH-*` rules for governed Goal delivery and phase
   separation.
2. Update the immutable release runbook without rewriting historical evidence.
3. Map every new rule to deterministic or explicitly manual enforcement.
4. Add regression checks for the required Goal invocation, feature probe,
   pull-request-only implementation delivery and server-side trust boundary.
5. Run the full hub test contract and review the exact five-file
   implementation diff.

## Actual changes

- Created the ticket plan and bounded machine intent only.
- Recorded the user's 2026-08-09 continuation as interactive implementation
  authorization and entered `IN_PROGRESS / EDIT`.
- Added phase-separated Goal publication rules `C-PUBLISH-005..008`.
- Added the managed Goal release runbook while retaining the historical
  `v0.10.0` procedure as immutable evidence.
- Added complete enforcement mappings and a semantic regression test.
- Used four implementation files, one below the approved budget.
- Entered `IN_PROGRESS / VALIDATION` after the full Linux hub contract passed.
- Repeated the entire Linux CI contract under `set -euo pipefail` with the
  workflow-pinned `jsonschema==4.25.1`; all suites passed.
- Verified published Goal 2.1.289 exposes `--delivery-mode` and resolves the
  repository policy to governed `pull-request` mode with server enforcement.
- Corrected the planned command after the probe proved `--ticket` must follow
  the explicit `push` subcommand while root `-a` still enables the full
  workflow; intent/branch/PR provide additional ticket binding.

## Blockers

- Publishing this ticket or a dependent immutable release is outside the
  current plan and requires the existing PR/release gates.
- Windows and trusted exact-head validation are available only after a PR is
  published; they are not claimed locally.

## Acceptance evidence plan

- AC-01/AC-02: normative rule text plus focused shell assertions.
- AC-03: explicit feature-probe rule and negative regression.
- AC-04: release runbook diff preserving historical release records.
- AC-05: complete rule-enforcement audit and full Linux hub contract.

## Validation result

- AC-01..AC-05: satisfied locally.
- Eight Linux test suites: PASS.
- Rule count/mapping completeness: PASS.
- Docker Engine: available, server 29.1.3.
- Windows/exact-head protected evidence: not run locally.
- Publication is authorized by the user's 2026-08-10 instruction and will use
  Goal 2.1.289 in `pull-request --no-publish` mode.

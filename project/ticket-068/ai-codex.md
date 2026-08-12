---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-068
---
# Participant: codex (AI agent)

## Understanding

The remediation-intent DSL from ticket 067 is merged but not present in an
immutable release. During the v0.15.0 work, public Goal generated a 523-line
`goal.yaml` for `new-project-ticket-065`, including PyPI/npm configuration and
enabled Python/Node.js/Rust publishing. That file was outside ticket 065's
approved paths.

PR #96 still passed because the Governance Hub CI executed schema and fixture
tests but never ran the deterministic validator against the PR's own base/head
diff. The trusted Validator App used those green checks as its deterministic
trust root and mentioned the added file only in advisory prose. A source-hub
manifest plus a real PR-diff invocation closes that boundary without treating
the downstream `project.sh` wrapper as the hub gate.

The hub is not a Python distribution despite containing Python scripts. Goal
must therefore model it as a generic, non-registry project. Its governed
`pull-request` mode delivers implementation; `direct-main` may create only the
annotated Git tag and matching GitHub Release after trusted merge and a clean
retest.

## Execution plan

1. Commit this bounded plan on exact `origin/main` before implementation.
2. Replace the generated Goal defaults with the minimal source-hub delivery
   contract and synchronized version sources.
3. Add a source-hub manifest and make PR CI validate its real base/head diff.
4. Add regressions for source-hub scope and the raw Goal release contract.
5. Advance release carriers to 0.16.0 and run the full Linux/Windows contract.
6. Deliver through Goal pull-request mode, require exact-head trusted review,
   merge, and retest the clean merge SHA.
7. Publish only the immutable v0.16.0 Git release through Goal direct-main,
   close the ticket governance-only and remove temporary branches/worktrees.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Traced the regression to commit `8e47d5594ddd014c87de25d02950db303c8caca8`
  in PR #96: `goal.yaml` was generated outside ticket 065's `allowedPaths`.
- Confirmed the repository ruleset required only the `test` and
  `windows-governance` fixture suites plus exact-head review; neither required
  check validated PR #96's own diff against its intent.
- Confirmed Goal 2.1.297 has a distinct source-hub health contract and supports
  governed `pull-request` and `direct-main`; the downstream wrapper mismatch is
  therefore not a current defect.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.

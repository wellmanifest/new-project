# Ticket 200: Validate already-published integrations against their preceding base

- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: the user requests continued repairs, tests and GitHub publication. The delivery-base gate currently attributes an already-published integration to intervening target drift and rejects post-merge CI.

## Acceptance criteria

- [x] AC-01: A clean published HEAD with an exact supplied first-parent base passes without hiding genuine intervening target overlap; unknown or dirty observations stay conservative.
- [ ] AC-02: Regression and package checks pass; publish standard 0.20.16 through independent exact-head approval and verify its immutable release.

No policy bypass, target-owned patching, implicit merge approval or modification of other agents' workspaces.

## Validation

The new real-Git suite passes 10 tests; the original implementation failed three assertions. Full governance-validator, adoption-lock and agent-host suites pass. Managed governance reports 0 errors and 0 warnings. The delivery contract counts the already-selected governance checker as one public interface path; the initial allowed file scope is unchanged. Protected publication and immutable release remain pending.

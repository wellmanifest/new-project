# Agent plan — ticket-087 (composer)

## SESSION_EXECUTION_AUTHORIZATION

User asked to standardize autonomously so LLMs invoke validator-agent without
re-explaining each time; closest pack is `wellmanifest/new-project`.

## Why LLMs keep asking

Hub AGENTS described *what* trusted approval is (`trusted-validator-apps`) but
not the *operator action* coding agents must take (`dispatch-direct-pr.sh`).
Agents therefore escalate to the human.

## Done

1. Closed integrated ticket-085 to free governance workstream.
2. Added rule **13a / 11a INVOKE VALIDATOR-AGENT** to `AGENTS.md` and template.
3. Extended `C-PUBLISH-003` and `docs/GOVERNANCE_ENFORCEMENT.md`.
4. Dispatched validator for `wellmanifest/policy-dsl#5` (run failed on
   validator-agent pytest — infra, not policy-dsl); will retry after hub PR.

## Validation

- rg for dispatch-direct-pr / MUST NOT ask human
- `./project/governance-check.sh`

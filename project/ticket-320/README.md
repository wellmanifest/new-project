# Ticket 320: Protected local publication evidence composition

- **ID**: ticket-320
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user requested a local alternative using github-com, onedev-agent and validator-agent; continue, test and publish through the protected independent controller.

## Acceptance criteria

- [x] AC-01: Closed composition schema binds exact subject, protected boundary, independent CI/review, publication CAS/readback and signature-verification references; negative fixtures reject incomplete shapes.
- [ ] AC-02: Normative verification and adoption obligations are explicit, existing hosted S4 remains intact, required CI runs the schema suite and native governance passes before independent publication.

## Boundary

PLF-029 normative composition only. Git ref lifecycle and attestation signature verification retain their canonical owners. Source schema validity grants no authority; production verifier, service deployment and Clonerd admission are dependent work in PLF-026.

Bounded S30 session; exact fencing and continuity receipts live in the external protected store.

## Validation

Eight composition tests pass, including nested required fields, closed unknown authority, wrong roles, false hosted claims, malformed subject/digests, check outcomes and bounded aware timestamps. Four canonical namespace tests and existing standard-pack suite pass. These are structural fixtures, not cryptographic or deployed admission evidence. Required CI runs the new suite. Independent exact-head review/publication remains pending.

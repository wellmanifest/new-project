# ticket-424: Resolve issue #534 finding 5 by documenting declared S4/S5 evidence and adding regression tests for its verification boundary.

- **ID**: ticket-424
- **Owner**: agent:coding-agent
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

## Goal and scope

Resolve the remaining evidence-policy ambiguity in issue #534 finding 5 through explicit documentation and regression coverage of the existing declared-evidence behavior.

SESSION_EXECUTION_AUTHORIZATION: validated native ticket PLF-22366; Willman request 814f8ce9-b01d-4a4f-93d6-dee698114acc; protected publication only.

## Acceptance criteria

- [x] AC-01: AC-01: Document the explicit decision to retain declared external evidence: the checker recognizes schemes with at least two characters and validates SHA-256 syntax without fetching evidence or authenticating its issuer, contents or freshness.
- [x] AC-02: AC-02: Explain that checker acceptance does not establish actual S4 protection, S5 runtime conformance or trusted publication approval; reference the existing conformance and approval standards.
- [x] AC-03: AC-03: Add offline positive regressions for complete S4 and S5 evidence chains using HTTPS and custom schemes, selecting the appropriate existing execution model for each level.
- [x] AC-04: AC-04: Add negative regressions rejecting Windows drive paths as external evidence, malformed external digests, local files presented as S4/S5 proof, and reused S3/S4/S5 proof URIs. Preserve existing local-file existence and digest tests.
- [ ] AC-05: AC-05: Focused evidence tests, existing standard-pack checks, the managed governance gate and whitespace checks pass during subsequent authorized execution.
- [x] AC-06: AC-06: Material changes remain confined to the two frozen paths, with no checker behavior changes, public interface changes or runtime dependencies. This slice does not claim completion of the release or adopter rollout.

## Implementation evidence and runner handoff

- Request: PLF-22366 / admitted issue `wellmanifest/new-project#534`, finding 5 only.
- Participant: `agent:coding-agent`, implementing the runner's bounded session scope.
- Frozen `acceptedBaseSha` and unchanged HEAD: `2269e5736270b55b61fd1db2a42658d1467c49ff`.
- Immutable intent SHA-256: `4b017bd3606c951c7067385b3f927f7b3734090eec4f81c180f6a7187dbcc799`.
- Branch: `ticket/424-project-job-814f8ce9`; canonical worktree: `.worktrees/ticket-424--project-job-814f8ce9`.
- Observed runner lease: `allocation-ticket-424-project-job-814f8ce9`, revision 1, fencing token 1, phase `claimed`, expires `2026-11-11T04:39:13Z`. No lease transfer or renewal was performed.
- Managed work-start query returned `REUSE_EXISTING`, no blockers, and only the two accepted material paths. Existing runner changes to `project/TICKETS.md` were preserved.
- AC-01/02: `docs/STANDARD_PACK_BOUNDARIES.md` explicitly retains declared external evidence and documents URI recognition, digest syntax, local-file verification, distinct URI strings, execution-model limits and independent conformance/approval authority.
- AC-03/04: `tests/standard_pack_evidence_test.py` exercises complete S4/S5 chains with reserved HTTPS hosts and custom schemes, plus Windows drive paths, malformed external digests, valid local files used as upper-level proof, reused proof URIs and missing chain levels. Existing local-file existence and digest-mismatch regressions remain covered. CLI exit status is also checked.
- Focused validation: `PYTHONDONTWRITEBYTECODE=1 bash tests/standard-pack-check.test.sh` passed (17 unittest methods, including 9 evidence methods); `git diff --check` passed. The final URI-reuse assertion was strengthened to retain different declared digests and rechecked with the focused evidence suite.
- Diff review: material changes are confined to the two frozen paths; the checker, hooks, version projections and runtime dependencies are unchanged. Added content contains documentation, synthetic evidence and test fixtures; no secrets were introduced. Docker validation is not relevant to this documentation/test slice and was not run.
- AC-05 remains partial pending the runner's authoritative repository tests and managed governance gate. Broad verification and `todo2code compare-workspace` were deliberately not run in this model turn, as instructed.
- Next action: runner refreshes the managed continuity checkpoint/snapshot for this exact dirty worktree, runs the authoritative gates once, and performs its guarded branch binding and publication. This model turn changes only the ticket README and the two accepted material files.
- Outside this slice: findings 1–4, patch release, wave 1 upgrades and adopter PRs. No claim of completing or closing the entire issue is made.

Delivery states: completed locally — finding 5 documentation and regression coverage; locally committed — no; pushed/PR-open — no effect performed by this model turn; merged/deployed — no effect performed by this model turn. Ticket remains `IN_PROGRESS / PUBLICATION`.

---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "local-ci-publication",
  "kind": "information",
  "version": 2,
  "title": "Local OneDev verification and independent Validator publication",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-07",
  "updated": "2026-09-08",
  "review_after": "2026-10-07",
  "source_revision": "d5f77d83b3752477cfb95a535d0e1ce77f148576",
  "affected_repositories": [
    "wellmanifest/new-project"
  ],
  "evidence": [
    "https://github.com/subactor/validator-agent/blob/e0cc9d3707752d7cc3a8d55fa39f05b64254bb76/docs/LOCAL_VALIDATOR_APP_SETUP.md",
    "https://github.com/subactor/docs/pull/75"
  ]
}
---

# Local OneDev verification and independent Validator publication

<!-- docs:section purpose -->
## Purpose

For `semcod/*` and `subactor/*`, prefer local OneDev verification followed by
the independent local Validator App. GitHub may remain the repository and PR
host; GitHub Actions execution is not a prerequisite for this local route.
This standard does not promise zero infrastructure or provider cost.
For these two organizations this transport-selection rule supersedes older
unconditional `dispatch-direct-pr.sh` examples in governance documentation.

<!-- docs:section scope -->
## Scope and authority

Wellmanifest owns this standard. `subactor/onedev-agent` owns the credential-
separated coordinator and test executor. `subactor/validator-agent` owns the
protected verification policy, App approval and explicit merge effect. The
coding agent invokes that boundary and never reviews or merges its own work.

Use the actual protected `config/direct-pr-registry.json` policy, its digest and
OneDev profile. A repository-local document, candidate configuration, green
shell command or LLM opinion cannot replace this authority. Existing explicit
checks remain required until their protected migration is complete.

<!-- docs:section evidence -->
## Evidence levels

Report each level independently for every repository:

1. **Declared:** immutable Wellmanifest revision and digest, indexed instructions.
2. **Configured:** OneDev test profile and canonical Validator policy agree.
3. **Deployed:** the running coordinator/executor and Validator use those pins.
4. **Verified:** a successful receipt binds the actual PR head, current base and
   tested merge result, including the profile and verification commands.
5. **Published:** independent exact-head approval and a fresh merge readback.

An organization policy covers identities but does not enumerate its repositories.
Audit the complete explicit repository inventory, including repositories absent
from both configuration files. Missing profiles are gaps, never success.

<!-- docs:section content -->
## Required agent workflow

1. Read the target's required checks through the protected Validator resolver.
   Observe whether the local timer already selected or published the exact PR;
   reuse its receipt before creating duplicate work.
2. Verify OneDev coverage and runtime health. OneDev must execute the repository's
   real test, governance and required platform matrix against the PR head merged
   with the current base. Candidate code runs without publication credentials;
   only the coordinator publishes `onedev/local-verify`.
3. Freeze the current head and wait for its fresh OneDev receipt. A moved base
   requires a new merge-result test even when the head has not changed. Use the
   existing bounded OneDev retry interface after diagnosing failure; do not
   delete retry state or write a success status manually.
4. Use the trusted local Validator deployment. The deployed reconciliation timer
   is preferred when it already owns the task. For an explicitly authorized
   single PR, the supported local adapter is:

   ```bash
   ./bin/run-local-direct-pr.sh \
     --repository OWNER/REPO --pull-request N --ticket ticket-NNN \
     --expected-head-sha EXACT_HEAD_SHA \
     --key-file "$VALIDATOR_APP_PRIVATE_KEY_FILE" \
     --output-dir "$VALIDATOR_RECEIPT_DIRECTORY" --merge
   ```

   Run it from an independently trusted Validator checkout, with the existing
   protected environment and App key reference. The key contents never enter
   chat, Git, command arguments or receipts. `--merge` invokes the independent
   App's gated publication; it is not self-approval. Without publication
   authorization use the adapter's default dry-run. Preserve all other required
   checks, scoped token verification and current-head/base checks.
5. Re-read the PR, trusted App review and merge result. A timer exit of zero,
   `idle`, pending status or missing receipt is not publication success.

`bin/dispatch-direct-pr.sh` uses GitHub Actions. Use that transport only when
selected by the protected deployment/profile and available. A hosted billing or
capacity error is not a test failure and does not prove that the independent
local route is unavailable. Diagnose OneDev and the local Validator before
escalating a hosted outage. The same distinction applies to `--wait-checks`:
waiting for a missing local status does not mean Validator has executed.

## Migrating existing hosted checks

Before retiring any hosted context, enumerate its exact checks, operating
systems, dependency pins, isolation and test commands. Build a corresponding
trusted OneDev profile, deploy it and obtain a successful canary for the same
head/base. A Linux-only run cannot substitute for an untested Windows job.
Only then may an independently reviewed policy change require the local status
and explicitly retire the equivalent named hosted contexts. Preserve distinct
checks that are not covered, branch protection, trusted App identity and merge
approval. Never blanket-delete workflows, empty a check list, invent a receipt
or use an account wildcard to turn missing verification into approval.

For an unconfigured target, record the exact missing profile, environment,
App installation or verification capability and route it to its owning
repository. Source instructions alone do not enable runtime execution.

<!-- docs:section limitations -->
## Limitations

This file defines behavior and is distributed with the governance package. It
is not a deployment receipt, an executor profile or an execution grant. Adopting
it does not prove adoption of every Wellmanifest pack; select applicable packs
and retain their own immutable pins and conformance checks. Repositories with
existing custom policy need a reviewed, scoped adoption that preserves their
additional test and authority requirements.

<!-- docs:section next_actions -->
## Runtime references and adoption

The canonical runtime runbook is [Local Validator App with OneDev](https://github.com/subactor/validator-agent/blob/e0cc9d3707752d7cc3a8d55fa39f05b64254bb76/docs/LOCAL_VALIDATOR_APP_SETUP.md).
The [profile coverage audit](https://github.com/subactor/validator-agent/blob/e0cc9d3707752d7cc3a8d55fa39f05b64254bb76/docs/information/profile-coverage-audit.md)
compares configured policies; its configured-union mode does not establish a
full inventory. Retain dated, per-repository fleet evidence in `subactor/docs`.

Adopt the published governance package through `goal governance adopt` with an
immutable source revision. The managed consumer reference is
`.governance/docs/LOCAL_CI_PUBLICATION.md`; the managed `AGENTS.md` points to it.
The reference pins the canonical policy without copying authored metadata into
the target repository. This preserves canonical ownership and compatibility
with the documentation placement checker.
For a scoped instructions-only rollout, preserve the target's custom policy,
record the exact standard revision/document digest and explicitly label the
result as publication-policy adoption, not full governance or runtime adoption.

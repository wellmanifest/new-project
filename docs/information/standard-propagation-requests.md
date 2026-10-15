---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "standard-propagation-requests",
  "kind": "information",
  "version": 1,
  "title": "Advisory immutable standard propagation requests",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-10-15",
  "updated": "2026-10-15",
  "review_after": "2026-11-15",
  "source_revision": "6606a17f63fbcaf222771efef7af02cbab4d2851",
  "affected_repositories": ["wellmanifest/new-project"],
  "evidence": ["scripts/standard_propagation_request.py", "governance/standard-propagation-request.schema.json", "tests/standard_propagation_request_test.py"]
}
---

# Advisory immutable standard propagation requests

<!-- docs:section purpose -->
## Purpose

A canonical Release produces source facts for a later governed adoption.
The `propagate-standard` workflow emits an artifact and grants no execution
or publication authority in any adopter repository.

<!-- docs:section scope -->
## Scope

This producer belongs to the standard's CI metadata adapter. Product services
in Semcod or Subactor own future live allocation, admission and execution.
No organization is scanned and no target is selected implicitly.

<!-- docs:section content -->
## Request contract

`scripts/standard_propagation_request.py` reads the GitHub event as bounded
JSON data. Release events must describe a final published canonical release.
Manual dispatch requires `target-version` and `dry-run=true`. A false, missing
or ambiguous dry-run refuses execution: no protected product executor is
configured. Inputs never become shell source.

The producer reuses `create_adoption_lock.py` to resolve the remote canonical
annotated tag and verify the final, non-draft, non-prerelease GitHub Release.
It then reads VERSION, the package manifest and adoption tool from that exact
Git commit. The checkout needs complete source history. Missing tags, source
objects, Release evidence or a matching VERSION cause refusal; HEAD is never
a substitute. The request includes the full source SHA and SHA-256 digests of
both package manifest and adoption tool bytes.

The closed schema requires `readOnly=true`, `executionAuthorized=false` and
an empty `targets` array. Workflow success means that this request was
verified and uploaded. It does not mean that an upgrade ran. The built-in
GitHub token has only contents read permission; there is no broad org token,
target checkout, dependency installation, target write or PR creation step.

<!-- docs:section evidence -->
## Evidence

The focused Python suite uses real Git commits and mocks only external
publication transport. It covers source pins, Release/tag mismatches,
malformed and duplicate input, live dispatch refusal and the workflow's
closed artifact path. CI runs the suite with the existing schema dependency.

<!-- docs:section limitations -->
## Limitations

This artifact is advisory and is neither a lease nor a trusted controller
receipt. A consumer must independently revalidate immutable source evidence,
request bytes and current target state. Goal's existing adoption transaction
and command adapter contracts are optional library pilots; they do not prove
a deployed authorization provider or live delegate exists.

<!-- docs:section next_actions -->
## Next actions

Before any adopter write, use its native ticket allocator and canonical
relative worktree, record bounded intent, acquire and check an independently
controlled current fenced lease, and preserve the protected review/merge
boundary. Publish a canonical source Release only through its authorized
publication process. Installing this schema alone cannot activate a runtime
or establish fleet rollout readiness.

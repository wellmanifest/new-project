---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "ticket-activity-batching",
  "kind": "information",
  "version": 1,
  "title": "Batch ticket activity reads without retaining stale reservations",
  "status": "implemented",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-14",
  "updated": "2026-09-14",
  "review_after": "2026-10-14",
  "source_revision": "6d51770651488d6a5bc25e82c79e2a48893d3fdb",
  "affected_repositories": ["wellmanifest/new-project"],
  "evidence": ["https://github.com/wellmanifest/new-project/issues/352", "../../tests/ticket_activity_batch_test.py", "../../scripts/ticket_activity.py", "../../scripts/worktree_overlap_check.py"]
}
---

# Ticket activity read batching

<!-- docs:section purpose -->
## Purpose

A worktree check must distinguish active delivery from historical ticket files.
Repeating repository discovery, target resolution and receipt reads for each
historical ticket adds delay to every commit without adding independent evidence.
Ticket 230 reduces that repeated work while preserving activity authority.

<!-- docs:section scope -->
## Scope

`worktree_overlap_check.ticket_scopes` opens one `ActivityReadBatch` per checkout.
The standalone resolver remains fresh on every call. Batches are context-local;
linked checkouts and independent clones never share a batch, even with identical
origin URLs. No persistent activity cache, dependency, configuration switch or
change to WIP limits is introduced. Receipt recording refuses an open read batch.

<!-- docs:section evidence -->
## Evidence and reproduction

The regression fixture creates a real Git repository containing 40 delivered
tickets and 40 validated terminal receipts. On 2026-09-14, ordinary resolution
used 280 subprocess calls; one batch used 94, with identical complete resolution
records. This is a deterministic operation-count comparison, not a host latency
SLA. The suite also exercises invalidation, separate clones, nested contexts,
batch reuse, receipt binding and the overlap check's failure path.

Run `python3 tests/ticket_activity_batch_test.py` to reproduce the comparison.
`bash tests/ticket-activity.test.sh` includes that suite so the existing CI job
executes it. Run `bash tests/worktree-overlap.test.sh` for the consuming checker.
A read-only comparison against the same 18 registered checkouts resolved 779
tickets in each run and produced identical complete overlap reports. Subprocess
calls fell from 1,836 to 781. Observed wall times were 28.94 and 25.44 seconds;
these single runs on a shared host are not a controlled latency benchmark.

Raw local profiles and test logs are external in the host audit
`activity-batch-230-20260914`; this document carries the durable interpretation.

<!-- docs:section content -->
## Mechanism and maintenance practice

During a batch, repeated Git queries reuse their observed output, and document
reads and presence checks reuse their observed values. Before returning a result,
the batch re-reads every consulted query and document and checks the ticket
inventory. It observes checkout HEAD, Git common directory and registered
worktrees even when the historical ticket is unrelated to the current branch.
A changed or unavailable input raises the existing activity error and prevents a
clean overlap report. The caller can retry with a fresh observation.

Ancestry targets and candidate ticket branches use observed commit IDs, avoiding
an ancestry decision against a mutable ref that moves during the inspection.
Policy, repository binding, receipt validation and rewritten-history checks retain
their existing rules. Missing policy and registry still follow the adopted
conservative or explicitly selected ancestry policy.

The batch clears all data on success and failure and restores its enclosing
context. A subsequent invocation sees resumed work. Performance changes must
measure operation counts on the same history and preserve negative cases before
claiming speedups; removing checks or trusting old inactive decisions is not an
optimization. New mutable inputs must be included in the revalidation boundary.

<!-- docs:section limitations -->
## Limits

The final read is an observation fence, not a repository lock or transaction.
Changes after observation remain possible; writer leases, overlap checks and
protected publication still apply. Ancestry and rewritten patch verification
continue to run; a large history therefore has nonzero cost. This optimization
covers the overlap inspector, not every caller of the activity resolver.

SQLite ticket content keeps its existing input validation and snapshot behavior;
this batch does not create a new database synchronization guarantee. Publishing
source or a release does not prove deployment to adopters or protected executors.

<!-- docs:section next_actions -->
## Publication and adoption

Publish the source with matching VERSION and standard manifest projections through
Goal and independent exact-head review. Publish an immutable release before
updating a canary adopter through its managed adoption command. Verify the new
pin, application tests and protected executor compatibility before expanding to
other repositories. Do not patch installed governance files or hashes directly.

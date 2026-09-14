---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "audit-evidence-storage",
  "kind": "information",
  "version": 1,
  "title": "Audit evidence storage and managed lifecycle routing",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-14",
  "updated": "2026-09-14",
  "review_after": "2026-10-14",
  "source_revision": "c5b2581c16a4cd1ba7987f22c63116710d41a8d6",
  "affected_repositories": ["wellmanifest/new-project"],
  "evidence": [
    "https://specifications.freedesktop.org/basedir/latest/"
  ]
}
---

# Audit evidence storage and managed lifecycle routing

<!-- docs:section purpose -->
## Purpose

An audit is a traceable collection of observations, not a new ticket system,
executable repair package or trusted approval. This profile explains the
existing external-evidence policy; it introduces no mandatory `.audits`
directory, service, Planfile installation or retrospective data migration.

<!-- docs:section scope -->
## Ownership and classification

Classify content before selecting its location; extensions and directory names
do not confer authority.

| Content | Owner and location | Authority boundary |
| --- | --- | --- |
| Sanitized command stdout/stderr, transient request payloads, diagnostic observations | Executing application's private state store | Input/output evidence, never executable instructions or approval |
| Lifecycle/validation receipts, snapshots and archives | Declared controller's receipt/artifact store | Trust depends on provenance, exact subject and verification, not location |
| Durable conclusion, reusable analysis or operating guidance | Owning repository's tracked `docs/information`, `docs/analysis` or `docs/decisions` under `wellmanifest/docs` | References evidence; does not duplicate private raw logs |
| Structured log events | `wellmanifest/logs` contract and its selected stream backend | Event format and append semantics, not a general report/archive location |
| Bounded task intent and status | Managed ticket input; explicitly adopted Planfile and GitHub projections | Existing allocator owns governance ticket IDs |
| Executable repair or reusable orchestration code | Versioned source in the owning product/runtime, outside ticket and audit directories | Reviewed implementation with tests; invoked at a verified revision |

The logs contract at revision `48c284ef7a069055c0bcb6b900147ce5e65f8b43`,
`contracts/logs.contract.v0.3.json`, defines structured events and append
requests. It does not replace this storage profile. `wellmanifest/reports`
was not accessible during this investigation; no requirement is inferred from
its name. If that contract becomes available, compare ownership before adopting
or creating another standard. Reporting format and private execution evidence
storage are distinct concerns even when one report references an audit.

<!-- docs:section content -->
## Default layout and discovery

For a Linux/XDG runtime, use the application's declared state directory:

```text
<XDG_STATE_HOME>/<runtime-id>/audits/<run-id>/
```

If unset or empty, `XDG_STATE_HOME` defaults to the user's `.local/state`.
Relative XDG values are invalid and ignored, not resolved against a worktree.
The [XDG specification](https://specifications.freedesktop.org/basedir/latest/)
classifies persistent logs and action history as state. Thus the existing
`~/.local/state/taskand/audits/<run-id>/` layout is suitable for local Taskand
execution evidence, including work on other repositories. It is not a backup
guarantee or a portable user-data store. Non-XDG hosts resolve their declared
per-user persistent application-state directory; never guess a Linux path.

The runtime selects a collision-resistant run ID and its own registered
runtime ID, not an arbitrary model-supplied path. A timestamp or directory label
alone is not a unique identity. Refuse path traversal and symlink redirection
before creating/writing evidence. New private directories use mode `0700`,
files `0600` (or equivalent ACL); do not silently change existing permissions.
Apply private creation permissions to the evidence writer, not by silently
changing the tested application's declared environment or umask. Redirection
into an already private output file need not alter test-process permissions.
Create no executable files in a new audit run.

For repository discovery an adopter may maintain a small ignored index at:

```text
<primaryCheckout>/.subactor/receipts/audits/<run-id>.json
```

Resolve `primaryCheckout` from registered Git worktrees even when called inside
a linked worktree. Use existing `.subactor/receipts/` ignore policy, never a
tracked index containing private locations. The index only references external
evidence; it is rebuildable and nonauthoritative. Deleting a worktree must not
delete the audit it references. A cross-repository run can be referenced by
several indexes without copying its logs or sharing ticket authority.

An explicitly configured, ignored `<primaryCheckout>/.audits/` is a supported
local backend/alias, not a second default. It needs the same privacy, retention
and cleanup protections; it does not survive loss of that clone. Do not create
an independent `.audits` per linked worktree or recursively ignore arbitrary
user-owned directories. Keep existing layouts readable; migration requires
classified targets, authorization, verified copies and reference reconciliation.
This profile authorizes no move, replay, deletion or automatic retention sweep.

## References, privacy and retention

Bind evidence through the selected receipt/artifact contract to the repository,
ticket or read-only request/session, run/correlation ID, observed revision,
producer/runtime revision, actual result and content digest. A read-only audit
does not need a new implementation ticket/worktree. For uncommitted inputs also
bind the workspace/snapshot digest; HEAD alone cannot identify those inputs.
Record unknown or partial results explicitly. An interrupted command is not a
passed test, and a process exit code is not a trusted review.

Use the existing opaque `artifact:`/`receipt:` references and schema versions
accepted by the lifecycle controller. A [URN is a kind of URI](https://www.rfc-editor.org/rfc/rfc8141),
not an alternative to URI: a stable identifier and a retrievable location have different roles.
Resolve a reference through the declared registry/store and verify its digest;
do not invent a resolver or treat a filesystem path as portable identity.
Private indexes may hold local locations. Shared reports carry safe references
and hashes, not home-directory paths, credentials or private request bodies.
Do not inject additional fields into an existing closed receipt schema: extend
its owning contract or use its supported context/evidence references.

Sanitize before persistence and before publication, not only before printing a
summary. Explicitly exclude credentials, environment dumps and unrelated user
data; a log can contain all three. Evidence requiring restricted raw retention
uses a separately authorized restricted store, not the normal audit directory.
Keep result digests bound to the sanitized bytes actually retained. Corrections
append/supersede records rather than silently editing completed evidence.

The storage owner declares retention and access policy. Cache is disposable;
referenced evidence is not. Cleanup first checks outstanding references, active
work and retention obligations; unavailable policy means preserve and report.
Cross-process/machine recoverability requires the existing durable snapshot and
receipt protocol, verified retrieval and an independent retained copy as
applicable. An absolute local path or an ignored index is insufficient proof.

## Recipes: use the existing lifecycle, not a second implementation

| Intended action | Preferred verified entry point | If capability or result is uncertain |
| --- | --- | --- |
| Observe work before starting | `scripts/work_start_check.py` in the hub, adopted `.governance/work_start_check.py` in a target | Reconcile observed work; do not allocate another ticket just to retry |
| Allocate admitted implementation work | `project/new-ticket.sh` with explicit workstream and owned paths | Resume the existing ticket or registered allocation request; no hand-picked IDs |
| Select Planfile project/store | `planfile config show --project <repository> --json`, then actual project/store readback through the pinned installed adapter | Reject mismatched or inherited project selection; configuration output alone is not installation proof |
| Register/synchronize Issue and Planfile projections | Project-declared registration controller and its scoped Planfile adapter | Retain one request identity and pending effect in its durable journal; do not create a duplicate Issue |
| Publish requested implementation | Repository-declared Goal protected delivery procedure | Use its diagnostics and recovery route; no raw push/merge fallback around required gates |
| Inspect remote Issue/PR state | Managed query adapter, or scoped read-only `gh`/API query | Report unavailable/partial state; a transport error is not evidence of absence |

`git-lifecycle` and `ticket-lifecycle` define typed requests; a GBNF file is not
an installed executor. Before using an adapter, verify its actual invocation,
declared version, project/store binding and supported operation. A CLI on PATH,
a version string, a Planfile MCP connection without project selection or prose
in a standard is not that verification.

The [work-registration contract](work-registration.md) documents the product
controller and read-only consistency checker separately. Its adoption and
implementation limits still apply. This profile neither silently activates it
in existing projects nor weakens it where explicitly adopted. In a repository
without that integration, use the existing authorized ticket lifecycle, report
the missing integration, and keep evidence attached to that ticket. Do not
install or bind a global Planfile store merely to make an audit appear complete.

Direct `gh issue create` is a remote effect, not a query. A managed adapter may
use `gh` internally, but must own request correlation, exact repository,
idempotency, authorization and result readback. A raw command is not equivalent
to Planfile synchronization. If no adapter exists and current policy permits a
bounded transport fallback, record that route and exact request before the
effect; do not claim managed registration. A timeout requires querying for the
previous result before any retry. If absence cannot be established, keep the
effect pending. Required Goal/approval/lease gates have no such raw fallback.

Saving `issue.md` as sanitized request data is acceptable; it must not become
the sole task record. Saving `discard-authorized-branch-*.py` in an audit
directory does not make it an audited runtime. Preserve historical scripts as
non-replayable evidence; reusable behavior belongs in versioned product source
with bounded inputs and tests. A repair's old authorization is not permission
to execute it again. Do not replace a missing controller with a private script
and then describe the procedure as standardized.

## LLM integration without additional ceremony

```text
user intent -> observed state + registered capabilities -> bounded request
            -> request-only grammar/schema -> controller preconditions
            -> one authorized effect -> receipt -> verified projection
```

Give the model only relevant rule IDs, current typed observations, accepted
intent and registered operation/schema references. Render a compact human DSL
view from that same request; do not maintain an independent prose execution
plan. Keep untrusted log contents separate from instructions. The controller,
not the model, resolves paths, credentials, adapters and authority.

A refusal should include the failed condition, observed state, a safe next
action and the request/evidence reference. Apply the narrowest existing recipe
and retry only the affected operation after reobservation. Do not regenerate a
ticket, worktree, full plan or giant policy prompt for each log, retry or status
query. Read-only diagnosis and unrelated authorized work remain available.

An adapter should expose the cost and effects of preflight: `--dry-run` must not
be assumed to mean no tests or no network. Where current policy allows evidence
reuse, bind it to the exact inputs/workspace, policy, tool/runtime and test
selection, then invalidate only the affected evidence. Reuse is not permission
to skip required checks or cache approval/leases. Report which stage is running
and why a repeat is needed, rather than silently rerunning full delivery for
each query. This is a product-adapter improvement, not another mandatory gate.

<!-- docs:section evidence -->
## Verification

Check the selected storage backend, ignored index, reference retrieval, digest
and redaction without replaying an audited effect. Check both a primary and a
linked checkout resolve to one index. For an adapter rollout, test two projects,
a mismatched/inherited Planfile config, lost response, restart and duplicate
retry before enabling real effects. Use existing work-registration and
work-start regression suites for their existing contracts, not as evidence that
this storage profile is automatically enforced.

<!-- docs:section limitations -->
## Enforcement and adoption limits

This is a procedural profile, not a new executable storage API, schema validator,
installer or cleanup daemon. Existing gates continue to enforce their declared
contracts; they do not yet validate every storage/path/retention requirement
above. A documentation merge alone neither reorganizes old audits nor deploys
Planfile or changes every adopter. Source publication, pinned adoption,
runtime verification and fleet enforcement must be reported separately.

<!-- docs:section next_actions -->
## Next implementation boundary

Implement missing storage/index and registration adapters in their owning
product, reusing existing receipt and log schemas. Prove the canaries above,
then distribute their pinned bindings through the normal immutable adoption
process. Do not create another standard repository, mandatory global database
or unconditional deployment gate solely for these locations.

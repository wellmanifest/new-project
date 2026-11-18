# Explicit local owner handoff

`owner_handoff.py` supports the registered `local-single-clone` allocation
policy. It preserves the ticket, branch, relative linked worktree, scope and
birth plan while advancing revision, fencing and session with a bounded TTL.
Expiry or absence of a process never supplies consent.

The standalone command is read-only:

```sh
python scripts/owner_handoff.py --root /canonical/primary --request /protected/request.json
```

For application, a protected host adapter imports the **independently published,
immutable** controller and invokes its public `handoff` function with
`apply=True`, a pre-opened authorization FD and a trusted `verifier` callable.
The request cannot select a verifier or executable path. The standalone CLI
cannot authenticate an owner and therefore refuses `--apply`.

The adapter must authenticate the old owner's explicit consent using its
existing trusted identity or capability mechanism. It must independently bind
that proof to the complete request: primary checkout and repository, old owner
and session, lease bytes/revision/fence, current HEAD, content/index snapshot,
intent digest, preserved scope, successor actor and **fresh session**, and TTL.
An actor label, environment variable, JSON object, FD or digest alone is not an
identity credential. A host without that trusted adapter must stop; this
controller does not create an identity issuer or an unregistered lease store.

The verifier receives the complete request and decoded authorization data. It
must return stable JSON evidence containing `requestDigest` (SHA-256 of sorted,
indented request JSON plus newline) and `verificationRef`, or raise on refusal.
It runs again before replacement and on every replay. Verification must be
read-only; the durable controller journal owns mutation/replay bookkeeping.
Authorization bytes and verified provenance are archived in the private journal.

`observe(root, worktree_id)` supplies a read-only snapshot for preparing the
request. The protected adapter must authenticate consent separately. Apply
re-observes registered Git ownership, current intent, staged blobs, file bytes
and lease identity under the shared slot lock. It archives original bytes and
the exact successor before replacing the lease atomically. Recovery accepts
only that exact journal and successor, re-authenticates, never extends its
lifetime and rejects later workspace, fencing, policy or authorization changes.
The returned writer environment is for the ordinary work-start/writer checks;
it is neither review approval nor permission to merge.

## Resume a released unfinished ticket

`observe(root, worktree_id, released=True)` is read-only. The separate public
`resume_released` API accepts `new-project.released-owner-resume/v1`: all the
ordinary request bindings plus `releaseEvidenceRef` and
`expectedTerminalStateSha256` from the observation's `terminal` field.
The ordinary `handoff` API and standalone CLI continue to reject this schema;
the protected host adapter selects the explicit API, never candidate code.

A released file is insufficient evidence of a stopped writer. Before each
apply and exact replay, the trusted verifier must independently authenticate
an explicit original-writer release/handoff or a protected controller's
observation that its old writer has stopped. A timeout or missing PID is not
that observation. The full request digest binds the successor session, TTL,
all Git/index/content/intent observations and old lease CAS. In addition to
`requestDigest` and `verificationRef`, verifier evidence must contain exactly
these `releasedOwner` fields:

```json
{
  "leaseId": "original-lease-id",
  "leaseSha256": "exact-request-expectedLeaseSha256",
  "revision": 2,
  "fencingToken": 2,
  "repositoryRef": "original-lease-repositoryRef",
  "canonicalRepositoryRef": "request-repositoryRef",
  "releaseEvidenceRef": "receipt:independently-acquired-controller-release",
  "writerState": "explicitly-released"
}
```

`controller-observed-stopped` is the other supported `writerState`. The
example is data, not a credential, signed attestation, proof issuer or
request-selected verifier. Missing, revoked or unavailable independent proof
must cause the adapter to refuse. A saved README or local JSON receipt alone
does not authenticate a controller. Apply before independent publication of
the implementation is forbidden.

Resume requires an unfinished `BLOCKED / HANDOFF` carrier, the allocator's
exact `scopeHash` (canonical `allowedPaths` JSON), and the separately bound
full current intent digest. The birth `planHash` is preserved. A complete,
schema-valid, repository-bound managed terminal registry and policy must be
present; any known releasing outcome for this ticket/target prevents reopening.
Their digest and the current target HEAD are rechecked with the workspace.
Missing, corrupt, unsafe or changed terminal state fails closed.

Only this released operation can translate a historical bare repository name
to the exact canonical origin of the same primary Git registration. The bare
name must equal that origin's basename; the protected verifier binds both
identities and the exact old bytes. All other lease fields remain subject to
canonical validation. The operation never patches the old file in place:
its separate `released-owner-resume` journal archives the original bytes and
the canonical successor before an atomic CAS replacement. Ordinary handoff's
repository comparison remains strict.

The successor preserves ticket, branch, worktree, scope, birth plan, current
HEAD and dirty payload. It advances revision/fencing, starts a fresh bounded
`claimed` session and clears obsolete PR/Validator references. Exact replay
reauthenticates and never extends expiry. Later workspace, intent, terminal,
owner, policy, authorization or fencing changes require a new protected
decision. Re-run work-start and writer checks before implementation, then
activate the same ticket and obtain fresh independent validation/publication.

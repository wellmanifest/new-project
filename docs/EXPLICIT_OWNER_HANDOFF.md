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

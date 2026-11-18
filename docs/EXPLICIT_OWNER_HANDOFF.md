# Explicit owner handoff

`owner_handoff.py` is a local controller operation, not an expiry-based
takeover. The current owner must provide explicit consent and the protected
caller must pass the owner/session invocation context. The request binds the
lease bytes, revision, fencing token, checkout branch, `HEAD`, and complete
dirty snapshot. A plan is read-only; apply archives the original lease and
atomically issues one bounded successor with incremented revision/fence.

Replaying the exact request returns the original receipt without extending its
TTL. Any changed lease, checkout, symlink, frozen phase, or missing owner
context is refused. The controller does not infer owner death from timeout or
PID absence and never removes a checkout.

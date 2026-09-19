# Allocator recovery authorization

- participant-id: codex
- role: agent
- ticket: ticket-254

## Authorization

SESSION_EXECUTION_AUTHORIZATION: the user explicitly accepted extending the
Wellman delivery task to repair and publish the upstream allocator, with owner,
lease and exact-commit validation. This authorizes the declared protected
publication process, not self-approval or direct merge.

## Plan

Implement one bounded local-file recovery operation under allocator/controller
locks; validate exact identity, live owner/CAS, HEAD, dirty digest, scope and peer
admission before creating absent ticket carriers. Add negative and end-to-end
tests, run the managed gate and publish the material change with its version.
Adoption in downstream repositories remains owned by their separate tickets.

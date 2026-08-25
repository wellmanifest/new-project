# Multi-agent change lease

`wellmanifest/change-lease` is the portable authority contract for serializing
repository and publication effects. Worktrees isolate files; a change lease
decides which actor may mutate a repository, branch, pull request or release.

## Contract

- `wellmanifest.change-lease/v1` is the current state.
- `wellmanifest.change-lease-transition/v1` is a compare-and-swap request.
- `wellmanifest.change-lease-receipt/v1` is append-only transition evidence.

Every accepted transition increments `leaseRevision` and `fencingToken`. A
writer presents the exact current revision, token and phase. Once the phase is
`publication_frozen`, `headSha` is immutable through approval and merge.

```text
claimed -> editing -> validating -> publication_frozen -> dispatching
                                                    -> approved -> merged
                                                                -> closed
                                                                -> released
```

`cancel` and `expire` are explicit terminal paths. `supersede` is accepted only
outside frozen publication phases and with a terminal replacement receipt.
Closing requires `merged`; a closed PR or absent worktree is not proof.

## Adoption

The managed package installs `.governance/change-lease.schema.json`,
`.governance/change_lease_check.py` and its diagnostic runbook. An adopter may
persist `.governance/change-lease.json` and append receipts to
`.governance/change-lease-events.jsonl`; governance validates them when present.
The effectful controller, lease store, GitHub authority and credentials remain
runtime responsibilities of Subactor.

```bash
python3 .governance/change_lease_check.py validate .governance/change-lease.json
python3 .governance/change_lease_check.py transition --lease lease.json --request request.json
python3 .governance/change_lease_check.py trace .governance/change-lease-events.jsonl
```

Lease evidence contains references and hashes only, never secrets or raw diffs.

# Standard pack boundaries

`wellmanifest/new-project` composes standards; it does not re-own their domain
semantics. The machine-readable source for this routing is
`governance/standard-packs.json`.

## Git delivery chain

| Concern | HOME pack | `new-project` responsibility |
| --- | --- | --- |
| repository, branch, ref and PR lifecycle | `wellmanifest/git-lifecycle` | point to and pin; never restate the state machine |
| physical worktree placement and lease path | `wellmanifest/worktrees` | distribute immutable schema/checker bytes |
| divergent-work disposition | `wellmanifest/merge` | require it before destructive recovery |
| exact-head approval evidence | `wellmanifest/validation-attestation` | expose the target's runtime binding |
| ticket states and transitions | `wellmanifest/ticket-lifecycle` | scaffold the ticket projection |
| authority lease and fencing | `wellmanifest/authority-lifecycle` | compose the adopted contract |

`wellmanifest/git` is a compatibility/navigation alias for
`wellmanifest/git-lifecycle`. It is not a repository or a second pack.

## Other extracted concerns

| Concern | HOME pack |
| --- | --- |
| LLM policy boundary | `wellmanifest/llm` |
| structured logs and diagnostics | `wellmanifest/logs` |
| plan of action | `wellmanifest/poa` |
| DSL interoperability | `wellmanifest/dsl` |
| repair/remediation lifecycle | `wellmanifest/repair-lifecycle` |
| product offer and commercial registry | `wellmanifest/offer` |
| brand vocabulary and tokens | `wellmanifest/brand` |

Runtime credentials, provider choices, validator commands, GitHub App
identities, daemons and effect execution remain in the adopting runtime (for
example Subactor). A domain pack must not HOME those runtime services.

## No-duplication rule

1. A semantic rule has exactly one HOME pack.
2. `new-project` may carry only a short pointer or a byte-exact, immutable and
   digest-bound adoption projection.
3. A generated projection states its source pack and revision; it is not an
   editable fork.
4. An alias resolves to one pack and cannot create a new repository.
5. Cross-pack requirements use stable pack identifiers, not copied prose.
6. Runtime-specific commands and credentials stay outside Wellmanifest.

This distinction permits offline, reproducible adopters without creating a
second source of truth: copied bytes are generated artifacts, while policy
authority remains in the referenced HOME pack.

## Effective execution model

The canonical enforcement scale is `S0-S5` from
`docs/STANDARD_CONFORMANCE.md`. Repository-role profiles in
`governance/standard-packs.json` require protected conformance (`S4`) for every
repository and runtime receipts (`S5`) for services, executors and deployment.

`scripts/standard_pack_check.py` validates the selected profile, immutable
revision, evidence chain and digest of each installed projection. Repositories
start with `.governance/standard-adoption.json` in `audit` mode and switch to
`enforce` after the evidence chain and exact required check exist.

An identical managed artifact is therefore not source duplication when its
revision and digest match. Independent normative sources and drifted projections
are errors. Historical `.worktrees` are excluded from authority scans and
audited separately under `wellmanifest/worktrees` so completed delivery work
does not obscure real policy forks.

The rollout sequence is: classify the repository role, attach its profile,
record immutable evidence, enable the exact required check, protect the default
branch, switch to `enforce`, and let the fleet report create drift work rather
than editing repositories concurrently.

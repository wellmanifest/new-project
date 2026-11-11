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
| code-level semantic query and AST diagnostics | `wellmanifest/code-dsl` |
| natural-language, canonical DSL, and adaptive LLM communication | `wellmanifest/nl-dsl-llm` |
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

## Declared evidence and verification limits

The evidence policy retains the existing declared external proof behavior in
`scripts/standard_pack_check.py`. External evidence is recognized by a URI
prefix matching `[A-Za-z][A-Za-z0-9+.-]+:`: the scheme has at least two
characters. HTTPS and custom schemes are accepted without a scheme allowlist;
Windows drive paths such as `C:\proof.json` and `C:/proof.json` do not qualify.
This prefix check does not validate the rest of the URI or establish that it
identifies an external service.

Every evidence entry must declare a SHA-256 of exactly 64 lowercase hexadecimal
characters. For external evidence, the checker validates this syntax and takes
the proof as declared. It does not fetch the URI, compare the digest with remote
content, authenticate an issuer, verify a signature, or assess freshness.
Repository-local evidence must instead name an existing file inside the
repository whose actual SHA-256 matches the declaration.

An adoption record needs valid evidence for every level from S0 through its
claimed level. S3 requires a recognized CI definition or declared external
proof; S4 and S5 require declared external proof. Each S3, S4 and S5 proof URI
must differ from every lower-level proof URI. This enforces distinct URI
strings, without establishing that different URIs identify different content.
The execution model must also support the claimed level:
`protected-conformance` supports at most S4; S5 requires
`runtime-conformance`.

Checker acceptance therefore establishes consistency of the adoption record
and installed projections within these limits. It does not establish actual
S4 branch protection or S5 runtime conformance. Those meanings remain defined
by the [conformance scale](STANDARD_CONFORMANCE.md#co-znaczy-egzekwowalne) and
the existing HOME packs. Independent exact-head approval remains owned by
`wellmanifest/validation-attestation` and the adopting protected publication
controller, subject to the [approval rules](../POLICY.md). A declared URI,
digest, or passing standard-pack check supplies no publication authority.

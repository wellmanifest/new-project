# Protected local publication evidence

This contract composes evidence for publishing a tested commit to a dedicated
protected local Git reference. It applies when an adopter selects a local
publication service instead of relying on paid hosted branch protection.
The closed model is
[`protected-local-publication.schema.json`](../../governance/protected-local-publication.schema.json).

The model is a structural contract. Passing schema validation MUST NOT grant
publication authority, establish deployment or satisfy an adoption level.
The current catalog's hosted S4 definition and existing adoption records remain
unchanged. A local publication receipt MUST NOT claim protection of GitHub refs,
a GitHub merge or hosted S4. Activating a local protection adoption route needs
a separately reviewed protected verifier, an immutable deployment profile and
real adoption canaries before any catalog or adopter transition.

## Ownership and independent selection

`wellmanifest/new-project` owns this composition. `wellmanifest/git-lifecycle`
owns native ref and transaction semantics; `wellmanifest/validation-attestation`
owns signatures, issuers and approval verification. Running producers and
verifiers belong to their product owners, including github-com, onedev-agent
and validator-agent. This model references their receipts and does not redefine
their formats or signature algorithms.

The protected verifier MUST select expected repository, storage identity,
issuer, policy, profile, runtime, trusted approval actors and exact required
check names from independently administered immutable inputs. Candidate files,
CLI choices by a writer, mutable branches, model output and receipt fields MUST
NOT select these trust inputs. Every referenced receipt MUST be acquired outside
the candidate checkout and checked against its SHA-256 before interpretation.
URI syntax or a digest alone establishes neither issuer authority nor freshness.

## Obligations beyond the schema

The verifier MUST enforce all of these relationships before accepting evidence:

1. `subject` identifies one repository, PR, active ticket, base/head refs and
   SHAs, exact tested merge commit and tree. All CI, approval, publication and
   signature subjects MUST match it. The native Git verifier MUST establish
   valid ref names, object types and the declared merge parent relationship.
   Equal hashes, plausible strings or matching trees alone do not prove that
   the exact commit was tested.
2. `boundary` MUST match the deployed protected storage, instance, profile,
   runtime and policy. Writer, CI and Validator identities MUST be distinct
   authenticated principals. The isolation receipt MUST prove that writer and
   candidate test processes cannot read Validator credentials or modify the
   protected base ref, policy, oracle, runtime or trusted receipt store. Merely
   naming three roles or using three tokens in one writable process is insufficient.
3. `ci.requiredChecks` MUST equal the independently selected required set;
   `ci.checks` MUST contain exactly that set with every result PASS. CI MUST
   genuinely execute those gates against the exact `subject.testedCommit` and
   attest the resulting immutable object and runtime. A copied hosted status,
   a head/base-only receipt or writer-authored PASS is insufficient.
4. `approval` MUST contain independently verified current exact-head approval
   for the same repository, PR and ticket from a selected trusted actor.
   Approval MUST follow successful CI. The protected publisher MUST reobserve
   approval and reject withdrawal, replacement or subject drift before its effect.
5. `publication.beforeBaseSha` and `beforeHeadSha` MUST equal the subject's
   base/head. The native protected transaction MUST verify both refs atomically
   with publication, set the base to the exact tested commit and preserve the
   head. The after-values MUST therefore equal `testedCommit` and `headSha`.
   `liveReadbackReceipt` MUST establish the current actual refs after publication;
   historical completion is insufficient after a later ref movement.
6. `proof` MUST reference an attestation verified by the selected protected
   verifier using the canonical signature contract, issuer, predicate type and
   complete subject bindings. The signed evidence MUST cover the composition's
   receipt digests, protected boundary and freshness. The signature envelope and
   its verification receipt are external references, not candidate booleans.
7. `freshness` MUST use aware timestamps, a positive lifetime no greater than
   the selected bound, and no future issue time. CI, approval, signature and
   readback timestamps MUST be ordered and within that bound at the effect.
   Replays for another instance, policy, subject or transaction MUST be refused.

All semantic failures MUST stop the dependent effect with a stable diagnostic.
Schema validation alone cannot establish these relationships. Runtime owners
MUST expose a bounded recovery route: reobserve, reacquire fresh evidence or
record a blocked handoff. Recovery MUST NOT overwrite unknown refs or manufacture
passing checks. An idempotent completed transaction requires live ref readback.

## Deployment and adoption canaries

`negativeCanaries` requires digest-bound receipts for wrong roles, missing or
failed checks, moved head/base, withdrawn review, untrusted issuer, expired
evidence, CAS conflict, direct ref write, another subject's replay and movement
after a completed merge. These tests MUST exercise the deployed authenticated
boundary and preserve actual refusal and unchanged-ref evidence. A successful
real candidate must also prove exact tested commit publication and recovery.

Fixture credentials, review doubles, schema examples and disposable Git tests
remain TEST_ONLY evidence. Their receipts MUST NOT be promoted into production
admission. Source merge, local commit, deployed service, passing canary and
accepted adoption are separate delivery states and MUST be reported separately.

An adopter transition MUST pin independently approved verifier and service
revisions, register the protected trust inputs, run positive and negative live
canaries and preserve a verified rollback before using this evidence to unblock
publication. Hosted mirroring, if wanted, requires its own approved transport
policy and actual hosted readback; this contract grants no such effect.

---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "release-bump-admission",
  "kind": "information",
  "version": 1,
  "title": "Release-bump admission class for native adoption gates",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-10-30",
  "updated": "2026-10-30",
  "review_after": "2026-11-13",
  "source_revision": "02721a30",
  "affected_repositories": [
    "wellmanifest/new-project"
  ],
  "evidence": [
    "https://github.com/maskservice/workshop/pull/12",
    "https://github.com/maskservice/fleet/pull/17",
    "https://github.com/subactor/onedev-agent/pull/814"
  ]
}
---

# Release-bump admission class for native adoption gates

<!-- docs:section purpose -->
## Purpose

Proposal only. It grants no execution, approval or merge authority and changes
no gate. It describes how a plain version increment can be admitted by a
declared class instead of a per-repository path patch.

<!-- docs:section scope -->
## Scope

In scope: version-only pull requests (`VERSION` and the ticket carrier files)
against repositories whose local OneDev profile runs the native adoption
admission check. Out of scope: firmware semantic versioning (see
`wellmanifest/semver`), publication authority, hosted CI billing.

<!-- docs:section evidence -->
## Evidence

Observed 2026-10-30 across eight `maskservice` repositories bumped in one pass:

- Six pull requests passed `onedev/local-verify` and were merged by the
  independent Validator.
- Two (`maskservice/workshop#12`, `maskservice/fleet#17`) failed with
  `NATIVE_ADOPTION_DIFF_SCOPE_MISMATCH: VERSION`. Their profiles admit only the
  paths listed in `applicationPaths`, and `VERSION` was not listed. Both were
  finally merged manually by the owner.
- The same gap was already patched once per repository for `errors/*`
  (`onedev-agent` ticket-696) and again for `VERSION` (tickets 760 and 761).
- Workstream ownership of `VERSION` differs between repositories
  (`governance` in `maskservice/update`), so the first allocation attempt with
  the usual workstream was refused with `GOV-WORK-START-001`.
- Hosted GitHub Actions jobs never started because of an account billing
  failure; this is unrelated to the class proposed here.

<!-- docs:section content -->
## Content

Proposed class `release-bump`, declared once in the locked manifest instead of
in each repository's profile:

1. **Paths.** Exactly `VERSION`, plus the ticket carrier files already accepted
   by the gate. A repository may add `CHANGELOG.md` explicitly; no globs.
2. **Value.** `VERSION` is one line, matches the repository's declared scheme,
   and is a strict increment of the version on the accepted base (patch by
   default; a larger step needs the ticket intent to say so).
3. **Integrity.** Not a symlink, no other file changes, accepted base equals the
   merge base, and the native baseline is already admitted (never during initial
   adoption).
4. **Ownership.** The manifest names the workstream that owns `VERSION`, so
   ticket allocation and the gate agree.
5. **Authority.** Unchanged: the class only widens what the diff-scope check
   accepts. Verification, independent approval and merge stay with OneDev and
   the Validator.

Effect: a version bump needs no profile edit, no protected canary per
repository and no manual merge.

<!-- docs:section limitations -->
## Limitations

- Not implemented or reviewed; no gate reads this class yet.
- Only the observed `maskservice` cases were examined; other schemes (calendar
  versions, multiple version files) are not covered.
- Changing the shared gate requires independent source approval and a protected
  canary, as for ticket-696.

<!-- docs:section next_actions -->
## Next actions

- Owner decision on whether the class belongs in `wellmanifest/new-project`.
- If accepted, a separate implementation ticket for the gate and manifest
  schema, with regressions for symlink, non-increment and initial-adoption
  smuggling cases.

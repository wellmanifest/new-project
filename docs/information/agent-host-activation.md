---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "agent-host-activation",
  "kind": "information",
  "version": 1,
  "title": "Agent host activation and its enforcement boundary",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-08",
  "updated": "2026-09-08",
  "review_after": "2026-10-08",
  "source_revision": "bf3099667babd14ee778917d911d6c6bad45dcab",
  "affected_repositories": [
    "wellmanifest/new-project"
  ],
  "evidence": [
    "https://github.com/wellmanifest/new-project/blob/bf3099667babd14ee778917d911d6c6bad45dcab/scripts/install-agent-hosts.sh",
    "https://github.com/wellmanifest/new-project/blob/bf3099667babd14ee778917d911d6c6bad45dcab/tests/agent-hosts.test.sh"
  ]
}
---

# Agent host activation and its enforcement boundary

<!-- docs:section purpose -->
## Purpose

Activation must report the actual local hook state and preserve existing user
instructions. A successful installer is a local configuration observation;
it is not proof of protected publication or universal IDE/LLM conformance.

<!-- docs:section scope -->
## Scope

This contract covers `scripts/install-agent-hosts.sh`, shared through the
managed package, and its regression tests. It does not replace trusted CI,
validate signatures, attest source freshness, install all packs, or authorize
publication. The cross-repository audit remains owned by
[subactor/docs](https://github.com/subactor/docs/blob/main/architecture/analysis/wellmanifest-adoption.md).

<!-- docs:section evidence -->
## Findings and regression evidence

At source revision `bf3099667babd14ee778917d911d6c6bad45dcab`, `--check`
accepted an existing non-executable hook when `core.hooksPath` matched. The
new regression failed on that exact behavior before the fix. Code inspection
also identified swallowed producer failures in Bash process substitutions,
copying before all package sources were checked, and truncation of existing
Gemini/Claude instructions when adding the first managed pointer.

`tests/agent-hosts.test.sh` exercises disabled hooks without permission
mutation, malformed contracts without Git configuration mutation, missing
source files and package mappings without partial instruction overwrite, and
preservation plus idempotence of existing user instructions. These are local
behavior tests; actual GUI host sessions and Windows execution require
separate evidence.

<!-- docs:section content -->
## Required behavior

- Resolve contract and package enumeration successfully before activation.
  Propagate command failures explicitly, including when the installer function
  is called inside a Bash conditional that suppresses implicit `errexit`.
- Preflight every required mapping and source before bootstrap writes.
  In-place activation checks all required files before changing permissions.
- `--check` is read-only and rejects a hook without executable permission or
  an incorrect effective `core.hooksPath`.
- Gemini and Claude pointers append to existing instructions once. A named
  managed Cursor rule remains a managed replacement file.
- Filesystem write failures return failure. Preflight does not promise an
  atomic transaction against disk errors or concurrent filesystem changes.

<!-- docs:section limitations -->
## Limits of enforcement

A user can disable local hooks, use `--no-verify`, change local policy, or
publish through another client. Therefore independent protected checks of the
exact candidate, current base, trusted policy and tested merge result remain
mandatory. Installer success must never be labeled bypass-resistant enforcement.
Content integrity, approved revision freshness, host applicability and actual
cross-host invocation are separate observations. `--user --check` currently
reports that user pointers are not inspected; it is not a conformance result.

<!-- docs:section next_actions -->
## Verification and adoption

Run `bash tests/agent-hosts.test.sh` and the managed governance gate. Preserve
required Linux and Windows publication checks. Adoption happens through a new
immutable published package revision and the normal bounded adopter change;
changing this source does not update existing clones or deployed executors.
After adoption, run activation followed by `--check` in the actual clone.
Rollback uses a protected corrective change; preserve user-authored content.

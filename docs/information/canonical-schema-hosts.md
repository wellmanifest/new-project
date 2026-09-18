# Canonical Schema Hosts and Schema Immutability

```dsl
DOCUMENT CANONICAL_SCHEMA_HOSTS
VERSION 1
LANGUAGE EN
MODE NORMATIVE
PURPOSE "Fleet-wide schema host resolution, migration aliases, and semantic immutability"
POLICY "../../POLICY.md"
```

## Canonical Schema Host

The canonical URI host for all Wellmanifest JSON Schemas is:

```text
https://wellmanifest.com/schemas/<domain>/<name>/v<N>
```

Examples:
- `https://wellmanifest.com/schemas/ssot/decision/v1`
- `https://wellmanifest.com/schemas/validation-attestation/v1`
- `https://wellmanifest.com/schemas/new-project/agent-hosts/v1`

## Fleet Namespace Routing and Backward-Compatibility Aliases

Historical schemas developed prior to this standard used several disparate hostnames. The following routing matrix defines canonical status, resolution, and migration policies:

| Namespace | Status | Target / Action |
| --- | --- | --- |
| `https://wellmanifest.com/schemas/*` | **CANONICAL (HOME)** | Primary authoritative endpoint for all schema contracts. |
| `https://wellmanifest.dev/schemas/*` | Supported Alias | Resolves via 301 redirect to `wellmanifest.com/schemas/*`. |
| `https://wellmanifest.org/schemas/*` | Legacy Frozen | Retained for immutable pinned versions (e.g. `worktrees/v5`). Future revisions migrate to `.com`. |
| `https://github.com/wellmanifest/*` | Legacy Alias | Subproject and repository-relative `$id`s retained for backward-compatible resolution. |
| `urn:wellmanifest:*` | Legacy Alias | URN-based identifiers mapped to equivalent `.com` schemas. |
| `https://json-schema.org/*` | External Standard | Meta-schemas (`draft/2020-12/schema`, `draft-07/schema`). |

## Schema Immutability Invariant

To resolve fleet divergence where an unversioned `$id` validated differently across adopters depending on installed package version (Issue #348):

1. **Semantic Invariance**: A schema published under a specific `$id` and document identifier (e.g. `new-project.intent/v3`) is **immutable**. Its validation semantics, required fields, and allowed transitions must never be altered in place.
2. **Version Bump on Semantic Change**: Any change to a schema that affects validation outcomes (adding/removing required properties, changing enum sets, tightening constraints) MUST bump the document identifier version (e.g. from `new-project.intent/v3` to `new-project.intent/v4`), or introduce revision/content addressing into the `$id`.
3. **Fail-Closed Gate**: Governance validators reject changes where schema content changes under an unchanged `$id` and unchanged package version.

## Supported Version Window and Fleet Upgrade Path

Adopters in the fleet converge toward the active supported package window:

- **Active Supported Line**: `new-project >= 0.20.0`
- **Maintenance Line**: `new-project 0.18.10`
- **Deprecated Lines**: `< 0.18.10` (scheduled for retirement via `goal governance adopt`)

Adopters upgrade using immutable signed receipts and exact-head validation rather than partial manual file edits.

# Ticket 421: Include target packaging declarations in native adoption plan (#548)

- **ID**: ticket-421
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-10

SESSION_EXECUTION_AUTHORIZATION: the user requested continuing autonomous testing, merging, fixing, optimization, and improving `wellmanifest/*` standards.

## Cel i Zakres

Ensure native standard adoption planning (`--check --allocation-plan`), drift inspection (`--check`), and upgrades (`--upgrade`) in `scripts/create_adoption_lock.py` detect, validate, and surgically project target-owned packaging declarations (`pyproject.toml`, `package.json`) declared by `.governance/agent-hosts.json`, closing Issue #548 without adding target-owned markers to `managedFiles` or bypassing ownership/fencing guards.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `--check --allocation-plan` and `--upgrade` project surgical byte-preserving `standard` and `revision` updates for existing `pyproject.toml` and `package.json` declarations, include them in `allowedPaths`, `target.files`, and `files` (`strategy: "generated"`), preserve `managedFiles` hashes unchanged, and pass both `agent_host_check.py` (`GOV-PACKAGING-*`) and `./project/governance-check.sh` in a real historical-adopter fixture.
- [x] AC-02: `--check` distinguishes internally inconsistent upgrades and invalid/missing packaging declarations from `up-to-date` adoptions, and negative tests verify fail-closed refusals for missing authority, stale target state, conflicting/missing workstream ownership, unmanaged local edits, and malformed/unbound declarations.
- [x] AC-03: Adoption regression suites, `./project/governance-check.sh`, and `wellman check` pass.

## Ryzyka i Uwagi

- Risk 1: Re-serializing `pyproject.toml` or `package.json` could alter comments, formatting, or unrelated package metadata; mitigated by lexical span replacement of only `standard` and `revision` string literals followed by full `tomllib.loads` / `json.loads` AST equivalence verification.
- Risk 2: Fresh bootstrap checkouts before native adoption carry bare `pyproject.toml` without `[tool.wellmanifest]`; mitigated by scoping native packaging declaration projection to existing native adoptions where `.governance/manifest.lock.json` is present outside `--bootstrap-native-adoption` / `--migrate-wellman-scaffold`.

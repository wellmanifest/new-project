# Standard Upgrade — 3-layer auto-propagation

## Overview

When a new `wellmanifest/new-project` release is published, all adopting
repositories receive the update through three independent layers:

```
Release v0.20.34
  ├── Layer 1: Pre-commit hook  →  auto-upgrade on next commit (local)
  ├── Layer 2: CI reusable gate →  fail-fast on outdated standard (CI)
  └── Layer 3: Org-wide auto-PR →  upgrade PR in all 100+ repos (batch)
```

## Layer 1 — Pre-commit hook (local, before development)

The pre-commit hook checks the installed `wellman` package
version against `pyproject.toml [tool.wellmanifest].standard`. On mismatch,
it auto-installs the correct version before the developer starts work.

```bash
# .githooks/pre-commit (installed by goal bootstrap)
REQUIRED=$(python3 -c "import tomllib; ...")
INSTALLED=$(python3 -c "from wellman import __version__; ...")
if [ "$INSTALLED" != "$REQUIRED" ]; then
  uv pip install "wellman==${REQUIRED}"
fi
```

**Result:** Developer cannot commit with outdated standard.

## Layer 2 — CI reusable workflow (GitHub Actions)

Adopter repos reference the governance gate as a reusable workflow:

```yaml
# .github/workflows/governance.yml
jobs:
  governance:
    uses: wellmanifest/new-project/.github/workflows/governance-gate-reusable.yml@v0.20.34
    with:
      target-root: .
```

**Result:** CI fails if governance check doesn't pass. Zero config in repo.

## Layer 3 — Org-wide auto-PR (batch propagation)

On new release, `propagate-standard.yml` scans all orgs for adopters and
creates upgrade PRs:

```
wellmanifest/new-project release v0.20.34
  → Scans semcod/*, subactor/*, autogrammar/*, ...
  → Creates PR "chore: upgrade wellmanifest standard to 0.20.34"
  → PR runs governance gate → auto-merge if green
```

**Result:** All repos receive upgrade within 24h of release.

## Migration from vendored copy

```bash
# Before (187KB governance_check.py copied to each repo):
.governance/governance_check.py   # 4343 lines, vendored

# After (1KB wrapper + package dependency):
uv add --group governance wellman==0.20.34
# .governance/governance_check.py is no longer needed
```

## Package: wellman

```bash
uv add --group governance wellman
python -m wellman check --root .
wellman check --root .
```

Source: `packages/wellman/` in this repository.

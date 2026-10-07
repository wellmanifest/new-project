# wellman

The runtime package version is synchronized with the immutable Wellmanifest
standard release. For the current release, install `wellman==0.20.46` when
the adopted governance manifest pins standard `0.20.46`. The corresponding
release is published by the `wellman-v0.20.46` trusted-publishing workflow.

Wellmanifest governance gate runtime — deterministic policy-as-code checker.

Distributes `governance_check.py` as an installable Python package instead of
vendoring 187KB+ scripts into every adopting repository.

## Install

```bash
uv add --group governance wellman
# or
pip install wellman
```

## Usage

```bash
# CLI
wellman check --root /path/to/repo

# Module
python -m wellman check --root /path/to/repo
```

```python
# Programmatic
from wellman.check import run_check
exit_code = run_check(root="/path/to/repo")
```

## Pre-commit hook integration

```bash
# In .githooks/pre-commit:
REQUIRED=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['tool']['wellmanifest']['standard'])")
uv pip install "wellman==${REQUIRED}" --quiet
python -m wellman check --root . --preflight
```

## CI reusable workflow

```yaml
# .github/workflows/governance.yml
jobs:
  governance:
    uses: wellmanifest/new-project/.github/workflows/governance-gate-reusable.yml@v0.20.32
```

## Source

Part of [wellmanifest/new-project](https://github.com/wellmanifest/new-project).

## Offline packaging regression

The source packaging regression builds a real wheel, installs it in a clean
virtual environment and exercises the installed runtime outside the source tree.
It uses preinstalled build tools and refuses index access during build/install.
Prepare `setuptools>=68.0` and `wheel` in the independently provisioned CI
runtime first; the hosted test job pins `setuptools==80.9.0` and `wheel==0.45.1`.
The deployed OneDev executor already includes these versions.

```bash
python3 tests/wellman-offline-build.test.py
PIP_NO_INDEX=1 bash tests/wellman-package.test.sh
```

The first command checks fail-fast behavior in a real environment without build
tools. Missing prerequisites produce `WELLMAN-BUILD-TOOLS-MISSING` before wheel
building. The packaging test keeps the real build and runtime checks and can run
with the candidate executor's network disabled. Installing the runtime package
does not require these source-test build tools.

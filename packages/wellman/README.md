# wellmanifest-governance

The deterministic New Project checker has a distinct package, module and console.

| Role | Distribution | Module / command |
| --- | --- | --- |
| Static governance gate | `wellmanifest-governance` | `wellmanifest_governance_runtime` / `wellman-governance` |
| Full standards and execution runtime | canonical `wellman` | `wellman` / `wellman` |

The physical source directory remains `packages/wellman/src/wellman` for the
existing bundle generator. Setuptools maps it only to the installed
`wellmanifest_governance_runtime` namespace; the wheel never installs a `wellman` module
or console script.

Install from an independently reviewed immutable New Project revision in a
dedicated tool environment:

```bash
uv tool install 'git+https://github.com/wellmanifest/new-project.git@<approved-full-SHA>#subdirectory=packages/wellman'
wellman-governance check --root /path/to/repo --json
python -I -m wellmanifest_governance_runtime check --root /path/to/repo --actor ci
```

The renamed PyPI distribution needs its own matching trusted publisher. Source
publication does not establish publisher enrollment, a registry release or a
fleet upgrade. Existing legacy `wellman` wheels and protected pins are unchanged.

Delivered CI selects only the new governance entry point or the legacy
`wellman.check:main` installed from its approved immutable pin. The unrelated
`wellman.cli:main` package is not a fallback. Candidate modules and inherited
Python import paths remain excluded.

For development commands, select the approved full runtime and use
`wellman run --root <ticket-checkout> -- python -m pytest ...` or an enrolled SDK.
This checker does not launch or intercept those commands. Its JSON report labels
runtime enforcement `not_checked`; static PASS grants neither execution nor
publication authority.

`sync_bundled.py --check` verifies the complete helper closure against `scripts/`.
The installed-wheel regression builds offline, checks namespace and command
ownership, preserves an unrelated Wellman installation and exercises the
delivered isolated CI gate bodies.

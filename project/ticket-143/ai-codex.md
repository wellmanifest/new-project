# Codex report

## Diagnosis

The Koru pilot materialized four managed files that its target `.gitignore`
excluded. Governance inspected the working tree and passed, but a normal commit
could not carry those files. Hosted pytest then also lacked clone-local hook
configuration and an exact PR base in a shallow checkout.

## Plan

1. Reject ignored managed targets before the adoption generator writes.
2. Activate the installed hook contract from the pytest lifecycle bridge.
3. Resolve and fetch the exact GitHub event base SHA when necessary.
4. Add deterministic regressions and validate the complete standard suite.

## Result

All three gaps are closed at the standard boundary. Ignored payloads are
reported before any write, hook activation changes only clone-local Git config,
and the GitHub event base is fetched by exact SHA before changed paths are
derived. Ruff, compileall and all deterministic Linux shell suites pass.

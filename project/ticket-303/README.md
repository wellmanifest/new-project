# Cached preflight current output errors

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Combine current invocation output-path and resolved-ticket writer failures with cached findings, summary and exit status. Keep legitimate cache reuse, warnings/timing and cache-disabled CI. Synchronize the existing bundled checker; no authority is supplied by advisory cache data.

## Acceptance criteria
- AC-01: Actual source/bundle CLI exposes unsafe report paths and writer/path failures while preserving cached warnings and later valid reuse.
- AC-02: Existing cache tests, native Linux/Windows, integration and installed wheel/parity gates pass.
- AC-03: Independent protected merge and standard v0.20.77 publication are verified.

## Bounds
S / 20 minutes; ten material files, three components, two existing interfaces (preflight CLI and Windows CI), zero dependencies. No cache key, ticket selection, schema identity, lease or approval policy changes; no foreign/frozen target mutations.

## CI fixture correction
The first head failed on clean Linux/Windows checkouts because the local-agent CLI fixture assumed an activated hook and origin/main. The refined fixture activates the real managed hook through child Git configuration environment and chooses an available explicit base (origin/main or a verified parent). It never edits repository configuration or skips either gate. Initial CI logs and the held head are preserved in private evidence.

The next Windows run exposed its shallow checkout: neither origin/main nor a parent commit was present. The Windows job now fetches full history, as the Linux job already does. The fixture now requires the verified origin/main base, without a parent or HEAD fallback. Both failed CI heads remain in the PR history and private evidence. A fresh clone also exposed the second public path introduced by the CI change; the refined bounded intent declares it within the existing policy limit.

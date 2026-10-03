# Catalog execution models and artifact boundaries

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Validate execution-model names, record types, levels and boolean effect flags before adoption conformance. Confine artifact file access to the canonical checkout; reject portable absolute/drive/parent escapes before hashing. Preserve valid models, metadata and confined paths. No hardware execution or effect authority.

## Acceptance criteria
- AC-01: Actual strict CLI and direct validator reject malformed models and escaping artifacts; valid declarations and confined files or symlinks pass.
- AC-02: Existing integration, native Linux/Windows, installed wheel and exact-head gates pass.
- AC-03: Independent protected merge and standard v0.20.76 publication are verified.

## Bounds
S / 25 minutes; eight material files, three components, one existing CLI contract, zero dependencies. No new bundled standard-pack module, schema identity, pack/profile semantics or foreign/frozen target changes. This does not claim resistance to arbitrary same-user concurrent path mutations.

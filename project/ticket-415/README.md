# Ticket 415: Anchor continuity transaction storage paths

- **ID**: ticket-415
- **Owner**: agent:codex-maskservice-np032
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-06

## Goal and scope

Deliver NP-042, the remaining original transaction confinement outcome of NP-032.
Hold validated journal/index parent namespaces throughout acquisition and effects;
preserve native Windows handle protection, regular private files and replay.
Material version 0.20.143 joins this fix. Foreign414 and its unique work remain.

## Acceptance criteria

- [ ] AC-01: Parent substitution cannot redirect reads/writes during waiting or transaction effects; existing concurrency/recovery and native Windows cases pass.
- [ ] AC-02: Source governance/full tests and genuine Goal publication pass; exact-head independent App approval and required CI precede merge.

## Session execution authorization

The user explicitly requests autonomous continuation, testing and protected merges.
NP-042 already exists under accepted NP-032. Prior source owner414 normally released
actual930/rev9, then managed work-start observed AVAILABLE before allocation.
No foreign workspace, policy, safety limit or managed consumer is changed.

## Validation

The old runtime failed8actual namespace substitution cases. Linux storage tests
now pass28cases with4Windows-only skips; the continuity CLI shell suite passes.
A positive distinct-parent commit/rebuild round trip also passes. Source governance
reports GOV-PASS with no warnings. Full canonical/Python and actual native Windows
CI plus independent exact-head App review remain required before merge.

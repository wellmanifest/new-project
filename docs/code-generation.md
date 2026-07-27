# JS/Node.js Code Generation

This document describes the Phase 9 code-generation boundary implemented in
`@office-dsl/codegen`. The package generates deterministic JS/Node.js artifacts
only from an approved `intent-contract.dsl.v1` snapshot. It does not generate
code directly from loose prompt text.

## Approval Gate

`assertDslApprovedForCodeGeneration(dsl)` validates the Intent/Contract DSL and
computes the code-generation hash from the approval-free DSL snapshot. Code
generation requires active `APPROVED` records from every Human1/Human2 party for
that exact current hash. Missing or stale approvals fail before any plan or code
is emitted.

## Allowed Target

The first bounded target is `node-esm-contract-module`:

- runtime: Node.js
- module format: ESM
- dependency policy: none
- filesystem policy: read-only fixtures
- network policy: disabled
- generated-artifact process policy: no child process
- output files: `package.json`, `src/contract-spec.mjs`, and
  `test/contract-spec.test.mjs`

The generated module has no dependencies, does not write files, does not call the
network, and does not use dynamic code execution.

## Implementation Plan

`createImplementationPlanFromApprovedDsl(dsl)` emits `codegen.node.v1` plan
steps with stable input DSL paths and output paths:

- extract the approved contract specification,
- emit dependency-free Node.js tests derived from the approved DSL hash and
  generated spec,
- emit a bounded package manifest.

The default timestamp is deterministic, so repeated generation from the same DSL
snapshot produces the same auditable plan.

## Generated Artifacts

`generateNodeCodeFromApprovedDsl(dsl)` emits:

- `package.json` with ESM metadata and no dependencies,
- `src/contract-spec.mjs` exporting the approved contract specification and a
  small summary helper,
- `test/contract-spec.test.mjs` with dependency-free Node assertions against the
  generated module.

Each generated file includes a SHA-256 hash. The generated contract spec includes
the approved DSL hash, approved parties, document metadata, parties,
deliverables, obligations, acceptance criteria, and source-reference labels.

## Generated Test Execution

`runGeneratedNodeTests(result)` writes the generated artifacts into a temporary
workspace and executes the generated Node.js test file with the current Node
runtime. It also checks that the generated source does not contain forbidden
dynamic/network/process APIs and that generated file contents still match their
recorded hashes.

## Verifier Input

Both generation and test execution produce `codegen.verifier-input.v1` metadata:

- approved DSL hash,
- target id,
- generated file paths and hashes,
- approved parties,
- generated test results once tests have run.

This gives the Python semantic verifier a stable future integration point. The
current milestone validates the package-level boundary; runtime, CLI, backend,
UI, and Python-verifier wiring remain open.

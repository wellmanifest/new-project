# Test Generation From DSL

This document describes the Phase 8 test generation boundary implemented in
`@office-dsl/testgen`. The package turns an Intent/Contract DSL snapshot into
typed test-generation inputs, generates deterministic test specifications, and
verifies coverage against acceptance criteria.

## Test-Generation DSL Inputs

The `intent-contract.testgen-input.v1` document is a typed list of
`TestGenerationItem` entries. Each item has an `id`, a `category`, a `text`, and
traceability (`sourceDslPaths`, `sourceIds`). The supported categories are:

- `REQUIREMENT`
- `INVARIANT`
- `ACCEPTANCE_CRITERIA`
- `PROHIBITED_BEHAVIOR`
- `EXPECTED_OUTPUT`
- `ERROR_HANDLING`
- `SECURITY_POLICY`

`validateTestGenerationInput` enforces the version, unique non-empty ids, known
categories, non-empty text, and array-typed source references.

## Extraction From Intent/Contract DSL

`extractTestGenerationInput(dsl)` maps a validated Intent/Contract DSL snapshot
into inputs deterministically and never invents entries that are absent from the
DSL:

- `REQUIREMENT` from `intents[].description` and `obligations[].description`
- `INVARIANT` from `conditions[].description`
- `ACCEPTANCE_CRITERIA` from `acceptanceCriteria[].description`
- `PROHIBITED_BEHAVIOR` from `exclusions[].description`
- `EXPECTED_OUTPUT` from `deliverables[].description`
- `ERROR_HANDLING` from `risks[].description`
- `SECURITY_POLICY` from prohibited/risk statements that mention
  security-sensitive behavior (secrets, keys, shell, injection, unauthorized
  access, deletion, traversal, escalation, exfiltration)

Only valued fields are extracted, and the resulting `dslHash` binds the inputs
to the exact DSL snapshot they came from.

## Generated Specifications

- `generateUnitTestSpecs(input)` emits a unit spec for every acceptance
  criterion, requirement, invariant, and expected output.
- `generateTestSuite(input)` adds integration, API, E2E, security, and
  error-handling specs where the corresponding inputs exist.

Every `TestSpec` records `mapsToItemIds`, `categories`, `dslPaths`, and a
given/when/then description so each generated test maps back to the DSL inputs
that justify it.

## Coverage Verification

`verifyTestCoverage(input, specs)` produces a `testgen.coverage.v1` report with:

- `coveredItemIds` and `uncoveredItems`,
- `uncoveredAcceptanceCriteria` and an `acceptanceCriteriaCovered` flag,
- a `coverageRatio`,
- a `testgen.verifier-input.v1` object that includes `uncoveredItemIds` and
  `uncoveredAcceptanceCriteriaIds` so a downstream verifier can gate on
  uncovered acceptance criteria.

`renderTestPlanMarkdown(input, specs, coverage)` renders a human-readable,
traceable test plan with a coverage table and an uncovered-inputs list.

## Boundary

The generator is deterministic and read-only over the DSL. It produces
specifications and coverage reports; it does not execute generated code and does
not create tests from loose prompt text. Executable code generation is tracked
separately in Phase 9.

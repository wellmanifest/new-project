# Python Semantic Verifier

This document describes the mock-safe Phase 10 semantic verifier boundary in
`verifier/office_dsl_verifier` and the TypeScript runtime bridge in
`@office-dsl/dsl-runtime`.

## Input

The semantic verifier accepts structured input through
`python -m office_dsl_verifier --semantic-input <file>`:

- `original_nl`: the original natural-language command, message, or transcript
  excerpt,
- `approved_dsl`: the approved `intent-contract.dsl.v1` snapshot,
- `rendered_document`: Markdown or text rendered from the DSL,
- `codegen_verifier_input`: `codegen.verifier-input.v1` metadata,
- `testgen_verifier_input`: `testgen.verifier-input.v1` metadata.

All fields are optional so callers can validate one artifact boundary at a time.
The default mode is `mock` and stays deterministic/offline.

## Report

The verifier returns `semantic-verifier.report.v1` with:

- `verdict`: `PASS`, `FAIL`, or `NEEDS_REVIEW`,
- `score`, `recommended_action`, and explanation,
- structured findings with kind, DSL path, message, and severity,
- `missing_requirements`, `contradictions`, `unauthorized_assumptions`,
  `document_mismatches`, `code_mismatches`, and
  `uncovered_acceptance_criteria` arrays.

Required missing fields, unresolved conflicts, rendered-document mismatches, and
failed generated-code tests block with `FAIL`. Unapproved assumptions and
uncovered generated-test acceptance criteria require review unless another error
already blocks the report.

## Checks

The mock semantic verifier validates:

- source quotes from DSL fields against the original NL text,
- required `MISSING` or `INCOMPLETE` fields,
- unresolved DSL conflicts and `CONFLICTING` fields,
- unapproved `ASSUMED` fields,
- rendered document text against DSL values for title, parties, deliverables,
  obligations, acceptance criteria, payments, deadlines, conditions, and
  exclusions,
- failed generated-code test results from `codegen.verifier-input.v1`,
- uncovered acceptance criteria from `testgen.verifier-input.v1`.

The verifier is deterministic and does not call external services in default
verification.

## TypeScript Runtime Bridge

`runPythonSemanticVerifier(input)` writes the semantic input to a temporary file,
executes `python -m office_dsl_verifier --semantic-input ...`, parses the JSON
report, and removes the temporary workspace.

`Runtime.createWithPythonSemanticVerifier(dsl, input)` runs that bridge before
creating the session, stores the report under `audit.verifier`, and gates
`FAIL` or `NEEDS_REVIEW` reports at `VERIFICATION_FAILED`. A gated session cannot
execute until it is regenerated or otherwise resolved.

## OpenRouter/LiteLLM Boundary

Non-mock mode requires `OPENROUTER_API_KEY` and the optional `litellm` dependency.
The current test suite validates that this configuration is required before
leaving mock mode, but it does not execute a live OpenRouter/LiteLLM semantic
verification request. Live provider validation remains an open Phase 10 item.

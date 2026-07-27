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

Non-mock semantic verification is available through LiteLLM/OpenRouter and must
be enabled explicitly. The default `verify` flow stays deterministic and offline.

Setup:

```bash
python -m pip install -e verifier[openrouter]
export OPENROUTER_API_KEY=...
export OPENROUTER_MODEL=openrouter/openai/gpt-4.1-mini
python -m office_dsl_verifier --semantic-input path/to/semantic-input.json --mode openrouter
```

The OpenRouter adapter sends the semantic verifier input as JSON, asks for a
`semantic-verifier.report.v1` JSON object, parses the response through the
Pydantic report model, and rejects malformed provider output.

Validation coverage:

- default tests prove that non-mock mode refuses to run without
  `OPENROUTER_API_KEY`,
- default tests monkeypatch `litellm.completion` and prove that the OpenRouter
  semantic adapter sends the expected model, API key, response format,
  temperature, and semantic input,
- an optional live smoke test is available with:

```bash
RUN_OPENROUTER_SEMANTIC_TEST=1 OPENROUTER_API_KEY=... python -m pytest verifier/tests/test_verifier.py -q
```

The optional live smoke test is intentionally opt-in so default repository
verification never depends on network access or secrets.

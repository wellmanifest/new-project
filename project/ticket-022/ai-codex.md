---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-022
---
# Participant: codex (AI agent)

## Understanding

The requested evaluator must extend the existing intent, governance and
code-change evidence model rather than create a competing score. It needs two
layers: non-compensable hard gates and independent review dimensions. Every
result is valid only for exact Git and contract hashes. The first deliverable
is the portable validation boundary; `todo2code` can later produce richer
semantic evidence against the same schema.

## Execution plan

1. Add normative `C-EVALUATION-001..010` rules and resolve publication in
   favour of ticket branches and pull requests for implementation.
2. Define `t2c.change-evaluation/v1` as the single machine contract.
3. Implement `scripts/runtime.sh` as a Bash entrypoint executing a
   TypeScript-compatible, dependency-free Node runtime.
4. Validate policy rule presence, hashes, exact Git bindings, intent scope,
   criterion evidence, approval freshness, hard gates and derived verdict.
5. Emit canonical JSON plus a concise Markdown view with stable diagnostics.
6. Add the runtime/schema to the adoption package and test positive and
   adversarial fixtures.

## Actual changes

- User supplied and approved the detailed Change Evaluation Contract on
  2026-08-05; implementation started within the bounded intent.
- Added the normative change-evaluation flow and exact rules 001-010 to the
  existing policy instead of creating a parallel work-ranking language.
- Added the canonical v1 JSON schema and a Bash entrypoint containing a
  dependency-free TypeScript-compatible Node runtime.
- Runtime verifies policy completeness, exact contract hashes, Git range and
  commit/path sets, intent scope, criterion evidence, approval freshness and
  independence, hard gates and derived verdict/completion.
- Runtime emits deterministic JSON and Markdown; a valid `BLOCKED` report exits
  non-zero, so validation consistency cannot be mistaken for merge permission.
- Added both artifacts to immutable adoption and moved adversarial coverage
  into the existing required governance CI test.
- All hub test contracts pass.
- PR #31 passed Linux and Windows CI, received exact-head Validator App
  approval and merged as `166ebeaa45903822329645328f61317131821935`.

## Blockers

- None.

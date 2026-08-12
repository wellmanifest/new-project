---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-067
---
# Participant: codex (AI agent)

## Understanding

Ticket 066 correctly centralized stable `GOV-*` messages, short remediations
and optional runbooks, but it stopped before an incident-specific refactoring
contract. The supplied Diagit report demonstrates the missing layer: one
finding may be a detector false-positive, another is a silent omission, a
third requires an explicit layout contract, and release work must wait behind
correctness blockers. A prose list alone does not give an LLM or todo2code a
validated scope, dependency graph or acceptance mapping.

The standard therefore needs a target-owned JSON DSL that separates observed
facts from applicability assumptions and desired outcomes. A deterministic
tool must validate and render it before any LLM reads it. Todo2code can then
analyze a canonical Markdown projection and return a hash-bound advisory
overlay; that overlay supplies hints but never changes authority or approved
paths.

## Execution plan

1. Record the target-vs-reusable storage rules and versioned DSL shape.
2. Implement dependency-free structural and semantic validation.
3. Render a canonical LLM brief and todo2code task/TODO projection.
4. Import todo2code diagnostics/plans into a digest-bound advisory overlay and
   reject path, criterion or provenance inconsistencies.
5. Add Diagit-shaped positive/negative fixtures and adopted-package coverage.
6. Run focused/full tests plus an actual deterministic todo2code pipeline,
   publish one ticket PR and retain `PUBLICATION` until trusted merge.

The rule-enforcement audit must also discover the new deterministic analyzer;
that existing audit script is therefore part of the bounded adapter component.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Classified the work as a distinct `integration` feature. It does not overlap
  ticket-065 implementation paths and does not release the blocked v0.15.0.
- Verified that current new-project only provides diagnostics v2 and Markdown
  runbooks, while todo2code already exposes deterministic task extraction,
  intent diagnostics and grounded `t2c.code-change-plan/v1` proposals.
- Added `new-project.remediation-intent/v1`, a dependency-free semantic
  validator, canonical LLM/todo2code renderers and a digest-bound advisory
  importer. READY intents now fail on unresolved ownership/evidence, unsafe
  path scope, false-positive findings without exclusions, cycles, incomplete
  verification, unsafe user-state actions and release ordering gaps.
- Registered `GOV-REMEDIATION-001/002/003`, linked their reusable runbook and
  shipped the schema/template/analyzer through the immutable adoption package.
- Added Diagit-shaped regressions for OpenRouter detector-source false
  positives, unreadable selected paths, layout ambiguity, missing inventory,
  dirty worktree preservation and release drift. Negative fixtures also cover
  stale analysis, todo2code scope expansion and unauthorized deletion.
- Ran the complete local Linux CI contract and Ruff successfully. A real
  deterministic todo2code 0.5.0 pipeline consumed the rendered TODO, produced
  a code-change plan, and the importer correctly surfaced its P1-to-P2
  priority drift as a digest-bound LLM hint.
- Confirmed the target wrapper cannot run directly in the source Governance Hub
  because it intentionally expects adopted `.governance/*` paths. Hub-native
  deterministic validators and adoption/gate fixtures pass; this pre-existing
  source-vs-adopted entrypoint mismatch is not hidden as successful execution.

## Blockers

- Independent exact-head review and hosted Windows CI remain publication
  gates. Advisory model output is not approval.

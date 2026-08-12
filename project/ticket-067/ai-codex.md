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

## Blockers

- None inside the recorded intent. Independent exact-head review remains a
  later publication gate and advisory model output is not approval.

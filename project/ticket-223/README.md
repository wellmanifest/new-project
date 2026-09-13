# Ticket 223: Preserve registration inventory history

- **ID**: ticket-223
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-13
- **GitHub Issue**: https://github.com/wellmanifest/new-project/issues/337

SESSION_EXECUTION_AUTHORIZATION: the user requested continued standard fixes and protected publication. Normal scoped allocation admitted exactly the checker, regression suite and existing canonical document.

## Goal and scope

Retain observed checkout identity across snapshots so an orphan cannot disappear into a complete report. Require prior registration and a matching retained terminal request before inventory retirement. The checker remains read-only and does not authenticate receipts or grant deletion authority.

## Acceptance criteria

- AC-01: Missing/relabelled orphan, changed known path/branch and lost active/blocked checkout fail; resolved unknown observations and valid terminal retirement pass.
- AC-02: Registration/work-start and governance gates pass, followed by independent publication and ownership-safe retirement of this delivery.

Canonical result: [work registration](../../docs/information/work-registration.md). Packaging, mandatory installation and external controller effects remain in parent #330.

## Validation

All 41 registration tests and all 27 work-start tests pass. The new cases produced 10 failing subcases on the accepted source before correction. The source-hub CI manifest and pinned Docs checker pass. A declared 40-minute estimate exceeded the source profile's 30-minute active-work limit; the bounded implementation estimate is corrected to 20 minutes. Source publication still requires the protected exact-head gates and independent Validator.

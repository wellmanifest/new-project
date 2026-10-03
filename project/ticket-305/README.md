# Ticket 305: Require a resolved pytest governance base

- **ID**: ticket-305
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-03

## Outcome and scope
Stop the adopted pytest lifecycle before running the gate or product tests when no explicit, event or verified upstream Git base resolves. The existing fallback to HEAD can hide committed changes. Preserve valid base sources, collect-only, hook activation and event fetching; exercise actual Git and lifecycle behavior on Linux and Windows. Publish standard 0.20.79 through Goal after protected merge.

## Acceptance criteria
- [ ] AC-01: Missing-base and actual lifecycle regression fail before the fix and pass after; configured/event/upstream bases and collect-only remain supported.
- [ ] AC-02: Integration, full native and exact-head Linux/Windows/OneDev checks pass before independent review.
- [ ] AC-03: Independent protected merge and Goal-managed v0.20.79 release are verified.

## Boundaries and risks
Projects without a known base must configure WELLMANIFEST_BASE_SHA or fetch their target branch. No new runtime dependencies or authority grants. Intent bounds nine material files and three components. Raw logs remain in private external receipt storage. Session execution authorization covers this scope; merge approval remains independent.

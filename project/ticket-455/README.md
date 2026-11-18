# Ticket 455: Bounded ignore rules for first native bootstrap

- **ID**: ticket-455
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-18

SESSION_EXECUTION_AUTHORIZATION: the user authorized continuing repairs, testing and protected publication. NP-050 / #637 is the bounded prerequisite repair for first-adoption trackability. The downstream application ticket remains in its own repository. Native allocation and writer check bind this session to ticket-455, F1/R1; independent publication remains required.

## Cel i Zakres
Add an explicit exact-base and root-ignore digest plan to first native bootstrap. Preserve existing bytes and append only exact ignored managed/required-seed leaves with traversable parents. Keep default refusal and exclude ordinary upgrades, arbitrary source paths and operational state.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Real Git bootstrap check makes no changes; applying an exact plan preserves unrelated ignores and admits native first allocation.
- [x] AC-02: Stale state, duplicate/unsafe paths, unsupported plans, symlinks and excluded parent directories refuse without effects.
- [ ] AC-03: Scoped tests, required governance and independent exact-head publication pass; standard release is versioned.

## Ryzyka i Uwagi
Broad unignore rules could expose local data. Accept only literal leaf paths already selected by the bootstrap package, with current committed root ignore bytes and no excluded parents. Never negate a directory or wildcard.

Delivery estimate correction: the initial M/80 estimate was excessive for the concrete owner slice. The 87-line adopter change and its local validation completed within about ten minutes (00:50–01:00 UTC). S/30 covers this bounded change; eight implementation paths and all interface/component/dependency limits remain unchanged. Downstream adoption, application repair and hardware selection remain separate work.

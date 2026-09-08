# Ticket 199: Default-branch contribution attribution

- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION

SESSION_EXECUTION_AUTHORIZATION: user requests continuation, repairs, tests and protected GitHub publication of the remaining coordination safeguards.

## Acceptance criteria

- [x] AC-01: Inherited main paths do not implicate an independent writer; actual dirty/committed competing contributions still block, with conservative handling of unavailable or divergent Git observations.
- [ ] AC-02: Package and governance tests pass; publish the material fix with its version through independent protected review and immutable release.

## Risks

The local checker uses observed remote refs and never fetches, grants merge approval, removes another checkout or bypasses required checks. Pending merge conflicts remain visible as checkout state; only conflicts between both writers are attributed to their pair.

## Validation

The old implementation failed four independently reproduced attribution cases. The updated overlap suite, pending-merge cases, adoption lock, host activation and governance validator suites passed. The new suite also preserves rename/modify conflicts. Full publication checks and independent review are pending.

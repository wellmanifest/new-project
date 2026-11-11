# ticket-427: Harden v0.20.146 audit findings and auto-wire ticket-index merge driver

- **ID**: ticket-427
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: explicit owner authorization to execute `wellmanifest/new-project#600` (`v0.20.146` hardening + `project/TICKETS.md` merge-driver auto-wiring), synchronize bundled Wellman assets and `policy-dsl.lock.json`, add regression coverage, and prepare release `0.20.146`.

## Acceptance criteria

- [x] AC-01: Harden `work_continuity` (`os.O_WRONLY | os.O_APPEND`), `branch_lifecycle_check::require_ref` (`@` rejection), `remediation_intent::_analyze_criterion_coverage` (lowercase plan corpus normalization), `ticket_restoration::write_new` (destination-filesystem staging), `work_start_check::bootstrap_owned_paths` (end-of-proof dirty/payload stability), `idle_takeover` (`O_NOFOLLOW` lock verification and pre-replace idle/CAS re-observation), and `project/new-ticket.sh` (collision-resistant default `WRITER_SESSION`).
- [x] AC-02: Harden `governance_check.py` (and synchronized bundled Wellman copy) to validate historical `intent.json` via `validate_intent_value`, reject symlinks and bound size/containment on `**/__init__.py` scans, and restrict `legacy_base` adoption lock exemption strictly to absent base `package-manifest.json`.
- [x] AC-03: Harden `policy_dsl_check.py` (with synchronized `POLICY_DSL_LOCK` and `governance/policy-dsl.lock.json` SHA-256) to validate `VARIABLE ... DEFAULT` literal scalar types and reject duplicate Policy DSL `DOCUMENT` fences in `extract_markdown`.
- [x] AC-04: Auto-wire `merge.ticket-index.driver` and `merge.wellmanifest-ticket-index.driver` idempotently in `scripts/install-agent-hosts.sh` when `ticket_index_merge_driver.py` is present, verify all 13 `#600` audit items in `tests/governance-v146-regressions.test.py`, and bump standard/package version to `0.20.146`.

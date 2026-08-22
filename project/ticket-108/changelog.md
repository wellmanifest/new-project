# Ticket Changelog (ticket-108)

## [0.2.0] - 2026-08-23

- The managed adopter workflow gained `governance / enforce`, which runs the
  `.governance/governance_check.py` every adopter already carries.
- `scripts/audit_diagnostics.py` scans `.githooks`, so `GOV-AGENT-HOST-001..003`
  could be registered; the catalog holds 77 codes.
- `scripts/audit_rule_enforcement.py` knows `scripts/agent_host_check.py`, and
  `C-HOST-001..003` map its codes; 178 rules, 0 unmapped, 0 unclaimed.

## [0.1.0] - 2026-08-23

- Initial governance scaffold created.
- No human participant identity or content was generated.

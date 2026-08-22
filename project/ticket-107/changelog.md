# Ticket Changelog (ticket-107)

## [0.2.0] - 2026-08-22

- `governance/package-manifest.json` ships the host instruction files, the
  fail-closed hook, the host contract and its validator as managed files, so
  `GOV-SYNC-001` pins them in every adopter.
- Added adopter templates for `CLAUDE.md`, `GEMINI.md` and the Cursor rule.
- Rewrote `scripts/install-agent-hosts.sh`: contract-driven file list, `--check`,
  and an in-place activation distinct from a bootstrap into another checkout.
  This fixes the `cp` "same file" failure that kept `core.hooksPath` unset.
- Both fixtures derive from their source of truth: `agent-hosts.test.sh` from
  the contract, `adoption-lock.test.sh` from the package manifest.

## [0.1.0] - 2026-08-22

- Initial governance scaffold created.
- No human participant identity or content was generated.

# Ticket Changelog (ticket-060)

## [0.1.0] - 2026-08-12

- Initial governance scaffold created.
- No human participant identity or content was generated.
- Bound the maintenance change to the two hub-owned workflow files and exact
  Node.js 24 action revisions; workflow semantics and adoption package remain
  outside the change.
- Replaced two local and two reusable checkout pins with v7.0.1, setup-python
  with v7.0.0, and both github-script pins with v8.0.0.
- Passed the complete Linux shell contract and an exact seven-reference action
  audit; no legacy Node.js 20 action revision remains in the owned workflows.
- Kept the first required-LLM todo2code attempt fail-closed when the configured
  OpenRouter key still reported its weekly limit; no deterministic fallback was
  accepted as semantic evidence.
- Merged PR #88 after exact-head Validator GLM approval and green hosted
  Linux/Windows checks; the post-merge run remained green.
- Verified the adopted SHA in `twin` through real Linux, Windows and reusable
  governance execution with zero Node.js 20 annotations.
- Marked the ticket `DONE / DONE`; provider unavailability remains explicit
  and is not represented as a successful todo2code semantic analysis.

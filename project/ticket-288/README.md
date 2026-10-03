# Preserve ticket index changes and validate durability across platforms

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Respect the ancestor when merging ticket rows and surrounding target-owned prose. Preserve one-sided deletions and edits; expose conflicting changes through Git merge-file instead of choosing a row by populated cells. Reject ambiguous duplicate or unrecognized table content from custom merging. Complete ticket-287's deferred CI outcome by running ticket-index and continuity storage regressions on Linux and Windows. Keep captured Registry regressions on Linux and exact-byte fixture diagnostics. Windows Registry URL canonicalization and its Windows CI wiring are explicitly deferred to a dependent runtime ticket.

## Acceptance criteria
- AC-01: Real merge-file and pure merge regressions cover deletions, concurrent additions, conflicting edits and retained text. All three durability suites pass locally; Linux runs all three and Windows runs continuity and ticket-index suites. Retain and report the deferred Windows Registry failure.
- AC-02: Native governance, existing merge-driver self-test and required Linux/Windows/OneDev checks pass.
- AC-03: Independent exact-head merge and final immutable v0.20.62 release are verified externally.

## Risks and limits
Conflicts previously hidden by heuristic row selection become explicit conflicts. The workflow change has an explicit public-interface budget of one path. This ticket depends on the merged/released ticket-287; scope is S / 25 minutes, nine implementation files, three components and no runtime dependencies.

## Evidence
Isolated original-code reproductions show deleted rows resurrected, conflicting edits silently selected and one-sided footer text discarded. External test streams, accepted controller receipts and protected publication evidence remain in operational storage.

The diagnostic Windows run binds the failure to Python's literal `~` versus Node's `%7E` in the same temporary-directory URL. Exact machine-local paths remain in private diagnostic evidence. The original runtime scope does not include `scripts/ticket_storage.py`; the core correction belongs to a dependent ticket rather than expanding this PR's budget. The accepted narrowed intent retains this failure and makes no Registry Windows PASS claim.

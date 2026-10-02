# Execute the independently pinned Registry module closure

- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Goal and scope
Bind Registry execution to captured bytes of all three independently pinned ESM modules. Preserve CLI arguments, module identity and stdin, reject files outside the captured dependency closure, and publish standard 0.20.60 after independent exact-head approval.

## Acceptance criteria
- AC-01: Real Node tests reproduce entry-point and dependency replacement after verification, then pass with captured execution and preserved input semantics.
- AC-02: Native governance, existing storage boundary checks and required protected CI pass.
- AC-03: Independent exact-head merge and final immutable v0.20.60 release are verified externally.

## Risks and limits
Requires Node module.register support (Node 20.6 / 18.19 or later), retaining existing Node requirements of the independently pinned writer. The loader binds ESM module bytes; it does not sandbox trusted Node builtins. Scope is S / 25 minutes, seven implementation files, three components, no dependencies.

## Evidence
Raw test streams and accepted controller receipts stay in external operational storage. Passing tests grant no merge authority.

## Local validation
Nine captured-runtime tests pass; three checks fail on the original runtime (entry substitution, dependency substitution, unpinned import). Native governance passes with zero errors and warnings. The independently pinned Registry integration suite reports seven passes and one pre-existing failure: its legacy file-mode allocation expects a linked preparation checkout to accept allocation, but worktrees v5 requires the registered primary checkout on main. The exact same assertion fails against the unchanged 0.20.59 bridge; the policy is preserved and this separate fixture issue is not waived as a pass.

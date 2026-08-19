# AGENTS.md

## Repository Purpose
This repository is the central **Governance and Onboarding Hub** for both Human contributors and Autonomous AI Agents.

> ⚠️ **CRITICAL RULE**: This Governance Hub is the maintained source of
> the standard. It may be changed only inside the `wellmanifest/new-project`
> repository and every multi-step maintenance change must be governed by
> exactly one `project/ticket-{NNN}/` ticket with an approved `intent.json`.
> Tickets, task files and logs belonging to target systems must never be stored
> here.

## HOME vs ADOPT (closed vocabulary)

wellmanifest owns **standards**. Running CLI/daemons belong in the product org
(`subactor` or `semcod`). **"w ramach wellmanifest" / "within wellmanifest
standardization" means ADOPT, not HOME.**

Emit these fields on `intent.json` `placement` for SERVICE/FEATURE that create
or place a repository (optional on the schema so existing tickets still
validate; fill them in `WAIT_FOR_APPROVAL` before execution):

- `home`: `wellmanifest` | `subactor` | `semcod`
- `shape`: `domain_pack` | `runtime_service` | `both`
- `runtimeOwner`: same enum as `home` (who runs the CLI/daemon)
- `adopt`: `wellmanifest/<pack>` ids — follow those packs; **adopt ≠ home**

`shape=runtime_service` must not use `home=wellmanifest`.

## Primary Instructions & Policy Rules
AI Agents interacting with this workspace MUST immediately read and adhere to the authoritative policy files:

1. 🛡️ **[POLICY.md](POLICY.md)** – Mandatory safety rules, forbidden actions, and source precedence (Mode: Strict).
2. 📋 **[CONTRIBUTING.md](CONTRIBUTING.md)** – Procedural workflow, state machine transitions, and ticket lifecycle (Mode: Procedural).

## Quick Execution Rules & Workflow Sequence
- **Precedence**: `USER_REQUEST` > `FILESYSTEM` > `POLICY.md` > `CONTRIBUTING.md`.
- **Governance Hub Maintenance**: changes to the standard use this repository's
  own `project/ticket-{NNN}` lifecycle. Governance evidence and agent logs stay
  in that ticket; implementation, tests and scripts stay in their normal
  repository directories and must match the ticket's `allowedPaths`.
- **Target Repository Isolation**: tickets and task evidence for System X are
  created only in System X's repository, never in `wellmanifest/new-project`.
- **Target Repository Execution**: When assigned a task to create System X, the agent:
  1. Reads policies & copies templates/scripts from `wellmanifest/new-project`.
  2. Switches completely to System X's target repository/folder.
  3. Adopts the package through Goal. Root `project.sh` / `project.bat` are
     target-owned seed aliases: create them only when absent and never replace
     established target automation. The canonical managed gates are
     `project/governance-check.sh` and `project/governance-check.bat`.
  4. In System X's repository, BEFORE writing any code, resolves
     `.governance/manifest.json` repository mode and initializes:
     - Root `README.md`, `VERSION`, `CHANGELOG.md` and `TODO.md`.
     - `Dockerfile` and `compose.yml` only when `docker.required=true`; an
       application kind alone never makes Docker mandatory.
     - A separate repository for `repository.mode=standalone`, or every
       declared `repository.componentRoots` path in the current repository for
       `repository.mode=monorepo`.
     - Scaffolds `project/ticket-{NNN}/` containing `preprompt.md` (technical directives and resource links) and `changelog.md`.
     - Creates machine-readable `intent.json`; its `allowedPaths` bounds implementation after approval.
     - `project/TICKETS.md` is the ticket index; existing `project/README.md` files owned by analysis generators remain untouched.
     - Human participant file `user-{github_username}.md` is created only by that human or a trusted intake boundary. An agent never creates or edits it on the human's behalf.
     - AI Agent Brain `ai-{PROVIDER}.md` (AI's understanding of the task, intent, scope, risks & Acceptance Criteria) uses explicit participant metadata and typed sections.
     - Dedicated log file `ai-{PROVIDER}-logs.txt`.
  5. **RECORD BOUNDED AUTHORIZATION (`P-CORE-008`)**: Presents the initialized plan as an auditable scope before writing code:
     - **Understanding View (`project/ticket-{NNN}/ai-{PROVIDER}.md`)**: User checks if AI correctly understood the task, intent, and acceptance criteria.
     - **Task Checklist View (`TODO.md`)**: User checks if AI's step-by-step task breakdown and checklist are appropriate.
     - A request that already tells the agent to execute or work autonomously creates `SESSION_EXECUTION_AUTHORIZATION`; proceed within the recorded intent without a second confirmation.
  6. **EXECUTE WITHIN AUTHORIZATION**: With session execution authorization,
     executes the managed `./project/governance-check.sh` (or
     `project\governance-check.bat`) in System X's repository. It never assumes
     a target-owned root seed contains the gate. Optional analysis then runs
     only through a digest-pinned Docker image. The agent works EXCLUSIVELY in
     System X's repository.
     - Ask for new authority only for destructive action, secret access, new external coordination, or material objective expansion.
     - Chat/Markdown approval authorizes the interactive session but is not
       trusted merge approval. CI requires an independent allowlisted human
       review, allowlisted Validator GitHub App review, or verified signed
       attestation.
  7. **CONTINUE MATCHING ACTIVE TICKET (`P-CORE-009` / `C-TICKET-008`)**: Re-use the active ticket when workstream and scope match. A separate active ticket is allowed only for a declared different workstream with no write-scope overlap. Each branch/PR must resolve to exactly one ticket. Update only the agent-owned `ai-{PROVIDER}.md` and project TODO; NEVER modify human-owned `user-{github_username}.md` files.
  8. **KEEP IMPLEMENTATION OUTSIDE THE TICKET**: `project/ticket-{NNN}/` contains governance, decisions, logs and captured evidence. Executable source, tests and research scripts belong in their normal repository directories.
  9. **ROUTE UNKNOWN OWNERS EXPLICITLY**: use `unresolved:human` or `unresolved:agent`; never emit an empty required-response route or infer identity from a name.
  10. **RUN THE GATE**: `./project/governance-check.sh` must pass before stack tests and publication. Required governance decisions are deterministic; LLM findings are advisory.
  11. **COORDINATE PARALLEL WORK**: Serialize ticket-ID allocation before branching, then use separate branches/worktrees and explicit `dependsOn`/`conflictsWith`. Shared contracts are edited only by the manifest-declared integration workstream; `integrationTicket` records coordination but does not transfer path ownership. One agent implements; a second agent may review read-only or own a non-overlapping ticket. Product commercial registries (prices, entitlements, public plan ids, checkout-facing legal surfaces) and brand facades (tokens, closed vocabulary, public plan names) MUST be listed in `coordination.integration.requiredForPaths` and changed only by an integration ticket after the adopted product SSOT is updated. For Subactor: list prices and site bindings HOME in `subactor/offer`; brand tokens/vocabulary HOME in `subactor/brand`; `wellmanifest/policy-dsl` owns promo/qualification only (ADOPT plan ids — never a second price or brand SSOT). Portal `plans.json` / CSS-token copies are facades. Standards pointers: `wellmanifest/offer`, `wellmanifest/brand`. A feature ticket MUST NOT rewrite those paths with empty `conflictsWith` while another worktree carries a divergent commercial or brand intent. Advisory tools (todo2code, autogrammar, LLM) may flag Ambiguity; they never authorize merge over a catalog/lock/vocabulary mismatch.
   12. **RELEASE WAITING RESERVATIONS**: Only `IN_PROGRESS` reserves a workstream and write scope. Use `BACKLOG`, `PLAN` or `BLOCKED` while waiting, and return to `IN_PROGRESS` before changing implementation files.
   13. **VERIFY REVIEW AUTHORITY**: A current-head approval is trusted only when a `User` login is in protected `trusted-reviewers`, a `Bot` login is in the separate protected `trusted-validator-apps`, or a protected verifier has validated a signed attestation. Evidence must bind repository, PR, HEAD, ticket and actor and be created outside the PR checkout. Any other review remains advisory.
   13a. **INVOKE VALIDATOR-AGENT (do not ask the human)**: When publication needs trusted merge approval (protected `main`, merge blocked on reviews, or the user asks to publish/merge), the coding agent MUST invoke `subactor/validator-agent` itself. From a checkout of `subactor/validator-agent` on `main`, run `./bin/dispatch-direct-pr.sh --owner <org> --name <repo> --pr <N> --ticket ticket-NNN [--wait-checks] [--merge] [--watch]`. Freeze protocol: re-read `headRefOid` immediately before dispatch; do not push after freeze until approve or fail. MUST NOT ask the human to “use the validator”, self-approve, or treat chat/Markdown as merge approval. The implementing agent MUST NOT review its own PR. Normative detail: `subactor/validator-agent/docs/PUBLICATION_FREEZE.md` and `docs/GOVERNANCE_ENFORCEMENT.md` (Validator integration).
   14. **KEEP LLM ADVISORY**: Validator-agent examples use `LLM_MODEL_VALIDATOR=openrouter/z-ai/glm-5.2`; Gemini 3.1 Pro Preview is not used. No model output is itself a trusted approval.
   15. **CLEAN UP TICKET BRANCHES**: Configure GitHub with `delete_branch_on_merge=true`. A merged head branch is temporary and must disappear after merge. A PR closed without merge keeps its branch until the owner explicitly discards that unmerged work. When no PR is open, the only remote branch is the default branch.
   16. **CLEAN UP LOCAL WORKSPACES**: At merge, publication or explicit pilot discard, inventory every temporary linked worktree, duplicate clone and non-default local branch. Verify dirty state and whether each HEAD is integrated or explicitly disposable before removal. Preserve unknown or unique data. Remove an exact linked worktree through `git worktree remove`, then prune metadata and delete only its released disposable local branch; prefer recoverable trash for a verified duplicate clone. The checker is read-only: during active work exempt a branch only by allowlisting its exact checkout path, never by pattern or branch name. Run the adopted `.governance/workspace_lifecycle_check.py` through Goal for the terminal audit. CI validates GitHub state separately and cannot see a developer filesystem.
   17. **ALLOCATE THROUGH THE MANAGED SCRIPT**: Allocate every ticket ID only through `project/new-ticket.sh` after fetching/pruning. Never create or copy `project/ticket-{NNN}` manually. The clone-wide lock and high-water reservation are required even before the ticket is committed.
   18. **KEEP PUBLICATION ACTIVE**: An implementation PR remains `IN_PROGRESS / PUBLICATION` through exact-head review and trusted merge. Set `DONE / DONE` only in a governance-only closure created from the integrated default branch; never close the unmerged full-diff branch.
   19. **FOLLOW CANONICAL REMEDIATION**: Resolve `GOV-*` findings through `governance/diagnostics.json` and the linked `error/*.md` runbook when present. A ticket log is historical evidence, not a reusable solution, and a runbook never authorizes bypassing a fail-closed gate.
   20. **VALIDATE TARGET REMEDIATION INTENT**: Keep an incident-specific `remediation-intent.dsl.json` in the target repository ticket, validate it deterministically before LLM planning, and treat todo2code/LLM analysis as digest-bound advisory input. Never store target reports or remediation intents in this Governance Hub.
   21. **KEEP ONE C/Q AUTHORITY**: When `.governance/manifest.json` selects
       `domainContracts.mode=cqrs`, keep command and query definitions only in
       `operations/index.json`. Publish the mandatory `events/index.json` and
       `error/index.json` catalogs plus stable `events/{event-id}.md` and
       `error/{code}.md` documents. Protobuf and JSON Schema models describe
       transport shape only; they never grant authority or redefine operation
       semantics. Run the managed gate after every graph change.
   22. **HOST-AGNOSTIC STANDARD**: Every LLM host loads the same fail-closed
       contract. Adopters and this hub ship `GEMINI.md` (Gemini/Antigravity),
       `CLAUDE.md` (Claude Code), `.cursor/rules/new-project-standard.mdc`
       (Cursor), and `.githooks/pre-commit`. An agent MUST run
       `./scripts/install-agent-hosts.sh` once per clone (and `--user` on a
       developer machine) before the first commit. The hook rejects commits
       whose branch is not bound to an `IN_PROGRESS` `ticket-NNN`. Markdown
       is not a substitute for the hook. Do not write on `main` or a dirty
       primary checkout.

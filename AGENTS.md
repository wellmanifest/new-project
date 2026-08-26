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
  11. **COORDINATE THROUGH OWNING PACKS**: ADOPT `wellmanifest/worktrees` for checkout placement and leases, `wellmanifest/git-lifecycle` for branch/ref/PR transitions, `wellmanifest/merge` for divergent-work disposition and `wellmanifest/validation-attestation` for trusted exact-head evidence. `wellmanifest/git` is only an alias of `wellmanifest/git-lifecycle`. Keep one ticket, branch, leased delivery worktree and pull request per delivery unit. Shared contracts remain owned by the integration workstream and their HOME domain packs.
   12. **RELEASE WAITING RESERVATIONS**: Only `IN_PROGRESS` reserves a workstream and write scope. Use `BACKLOG`, `PLAN` or `BLOCKED` while waiting, and return to `IN_PROGRESS` before changing implementation files.
   13. **FREEZE AND VALIDATE THROUGH THE TARGET BINDING**: Follow `wellmanifest/validation-attestation` and `wellmanifest/merge`. Freeze the current HEAD before independent validation and let the adopting runtime invoke its configured validator. Chat, repository-authored evidence, model output and arbitrary Bot reviews are advisory, never trusted approval.
   14. **KEEP PROVIDER POLICY OUT OF BOOTSTRAP**: Follow `wellmanifest/llm`; provider and model selection belong to the adopting runtime.
   15. **HAND OFF TERMINAL CLEANUP**: Follow `wellmanifest/git-lifecycle` for remote branches and PR state, and `wellmanifest/worktrees` for local checkout audit. Preserve dirty, unique, active or unknown work. Cleanup and merge require exact receipts.
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

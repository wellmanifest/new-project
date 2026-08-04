# AGENTS.md

## Repository Purpose
This repository is the central **Governance and Onboarding Hub** for both Human contributors and Autonomous AI Agents.

> ⚠️ **CRITICAL RULE**: This Governance Hub is the maintained source of
> the standard. It may be changed only inside the `wellmanifest/new-project`
> repository and every multi-step maintenance change must be governed by
> exactly one `project/ticket-{NNN}/` ticket with an approved `intent.json`.
> Tickets, task files and logs belonging to target systems must never be stored
> here.

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
  3. Copies `project.sh` & `project.bat` to System X's repository.
  4. In System X's repository, BEFORE writing any code, initializes:
     - Root `README.md`, `VERSION`, `CHANGELOG.md`, `TODO.md`, `Dockerfile`, `compose.yml`.
     - Scaffolds `project/ticket-{NNN}/` containing `preprompt.md` (technical directives and resource links) and `changelog.md`.
     - Creates machine-readable `intent.json`; its `allowedPaths` bounds implementation after approval.
     - `project/TICKETS.md` is the ticket index; existing `project/README.md` files owned by analysis generators remain untouched.
     - Human participant file `user-{github_username}.md` is created only by that human or a trusted intake boundary. An agent never creates or edits it on the human's behalf.
     - AI Agent Brain `ai-{PROVIDER}.md` (AI's understanding of the task, intent, scope, risks & Acceptance Criteria) uses explicit participant metadata and typed sections.
     - Dedicated log file `ai-{PROVIDER}-logs.txt`.
  5. **STOP & WAIT FOR USER REVIEW (`P-CORE-008`)**: Presents the initialized plan to the user for review & approval before writing any code:
     - **Understanding View (`project/ticket-{NNN}/ai-{PROVIDER}.md`)**: User checks if AI correctly understood the task, intent, and acceptance criteria.
     - **Task Checklist View (`TODO.md`)**: User checks if AI's step-by-step task breakdown and checklist are appropriate.
  6. **EXECUTE AFTER APPROVAL**: Upon user approval, executes `./project.sh` (or `project.bat`) in System X's repository to run the deterministic governance gate. Optional analysis then runs only through a digest-pinned Docker image. The agent works EXCLUSIVELY in System X's repository.
     - Chat/Markdown approval authorizes the interactive session but is not trusted merge evidence. CI requires an independent GitHub review or signed attestation.
  7. **CONTINUE MATCHING ACTIVE TICKET (`P-CORE-009` / `C-TICKET-008`)**: Re-use the active ticket when workstream and scope match. A separate active ticket is allowed only for a declared different workstream with no write-scope overlap. Each branch/PR must resolve to exactly one ticket. Update only the agent-owned `ai-{PROVIDER}.md` and project TODO; NEVER modify human-owned `user-{github_username}.md` files.
  8. **KEEP IMPLEMENTATION OUTSIDE THE TICKET**: `project/ticket-{NNN}/` contains governance, decisions, logs and captured evidence. Executable source, tests and research scripts belong in their normal repository directories.
  9. **ROUTE UNKNOWN OWNERS EXPLICITLY**: use `unresolved:human` or `unresolved:agent`; never emit an empty required-response route or infer identity from a name.
  10. **RUN THE GATE**: `./project/governance-check.sh` must pass before stack tests and publication. Required governance decisions are deterministic; LLM findings are advisory.
  11. **COORDINATE PARALLEL WORK**: Serialize ticket-ID allocation before branching, then use separate branches/worktrees and explicit `dependsOn`/`conflictsWith`. Shared contracts are edited only by the manifest-declared integration workstream; `integrationTicket` records coordination but does not transfer path ownership. One agent implements; a second agent may review read-only or own a non-overlapping ticket.
   12. **RELEASE WAITING RESERVATIONS**: Only `IN_PROGRESS` reserves a workstream and write scope. Use `BACKLOG`, `PLAN` or `BLOCKED` while waiting, and return to `IN_PROGRESS` before changing implementation files.
   13. **VERIFY REVIEW AUTHORITY**: A current-head approval is trusted only when the reviewer login is in the target repository's explicit `trusted-reviewers` set protected by CODEOWNERS. Any other review remains advisory.

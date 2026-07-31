# AGENTS.md

## Repository Purpose
This repository is the central **Governance and Onboarding Hub** for both Human contributors and Autonomous AI Agents.

> ⚠️ **CRITICAL RULE**: This Governance Hub is a READ-ONLY policy repository. **DO NOT CREATE ANY TICKETS, TASK FILES, TODOs, OR LOGS IN THIS REPOSITORY.**

## Primary Instructions & Policy Rules
AI Agents interacting with this workspace MUST immediately read and adhere to the authoritative policy files:

1. 🛡️ **[POLICY.md](POLICY.md)** – Mandatory safety rules, forbidden actions, and source precedence (Mode: Strict).
2. 📋 **[CONTRIBUTING.md](CONTRIBUTING.md)** – Procedural workflow, state machine transitions, and ticket lifecycle (Mode: Procedural).

## Quick Execution Rules & Workflow Sequence
- **Precedence**: `USER_REQUEST` > `FILESYSTEM` > `POLICY.md` > `CONTRIBUTING.md`.
- **Governance Hub Scope**: NO tickets (`project/ticket-{NNN}`), task logs, or project files are created in `wellmanifest/new-project`.
- **Target Repository Execution**: When assigned a task to create System X, the agent:
  1. Reads policies & copies templates/scripts from `wellmanifest/new-project`.
  2. Switches completely to System X's target repository/folder.
  3. Copies `project.sh` & `project.bat` to System X's repository.
  4. In System X's repository, BEFORE writing any code, initializes:
     - Root `README.md`, `VERSION`, `CHANGELOG.md`, `TODO.md`, `Dockerfile`, `compose.yml`.
     - Scaffolds `project/ticket-{NNN}/` containing `preprompt.md` (technical directives and resource links) and `changelog.md`.
     - `project/TICKETS.md` is the ticket index; existing `project/README.md` files owned by analysis generators remain untouched.
     - Human participant file `user-{github_username}.md` is created only by that human or a trusted intake boundary. An agent never creates or edits it on the human's behalf.
     - AI Agent Brain `ai-{PROVIDER}.md` (AI's understanding of the task, intent, scope, risks & Acceptance Criteria) uses explicit participant metadata and typed sections.
     - Dedicated log file `ai-{PROVIDER}-logs.txt`.
  5. **STOP & WAIT FOR USER REVIEW (`P-CORE-008`)**: Presents the initialized plan to the user for review & approval before writing any code:
     - **Understanding View (`project/ticket-{NNN}/ai-{PROVIDER}.md`)**: User checks if AI correctly understood the task, intent, and acceptance criteria.
     - **Task Checklist View (`TODO.md`)**: User checks if AI's step-by-step task breakdown and checklist are appropriate.
  6. **EXECUTE AFTER APPROVAL**: Upon user approval, executes `./project.sh` (or `project.bat`) in System X's repository to run Dev Tools and works EXCLUSIVELY in System X's repository.
  7. **CONTINUE ACTIVE TICKET (`P-CORE-009` / `C-TICKET-008`)**: For follow-up prompts or task continuation, DO NOT create new ticket folders. Re-use the active `project/ticket-{NNN}/` directory and update `ai-{PROVIDER}.md` and `TODO.md`. NEVER modify human-owned `user-{github_username}.md` files.
  8. **KEEP IMPLEMENTATION OUTSIDE THE TICKET**: `project/ticket-{NNN}/` contains governance, decisions, logs and captured evidence. Executable source, tests and research scripts belong in their normal repository directories.
  9. **ROUTE UNKNOWN OWNERS EXPLICITLY**: use `unresolved:human` or `unresolved:agent`; never emit an empty required-response route or infer identity from a name.

# AGENTS.md

## Repository Purpose
This repository is the central **Governance and Onboarding Hub** for both Human contributors and Autonomous AI Agents.

> ⚠️ **CRITICAL RULE**: This Governance Hub is a READ-ONLY policy repository. **DO NOT CREATE ANY TICKETS, TASK FILES, TODOs, OR LOGS IN THIS REPOSITORY.**

## Primary Instructions & Policy Rules
AI Agents interacting with this workspace MUST immediately read and adhere to the authoritative policy files:

1. 🛡️ **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** – Mandatory safety rules, forbidden actions, and source precedence (Mode: Strict).
2. 📋 **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** – Procedural workflow, state machine transitions, and ticket lifecycle (Mode: Procedural).

## Quick Execution Rules & Workflow Sequence
- **Precedence**: `USER_REQUEST` > `FILESYSTEM` > `POLICY.md` > `CONTRIBUTING.md`.
- **Governance Hub Scope**: NO tickets (`project/ticket-{NNN}`), task logs, or project files are created in `wellmanifest/new-project`.
- **Target Repository Execution**: When assigned a task to create System X, the agent:
  1. Reads policies & copies templates/scripts from `wellmanifest/new-project`.
  2. Switches completely to System X's target repository/folder.
  3. Copies `project.sh` & `project.bat` to System X's repository.
  4. In System X's repository, BEFORE writing any code, initializes:
     - `README.md` (System X architecture & scope plan)
     - `VERSION` & `CHANGELOG.md`
     - `TODO.md` (Task list for System X)
     - `project/ticket-{NNN}/` (Ticket files: `README.md`, `AI-{NAME}.md`, `logs.txt`)
     - `Dockerfile` & `compose.yml`
  5. Executes `./project.sh` (or `project.bat`) in System X's repository to run automated Dev Tools (`code2llm`, `redup`, `prefact`, `doql`, `sumd`, `goal`) and works EXCLUSIVELY in System X's repository.

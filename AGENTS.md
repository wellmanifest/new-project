# AGENTS.md

## Repository Purpose
This repository is the central **Governance and Onboarding Hub** for both Human contributors and Autonomous AI Agents.

## Primary Instructions & Policy Rules
AI Agents interacting with this workspace MUST immediately read and adhere to the authoritative policy files:

1. 🛡️ **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** – Mandatory safety rules, forbidden actions, and source precedence (Mode: Strict).
2. 📋 **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** – Procedural workflow, state machine transitions, and ticket lifecycle (Mode: Procedural).

## Quick Execution Rules
- **Precedence**: `USER_REQUEST` > `FILESYSTEM` > `POLICY.md` > `CONTRIBUTING.md`.
- **Dev Tools First (Token & Time Efficiency)**: Agents MUST run `./project.sh` (or `project.bat`) to execute automated tools (`code2llm`, `redup`, `prefact`, `doql`, `sumd`, `goal`) instead of manual file scanning. Work on tool-generated outputs in `./project/` to save tokens.
- **New System Architecture**: EVERY new system MUST be created in a NEW separate repository on GitHub to keep this Governance Hub clean.
- **New Repo Bootstrap**: In the new system's repository, the agent MUST immediately initialize `README.md`, `VERSION`, `CHANGELOG.md`, `TODO.md`, `Dockerfile`, `compose.yml`, and `project.sh`/`project.bat` so the user can easily verify and review the planned scope before coding.
- **Environment & Tools**: EVERY system MUST use Docker (`Dockerfile`, `compose.yml`) and all available development tools.
- **Ticketing**: Multi-step tasks (>1 step) MUST be tracked under `project/ticket-{NNN}`.
- **Ticket Retention**: Do NOT delete ticket directories unless explicitly ordered by the user after project completion.

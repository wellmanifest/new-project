# CHANGELOG

## [0.3.0] - 2026-07-30

### Added & Updated (Etap 2 Completed)
- **Universal Ticket Automation Scripts**: Added `project/new-ticket.sh` (POSIX script for scaffolding tickets with `preprompt.md` and `changelog.md`) and `project/readme.sh` (POSIX script for generating `project/README.md` master menu index).
- **Template Standards**: Created `template/files/project.template.md` adhering to `*.template.md` naming standards. Updated Polish documentation in `template/files/README.md` and `template/projects/README.md`.
- **DSL Procedural Rule `C-TOOLS-006`**: Added rule in `CONTRIBUTING.md` requiring AI agents to copy existing shell scripts from Governance Hub during target repository bootstrap instead of regenerating them.
- **Roadmap Checklist**: Marked Etap 2 as completed in `TODO.md` and bumped `VERSION` to `0.3.0`.

## [0.2.0] - 2026-07-29

### Added & Updated (Etap 1 Completed)
- **ASCII Sequence Diagram in `README.md`**: Added explicit creation sequence and dependency graph (`USER_REQUEST` → `user-{github_username}.md` → `project/ticket-{NNN}/README.md` → `TODO.md` → `ai-{PROVIDER}.md` + `ai-{PROVIDER}-logs.txt` → `VERSION` + `CHANGELOG.md`).
- **Detailed File Roles Breakdown**: Documented specific roles for `user-{github_username}.md`, `ai-{PROVIDER}.md`, `ai-{PROVIDER}-logs.txt`, `changelog.md`, and `preprompt.md`.
- **Master Navigation Menu**: Standardized `README.md` as the master navigation index.

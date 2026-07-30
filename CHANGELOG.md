# CHANGELOG

## [0.4.0] - 2026-07-30

### Added & Updated (Etap 3 Completed)
- **Technical Directive Template `preprompt.template.md`**: Created `template/files/preprompt.template.md` establishing standardized ticket preprompt layouts for technical constraints, linked resources, and execution directives.
- **Scaffolder Integration**: Updated `project/new-ticket.sh` to use `template/files/preprompt.template.md` when generating `project/ticket-{NNN}/preprompt.md`.
- **Template Indexing**: Updated `template/files/README.md` to index `preprompt.template.md`.
- **Roadmap Checklist**: Marked Etap 3 as completed in `TODO.md` and bumped `VERSION` to `0.4.0`.

## [0.3.0] - 2026-07-30

### Added & Updated (Etap 2 Completed)
- **Universal Ticket Automation Scripts**: Added `project/new-ticket.sh` (POSIX script for scaffolding tickets with `preprompt.md` and `changelog.md`) and `project/readme.sh` (POSIX script for generating `project/README.md` master menu index).
- **Template Standards**: Created `template/files/project.template.md` adhering to `*.template.md` naming standards. Updated Polish documentation in `template/files/README.md` and `template/projects/README.md`.
- **DSL Procedural Rule `C-TOOLS-006`**: Added rule in `CONTRIBUTING.md` requiring AI agents to copy existing shell scripts from Governance Hub during target repository bootstrap instead of regenerating them.
- **Active Ticket Reuse Rule `P-CORE-009` / `C-TICKET-008`**: Added rules prohibiting spawning multiple tickets for follow-up prompts and forbidding AI edits to human participant files.

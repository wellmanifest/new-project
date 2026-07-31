# CHANGELOG

## [0.6.0] - 2026-07-31

### Hardened ticket ownership and namespace

- Moved the generated ticket index to `project/TICKETS.md`, preserving any
  analysis-owned `project/README.md`.
- Made `new-ticket.sh` fail closed when an unfinished ticket exists and added
  validated agent IDs, complete ticket/agent scaffolding and safe template
  rendering.
- Stopped automatic human-file generation. Human intent must come from its
  owner or a trusted intake boundary; unresolved routes use explicit role
  sentinels.
- Added role-specific participant templates with typed metadata and prohibited
  executable implementation under ticket directories.
- Removed machine-local documentation links and added an isolated regression
  test for scaffolding, indexing, traversal protection and active-ticket reuse.

## [0.5.0] - 2026-07-30

### Added & Updated (Etap 4 Completed)
- **Mandatory Target Architecture Diagrams (`P-DOCS-001` & `C-DOCS-001`)**: Added rules requiring AI agents to generate visual Mermaid architecture & logic flow diagrams under `docs/` in all target repositories (e.g. `docs/ARCHITECTURE.md`, `docs/LOGIC_FLOW.md`).
- **TODO Roadmap Overhaul**: Refactored `TODO.md` with clean, precise descriptions for all 4 completed stages.
- **Version Bump**: Bumped `VERSION` to `0.5.0`.

## [0.4.0] - 2026-07-30

### Added & Updated (Etap 3 Completed)
- **Technical Directive Template `preprompt.template.md`**: Created `template/files/preprompt.template.md` establishing standardized ticket preprompt layouts for technical constraints, linked resources, and execution directives.
- **Scaffolder Integration**: Updated `project/new-ticket.sh` to use `template/files/preprompt.template.md` when generating `project/ticket-{NNN}/preprompt.md`.
- **Template Indexing**: Updated `template/files/README.md` to index `preprompt.template.md`.

## [0.3.0] - 2026-07-30

### Added & Updated (Etap 2 Completed)
- **Universal Ticket Automation Scripts**: Added `project/new-ticket.sh` (POSIX script for scaffolding tickets with `preprompt.md` and `changelog.md`) and `project/readme.sh` (POSIX script for generating `project/README.md` master menu index).
- **Template Standards**: Created `template/files/project.template.md` adhering to `*.template.md` naming standards. Updated Polish documentation in `template/files/README.md` and `template/projects/README.md`.
- **DSL Procedural Rule `C-TOOLS-006`**: Added rule in `CONTRIBUTING.md` requiring AI agents to copy existing shell scripts from Governance Hub during target repository bootstrap instead of regenerating them.
- **Active Ticket Reuse Rule `P-CORE-009` / `C-TICKET-008`**: Added rules prohibiting spawning multiple tickets for follow-up prompts and forbidding AI edits to human participant files.

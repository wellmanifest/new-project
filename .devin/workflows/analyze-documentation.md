---
description: Analyze and improve project documentation for AI agent clarity
---

# Workflow: Analyze Documentation for AI Agents

## Purpose
This workflow describes how to analyze project documentation to ensure it is clear and actionable for AI agents like Devin.

## When to Use
Use this workflow when:
- Starting work on a new project
- Verifying that documentation reflects actual implementation
- Checking if contributing guidelines are understandable for AI agents
- Identifying gaps between documented workflow and actual tools/scripts

## Steps

1. **Read the root entrypoint and operational instructions**
   - Read `CONTRIBUTING.md` as the entrypoint
   - Read `GPT56Luna/CONTRIBUTING.md` as the repository-specific operational guide
   - Confirm that the entrypoint points to the operational guide

2. **Read the documentation index**
   - Read `docs/README.md`
   - Verify that it lists the sources of truth and their roles
   - Verify that it points to the operational guide and analysis report

3. **Read the general standards and policy**
   - Read `README.md` for the general agent-work standard
   - Read `POLICY.md` for project policies

4. **Analyze project.sh (or equivalent setup script)**
   - Identify installed tools and active commands
   - Distinguish active commands from commented commands
   - Note inputs, outputs, side effects, overwrite flags and limitations
   - Check that the operational guide reflects the actual script

5. **Compare documentation with actual implementation**
   - Check whether `GPT56Luna/CONTRIBUTING.md` reflects the current workflow
   - Check whether `docs/README.md` links are valid
   - Identify unsupported claims about tools, agents, tests, CI, Docker or applications
   - Use Git history to explain moves or removals, but treat current files as authoritative

6. **Update the documentation when needed**
   - Put repository-specific operating rules in `GPT56Luna/CONTRIBUTING.md`
   - Put findings, gaps, decisions and history in `GPT56Luna/ANALIZA-DOKUMENTACJI.md`
   - Keep `docs/README.md` as the documentation index
   - Keep root `CONTRIBUTING.md` as a concise entrypoint
   - Document each confirmed tool with purpose, invocation, result and limitations

7. **Record the work**
   - Record the analysis method, decisions and checks in `GPT56Luna/NOTATKI-PRACY.md`
   - Do not claim that a command ran if it was only inspected
   - Do not run installation or overwrite operations without checking their effects

## Principles Applied

- **Single source of truth**: Repository-specific operating rules live in `GPT56Luna/CONTRIBUTING.md`; root files point to it
- **Documentation index**: `docs/README.md` lists the roles and sources of truth
- **Tool-specific documentation**: Every tool used in automation scripts is documented according to its confirmed use
- **AI agent clarity**: Documentation is actionable and does not claim unsupported capabilities
- **Current-state priority**: Active files and commands take precedence over historical or aspirational descriptions
- **Minimal changes**: Make focused edits rather than large rewrites

## Expected Outcome

After completing this workflow:
- Root `CONTRIBUTING.md` clearly references the operational guide
- `GPT56Luna/CONTRIBUTING.md` reflects the current repository workflow
- `docs/README.md` provides a valid documentation index
- `GPT56Luna/ANALIZA-DOKUMENTACJI.md` records gaps, decisions and history
- AI agents can understand the project workflow without relying on prior conversation

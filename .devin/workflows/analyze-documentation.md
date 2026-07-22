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

1. **Read root CONTRIBUTING.md**
   - Check if it contains actual guidelines or legacy pseudo-code
   - Verify if it references the comprehensive documentation in docs/

2. **Read docs/README.md**
   - Check if it contains comprehensive contributing guidelines
   - Verify sections 5 (tools) and 6 (agents) are filled with actual content
   - Ensure it follows the structure defined in the template

3. **Analyze project.sh (or equivalent setup script)**
   - Identify all tools used in the script
   - Note the specific commands and their purposes
   - Check if these tools are documented in docs/README.md section 5

4. **Compare documentation with actual implementation**
   - Check if docs/README.md reflects the actual workflow in project.sh
   - Identify missing tool descriptions
   - Identify gaps in the documented process

5. **Update root CONTRIBUTING.md if needed**
   - If it contains outdated pseudo-code, replace with clear reference to docs/README.md
   - Add quick start instructions
   - Include project initialization steps

6. **Add missing tool documentation to docs/README.md**
   - For each tool in project.sh, add a description following the format:
     - Przeznaczenie (Purpose)
     - Użyj do (Use for)
     - Sposób uruchomienia (How to run)
     - Wynik działania (Result)
     - Ograniczenia (Limitations)

7. **Create this workflow documentation**
   - Document the analysis process for future reference
   - Save in .devin/workflows/ for Devin to use in future sessions

## Principles Applied

- **Single source of truth**: Comprehensive documentation should be in docs/, root files should reference it
- **Tool-specific documentation**: Every tool used in automation scripts should be documented
- **AI agent clarity**: Documentation should be actionable and clear for AI agents
- **Consistency**: Follow the established format in docs/README.md for tool descriptions
- **Minimal changes**: Make focused edits rather than large rewrites

## Expected Outcome

After completing this workflow:
- Root CONTRIBUTING.md clearly references comprehensive documentation
- docs/README.md contains complete tool documentation
- AI agents can understand the project workflow from documentation
- Future analysis sessions can follow this documented process

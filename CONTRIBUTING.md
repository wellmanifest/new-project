# AI Agent Rules for Development

## Core Principles

1. **Check existing solutions first** - Before creating new functionality, check if it already exists in:
   - Available tools (code2llm, redup, prefact, vallm, doql, sumd, sumr, goal)
   - Available agents (test-agent, repair-agent, validator-agent, todo-agent, doctor-agent)
   - Existing scripts and workflows
   - Organization components

2. **Delegate to specialists** - Use appropriate tools and agents instead of doing everything manually:
   - Testing → test-agent
   - Code repair → repair-agent or prefact
   - Validation → validator-agent or vallm
   - Task management → todo-agent
   - Diagnostics → doctor-agent

3. **Follow documentation** - Always read and follow:
   - README.md for project overview
   - POLICY.md for naming conventions, modularity, dependencies
   - TODO.md for current tasks

## Workflow Rules

### Before Starting Work
1. Read README.md
2. Read POLICY.md
3. Check existing TODO.md
4. Identify available tools and agents
5. Plan approach using TODO.md

### During Work
1. Update TODO.md with progress
2. Use appropriate tools for each task
3. Delegate to specialized agents when available
4. Test using test-agent
5. Validate using validator-agent or vallm

### After Work
1. Update TODO.md with completion status
2. Update documentation if needed
3. Create logical commits
4. Update CHANGELOG.md if applicable

## Tool Usage Rules

### Code Analysis
- Use **code2llm** for project architecture analysis
- Use **redup** for duplicate detection
- Use **prefact** for code quality issues
- Use **vallm** for code validation

### Documentation
- Use **sumd** for markdown summarization
- Use **sumr** for report summarization
- Use **doql** for declarative project generation

### Workflow
- Use **goal** for task automation
- Use **project.sh** for project initialization

## Agent Coordination Rules

### Test Agent
- Use for: running tests, coverage reports
- Input: code, test configuration
- Output: test results, coverage data

### Repair Agent
- Use for: fixing detected issues
- Input: error reports, code
- Output: fixed code, change summary

### Validator Agent
- Use for: policy compliance, quality checks
- Input: code, validation rules
- Output: validation report, issues list

### Todo Agent
- Use for: task management, planning
- Input: project context, issues
- Output: updated TODO.md, task priorities

### Doctor Agent
- Use for: diagnostics, environment checks
- Input: project configuration, logs
- Output: diagnostic report, fix suggestions

## Policy Compliance

### Naming Conventions
- Repositories: lowercase, hyphen-separated
- Packages: match repository names
- Files/directories: lowercase, hyphen-separated

### Modularity
- Single responsibility per module
- Loose coupling, high cohesion
- Clear interfaces and encapsulation

### Dependencies
- Minimal dependencies principle
- Pinned versions for reproducibility
- Regular security audits

## Quality Standards

1. **Code Quality**: Use prefact and vallm before committing
2. **Testing**: Use test-agent for all changes
3. **Documentation**: Update README.md and TODO.md
4. **Validation**: Use validator-agent for policy compliance
5. **Security**: Follow POLICY.md security guidelines

## Communication

1. **Clear commit messages**: Use conventional commit format
2. **Update TODO.md**: Track progress and blockers
3. **Document decisions**: Explain why, not just what
4. **Report issues**: Use todo-agent for task tracking

## Prohibited Actions

- Do NOT duplicate existing functionality
- Do NOT skip testing
- Do NOT ignore security issues
- Do NOT commit secrets
- Do NOT bypass validation
- Do NOT ignore POLICY.md guidelines
- Do NOT create unnecessary dependencies
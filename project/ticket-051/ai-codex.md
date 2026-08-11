---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-051
---
# Participant: codex (AI agent)

## Understanding

The default standard conflates governance adoption with a mandatory Docker
runtime. On `glon`, that forced a second workstream/ticket and container-specific
write semantics before the governance gate could run. The default should be
portable; Docker enforcement remains available as a target opt-in. The same
pilot exposed managed root launchers with no matching owned path.

## Execution plan

1. Remove Dockerfile from default required files, set Docker enforcement false
   and clear the default stack list.
2. Add managed root launchers, runtime script and Goal config to governance
   ownership.
3. Strengthen manifest regressions and document target-level Docker opt-in.
4. Run the focused validator and full Linux contract.
5. Stop before versioning or external delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the overhead on `glon`: mandatory Docker required a second active
  workstream and introduced container-only writable-path behavior unrelated to
  governance correctness.
- Confirmed `project.sh`, `project.bat`, `scripts/runtime.sh` and `goal.yaml`
  are absent from every current workstream ownership pattern.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.

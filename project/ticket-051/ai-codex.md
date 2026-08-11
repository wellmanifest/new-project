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
2. Make only `docker.required` target-owned in the adoption projection so a
   target can opt in while the remaining Docker contract stays managed.
3. Add managed root launchers, runtime script and Goal config to governance
   ownership.
4. Strengthen manifest/adoption regressions and document target-level opt-in.
5. Run focused suites and the full Linux contract; stop before delivery.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Reproduced the overhead on `glon`: mandatory Docker required a second active
  workstream and introduced container-only writable-path behavior unrelated to
  governance correctness.
- Confirmed `project.sh`, `project.bat`, `scripts/runtime.sh` and `goal.yaml`
  are absent from every current workstream ownership pattern.
- Confirmed an unmanaged `false` scalar would block target opt-in; amended the
  plan to remove only `docker.required` from the managed manifest projection
  and test preservation through upgrade.
- Made the default manifest stack-neutral and added complete governance
  ownership for Goal configuration and every managed root launcher.
- Made only `docker.required` target-owned in the projected managed base;
  required paths and stack lists remain additive extensions, while all Docker
  file-name settings stay managed.
- Added regressions proving a target can opt in and retain that choice through
  adoption check/upgrade.
- Passed focused validator/adoption suites and the complete Linux CI contract.

## Blockers

- None; the bounded local objective is complete.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.

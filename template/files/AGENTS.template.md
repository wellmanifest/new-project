# AGENTS.md

This target repository follows `wellmanifest/new-project` policy-as-code.

HOME vs ADOPT: wellmanifest owns standards; product CLI/daemons HOME in
`subactor` or `semcod`. "w ramach wellmanifest" means ADOPT packs such as
`wellmanifest/{new-project,dsl,logs}`, not HOME wellmanifest. For
SERVICE/FEATURE that create a repo, fill `intent.json` `placement`
(`home`, `shape`, `runtimeOwner`, `adopt`) in WAIT_FOR_APPROVAL.
`shape=runtime_service` must not use `home=wellmanifest`.

Before any multi-step implementation, an agent must:

1. Read `.governance/manifest.json`, `TODO.md`, `project/TICKETS.md` and the
   active ticket.
   Respect `repository.mode`: `standalone` owns a separate repository, while
   `monorepo` confines work to declared `repository.componentRoots`. Require a
   running Docker engine and Docker runtime files only when
   `docker.required=true`; existing Docker configuration remains subject to
   stack validation even when Docker is optional.
2. Reuse an unfinished ticket whose workstream and scope match. A second active
   ticket is allowed only in a distinct workstream with no write-scope overlap.
   Otherwise run `./project/new-ticket.sh --title "..." --agent "..."
   --workstream "..."`.
3. Complete the ticket `README.md`, owned `ai-*.md`, `intent.json` and `TODO.md`.
4. Treat a user request that already says to execute or work autonomously as
   `SESSION_EXECUTION_AUTHORIZATION`; record it in the agent-owned ticket file.
   When that same request explicitly creates a new repository, `HEAD` is
   unborn and no implementation exists, it also authorizes exactly one local
   governance seed-baseline commit. Resolve an immutable seed profile, stage
   only its exact allowlist, scan for secrets, create no remote effect, then
   record the real resulting `HEAD` as `delivery.acceptedBaseSha`. This narrow
   exception never authorizes remote creation, push, pull request, merge, tag
   or release; ordinary implementation starts only after the baseline.
5. Move to `EDIT` without a second confirmation and stay inside `intent.json`
   `allowedPaths`. Ask for new authority only for destructive action, secret
   access, new external coordination, or material objective expansion.
   When the recorded outcome includes publication, this authorization also
   permits invoking the repository's declared protected delivery process and
   that process's merge after exact-head trusted approval. Do not ask for a
   second chat confirmation. Session prose is never approval evidence and the
   agent must not merge directly.
6. Never create or edit `project/ticket-*/user-*.md`; only its human owner or a
   trusted intake boundary may do so.
7. Keep executable source/tests/scripts outside ticket directories.
8. Run the managed `./project/governance-check.sh` (or
   `project\governance-check.bat` on Windows) plus the stack checks before
   reporting completion. Root `project.sh` / `project.bat` are optional
   target-owned seed aliases and must not be assumed to contain the gate.
9. ADOPT `wellmanifest/worktrees` for canonical checkout placement and lease
   identity, and `wellmanifest/git-lifecycle` for branch/ref/PR transitions.
   `wellmanifest/git` is only an alias of `wellmanifest/git-lifecycle`. Keep one
   ticket, branch, leased delivery worktree and pull request per delivery unit.
   Shared contracts remain owned by the declared integration workstream and
   their HOME domain packs; `integrationTicket` does not transfer ownership.
10. Only `IN_PROGRESS` reserves a workstream and write scope. `BACKLOG`, `PLAN`
   and `BLOCKED` retain evidence without blocking another implementation;
   transition back to `IN_PROGRESS` before changing source or tests.
11. ADOPT `wellmanifest/validation-attestation` for trusted exact-head evidence
   and `wellmanifest/merge` for disposition and merge decisions. Freeze the
   current HEAD before independent validation; a target runtime binding invokes
   its validator. Chat, repository-authored evidence and arbitrary Bot reviews
   are never trusted approval.
12. Keep LLM findings advisory under `wellmanifest/llm`; provider/model routing
   belongs to the adopting runtime, not this bootstrap standard.
13. Apply terminal remote-branch rules from `wellmanifest/git-lifecycle` and
   terminal local-checkout rules from `wellmanifest/worktrees`. Preserve dirty,
   unique, active or unknown work. Cleanup requires exact observations and a
   runtime receipt; neither pack silently deletes or merges.
14. Allocate every ticket ID only through `./project/new-ticket.sh` after
   fetching/pruning. Never create or copy `project/ticket-{NNN}` manually; the
   clone-wide lock and high-water reservation must exist before commit.
15. Keep an implementation ticket `IN_PROGRESS / PUBLICATION` through
   exact-head review and trusted merge. Set `DONE / DONE` only in a
   governance-only closure based on the integrated default branch.
16. Resolve `GOV-*` findings through `.governance/diagnostics.json` and its
   linked `.governance/error/*.md` runbook when present. Ticket logs are
   historical evidence and never authorize bypassing a fail-closed gate.
17. Keep each incident-specific `remediation-intent.dsl.json` in its target
   ticket. Validate it, atomically render its declared task/TODO paths and run
   `verify-todo2code` before extraction. Analyze todo2code with the exact graph,
   diagnostics and plans so only records citing those projections can affect
   the digest-bound advisory overlay; never let todo2code or an LLM expand the
   accepted intent.
18. When `.governance/manifest.json` selects `domainContracts.mode=cqrs`, keep
   command and query definitions only in `operations/index.json`. Publish the
   mandatory `events/index.json` and `error/index.json` catalogs with stable
   `events/{event-id}.md` and `error/{code}.md` documents. Protobuf and JSON
   Schema models describe transport shape only; they never grant authority or
   redefine C/Q semantics. Run the managed gate after every graph change.
19. Host-agnostic standard: follow `GEMINI.md`, `CLAUDE.md`, and
   `.cursor/rules/new-project-standard.mdc` in addition to this file. Run
   `./scripts/install-agent-hosts.sh` once per clone so `.githooks/pre-commit`
   rejects commits that are not bound to an `IN_PROGRESS` `ticket-NNN`. Do
   not write on `main` or a dirty primary checkout. Markdown is not a
   substitute for the hook.

Markdown approval is an audit note, not trusted merge approval. Required
merge approval comes from the repository's protected review, attestation and
ruleset boundary.

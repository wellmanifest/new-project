# Worktree overlap guard

## Why this exists

`workspace_lifecycle_check.py` is a **terminal** audit: it finds worktrees left
behind after a merge. Nothing stopped two active tickets from editing the same
files for hours and discovering it only as a merge conflict.

This guard is the **active-development** counterpart. It is adopted the way
`pyqual.yaml` and `goal.yaml` are adopted: a declarative file that a runner
honours, plus a deterministic checker that can also be called directly.

HOME is `wellmanifest` as a `domain_pack`. There is no wellmanifest daemon —
the runtime is the adopted script inside each clone plus, optionally, a
`systemd --user` timer owned by the developer.

## What it detects

Discovery groups every checkout it can reach by **repository identity**
(`origin` URL, normalised; local origins are followed to their real repo), from
`git worktree list` plus sibling `.worktrees` / `.workspaces` directories in the
same organisation folder. When an identity has two or more checkouts:

| Code | Meaning |
| :--- | :--- |
| `GOV-WORKTREE-OVERLAP-001` | Dirty or unmerged paths intersect. `git status` plus `git diff` against the merge-base with the default branch. |
| `GOV-WORKTREE-OVERLAP-002` | Two `IN_PROGRESS` `intent.json` files claim overlapping `allowedPaths` and neither lists the other in `conflictsWith`. |
| `GOV-WORKTREE-OVERLAP-003` | The audit could not finish safely. |

Two rules keep the signal honest:

- **Ignored paths.** `TODO.md`, `project/TICKETS.md` and `project/ticket-*/**`
  are append-only or per-ticket by construction. Every intent declares them, so
  comparing them would make every pair of tickets overlap. Extend with
  `--ignore` or `pipeline.ignore`.
- **Ticket attribution.** A merged-but-still-`IN_PROGRESS` ticket directory is
  physically present in every sibling worktree. Only the checkout whose
  **branch** is that ticket's branch is credited with it, so a stale copy never
  becomes a phantom second writer. If no branch claims a ticket, the checkouts
  actually writing `project/<ticket>/` are credited instead.

Mere existence of a second worktree is allowed. Overlapping writes are not.

**Hooks run with `GIT_DIR` exported.** Inherited by a subprocess, `GIT_DIR`,
`GIT_WORK_TREE` and `GIT_INDEX_FILE` override `git -C <path>` and point every
call back at the repository being committed. The checker would then see one
checkout instead of the whole workspace and pass. Both scripts therefore strip
those variables before invoking git. Anything else calling the checker from a
hook context must do the same.

## Scope: repository vs workspace

The two questions are different, so the answers are separate:

- A **repository gate** (pre-commit, `pyqual`) answers *for its own repository*.
  It still discovers the whole workspace — that is how a worktree parked outside
  its own tree gets found — but it reports only on its own identity. Otherwise a
  conflict in an unrelated repo would block your commit.
- A **workspace scan** (timer, path unit) has no single identity to answer for
  and reports on everything it discovers.

`worktree_guard.py --scope auto` (the default) picks repository scope when
`--root` is a checkout and workspace scope otherwise. Force it with
`--scope repository` / `--scope workspace`, or pass
`worktree_overlap_check.py --identity-of <checkout>` directly.

## Install

### Per repository — fail closed at the moment of writing

```bash
./scripts/install-worktree-guard.sh --target /path/to/repo --wire-hook \
                                    --pyqual /path/to/repo/pyqual.yaml
```

Installs `worktree-guard.yaml`, `.governance/worktree_overlap_check.py`,
`.governance/worktree_guard.py`, `.governance/error/GOV-WORKTREE-OVERLAP.md`
and a **chainable** `pre-commit-worktree-guard`.

The hook goes into the directory git will actually read, taken from
`git rev-parse --git-path hooks`, so it honours `core.hooksPath`. Hard-coding
`.githooks/` installs a hook that never runs in any repository configured
otherwise — which was true of two of the three first adopters here. When that
directory turns out to be `.git/hooks` the installer says so: the hook works,
but it is machine-local and not shared with anyone cloning the repository.

`--wire-hook` chains the fragment into `pre-commit`, creating that file if it
does not exist and appending to it if it does. It never overwrites, and running
it twice does not duplicate the call. Without the flag the installer only
prints the line to add:

```bash
# <hooks dir>/pre-commit
"$(dirname "${BASH_SOURCE[0]}")/pre-commit-worktree-guard"
```

The call is appended **last**, because the fragment `exec`s the runner and
because a hand-written hook may already end in `exec`.

Once wired, a commit into a repository with an undeclared overlap fails. The
escape hatch is the normal one, `git commit --no-verify`, and it is the wrong
answer: the overlap is still there at merge time.

`--pyqual` inserts the stage textually, re-parses the result and compares the
parse tree against the expected structure. If the file does not have the
standard `pipeline: / custom_tools: / stages:` shape it is left **byte
identical** and the snippet is printed for a manual paste. Re-running is a
no-op. The same snippet comes from
`python3 scripts/worktree_guard.py --print-pyqual-stage`:

```yaml
custom_tools:
  - name: worktree_guard
    binary: python3
    command: python3 .governance/worktree_guard.py --root {workdir} --once
    allow_failure: false
stages:
  - name: worktree-overlap
    tool: worktree_guard
    optional: false
```

### Per workspace — catch overlap long before anyone commits

```bash
./scripts/install-worktree-guard.sh --workspace ~/github/subactor \
                                    --interval 300 --enable
```

Installs the runtime under `$XDG_DATA_HOME/worktree-guard/` — no repository is
touched — and writes three `systemd --user` template units:

| Unit | Trigger |
| :--- | :--- |
| `worktree-guard@.service` | The scan itself. `Type=oneshot`, `SuccessExitStatus=0 1`, so a *finding* is not a unit failure — the verdict lives in the report, the unit only records that the scan ran. |
| `worktree-guard@.timer` | `OnUnitActiveSec=<interval>`, default 300s. |
| `worktree-guard@.path` | `PathModified=%f/.worktrees` — fires the moment a worktree is added or removed. |

The instance name is the `systemd-escape --path` form of the workspace root, so
one template serves every workspace:

```bash
systemctl --user list-timers 'worktree-guard@*'
systemctl --user start worktree-guard@home-tom-github-subactor.service
cat ~/.local/state/worktree-guard/home-tom-github-subactor.json
```

Without a systemd session, the same two triggers exist in the foreground:

```bash
python3 .governance/worktree_guard.py --root . --watch --interval 60
```

`--watch` re-runs when `git worktree list` or the names under `.worktrees`
change.

## How it works in practice

1. An agent or a human starts a second worktree under `org/.worktrees/`.
2. The path unit fires within seconds; the timer re-checks every 5 minutes.
3. Both sides touch `src/frontend/src/App.tsx` → `GOV-WORKTREE-OVERLAP-001`
   appears in the report, naming both worktrees, both branches and the exact
   overlapping paths.
4. The pre-commit hook in that repository fails closed. It stays failed until
   one writer stops, the paths move to a single ticket, or the intents declare
   `conflictsWith` and serialise.
5. After the first ticket integrates, the second re-runs the guard and rebases.
   The conflict surface is only ever the overlapping files.

Measured on this workstation, 2026-08-19:

| Workspace | Checkouts | Scan | Findings |
| :--- | ---: | ---: | ---: |
| `~/github/wellmanifest` | 44 | ~3s | 8 |
| `~/github/subactor` | 114 | ~3.4s | 11 |

A representative subactor finding is `src/frontend/src/App.tsx` and
`src/php_app/index.php` dirty in both `www-sub-actor` (branch
`ticket/157-fix-app-missing-imports`) and
`.worktrees/www-sub-actor-ticket-126` — two branches rewriting the same React
entry point.

## Relation to other tooling

- **`semcod/code2llm`** — optional enrichment. When the binary is on `PATH` the
  report records how to analyse the overlapping Python paths. Detection itself
  is deterministic git plus intent JSON; no LLM is in the gate.
- **`pyqual`** — the guard is a normal `custom_tool` + non-optional stage, so
  `pyqual` fails the pipeline on overlap exactly as it does on `cc_max`.
- **`wup`** — a workspace already running `wup watch` can call
  `worktree_guard.py --root . --once` as a probe; the systemd timer covers the
  same ground for workspaces that do not.
- **`wellmanifest/git-lifecycle`** — `local-commit` and `integrate` require no
  undeclared overlap. Terminal worktree inventory stays with cleanup.
- **`wellmanifest/ticket-lifecycle`** — parallel worktrees are legal only with
  non-overlapping `allowedPaths` or an explicit `conflictsWith`.

## Uninstall

```bash
systemctl --user disable --now worktree-guard@<instance>.timer worktree-guard@<instance>.path
rm ~/.config/systemd/user/worktree-guard@.{service,timer,path}
rm -rf ~/.local/share/worktree-guard ~/.local/state/worktree-guard
# per repository
rm -f worktree-guard.yaml .githooks/pre-commit-worktree-guard \
      .governance/worktree_guard.py .governance/worktree_overlap_check.py \
      .governance/error/GOV-WORKTREE-OVERLAP.md
```

Nothing was added to `package-manifest.json`, so there is no managed entry to
unwind.

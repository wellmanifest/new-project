#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[[ -x "$root/scripts/install-agent-hosts.sh" ]] || fail "installer must be executable"
[[ -x "$root/.githooks/pre-commit" ]] || fail "hook must be executable"
grep -Fq 'GOV-AGENT-HOST-001' "$root/.githooks/pre-commit" || fail "hook must emit GOV-AGENT-HOST-001"
grep -Fq 'verify-pin --root "$root" --staged' "$root/template/files/pre-commit.template.sh" \
  || fail "managed hook must validate the staged local standard pin"
! grep -Eq 'git[[:space:]]+(fetch|pull)' "$root/template/files/pre-commit.template.sh" \
  || fail "managed pre-commit must never fetch or pull"
grep -Fq 'new-ticket.sh' "$root/GEMINI.md" || fail "GEMINI.md must require new-ticket.sh"
grep -Fq 'new-ticket.sh' "$root/CLAUDE.md" || fail "CLAUDE.md must require new-ticket.sh"
grep -Fq 'alwaysApply: true' "$root/.cursor/rules/new-project-standard.mdc" || fail "Cursor rule must alwaysApply"
grep -Fq '<!-- wellmanifest:source-links:v1 -->' "$root/AGENTS.md" \
  || fail "AGENTS.md must expose the managed source-links marker"
grep -Fq 'https://github.com/wellmanifest/worktrees/blob/main/models/worktrees.schema.json' "$root/AGENTS.md" \
  || fail "AGENTS.md must link a concrete wellmanifest dependency file"

# Host guidance must agree with the allocator and C-CONCURRENCY-002; offline
# allocation is valid and does not authorize an unsolicited remote refresh.
python3 - "$root" <<'PYREFRESH'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
for path in ('AGENTS.md', 'template/files/AGENTS.template.md'):
    text = ' '.join((root / path).read_text().split())
    assert 'local and already-fetched remote refs' in text, path
    assert 'Fetch/prune only when explicitly requested via `--refresh-remote`' in text, path
    assert 'after fetching/pruning' not in text, path
contributing = (root / 'CONTRIBUTING.md').read_text()
assert 'DO FETCH_AND_PRUNE_KNOWN_REMOTE_REFS WHEN REMOTE_REFRESH_EXPLICITLY_REQUESTED' in contributing
assert '`VERSION 17`' not in contributing
assert 'WHEN MATERIAL_SCOPE_AUTHORITY_DESTRUCTIVE_OR_PUBLICATION_DECISION_MADE' in contributing
assert 'WHEN AGENT_DECISION_AFFECTS_REPOSITORY_STATE' not in contributing
assert 'TO "project/{TICKET_ID}/decisions.md" WHEN NO_MATCHING_RECOMPUTABLE_EVIDENCE_EXISTS' in contributing
assert 'FORBID RECURSIVE_CHECKPOINT_OR_DECISION_FOR_WRITING_THE_CHECKPOINT_ITSELF' in contributing
for path in ('AGENTS.md', 'template/files/AGENTS.template.md'):
    text = ' '.join((root / path).read_text().split())
    assert 'Reuse the matching authorized ticket/worktree before allocating another' in text, path
    assert 'not chat-agent count' in text, path
    assert 'Worktrees v5 still requires a canonical linked delivery checkout' in text, path
    assert 'classify-action --action <action>' in text, path
    assert 'Do not recursively log the act of writing evidence' in text, path
    assert 'branch/worktree per implementation ticket' not in text, path
policy = (root / 'POLICY.md').read_text()
assert 'DO REUSE_MATCHING_AUTHORIZED_CHECKOUT_BEFORE_CONSIDERING_NEW_ALLOCATION' in policy
assert 'FORBID INFER_SINGLE_WRITER_FROM_CHAT_PARTICIPANT_COUNT' in policy
assert 'DO FINALIZE_TRACKED_CARRIERS_AND_CHECK_FORMAT_BEFORE_SNAPSHOT_AND_LEASE_RELEASE' in policy
sys.path.insert(0, str(root / 'scripts'))
from policy_dsl_check import parse_markdown
rules = {rule['id']: rule for rule in parse_markdown(contributing)['rules']}
allocation = next(action for action in rules['C-CONCURRENCY-005']['actions'] if action['opcode'] == 'ALLOCATE')
append = next(action for action in rules['C-DECISION-001']['actions'] if action['opcode'] == 'APPEND')
assert allocation['guard'] is not None, 'allocation must be conditional, not an unconditional opcode'
assert append['guard'] is not None, 'reuse must prevent unconditional duplicate append'
parse_markdown(policy)
PYREFRESH

echo "== proportional action classification has no filesystem effects =="
python3 - "$root" <<'PYCLASSIFY'
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root / 'scripts'))
from decision_record import ACTION_EVIDENCE, classify_action

routine = {'read-only', 'local-check', 'routine-edit', 'format', 'evidence-write', 'checkpoint'}
material = {'scope-change', 'authority-change', 'publication', 'destructive-change'}
assert set(ACTION_EVIDENCE) == routine | material
expected_fields = {'schema', 'action', 'decisionRecordRequired', 'evidenceKind',
                   'reuseMatchingEvidence', 'createsWorktree', 'grantsAuthority'}
with tempfile.TemporaryDirectory(prefix='decision-classify-') as directory:
    for action in sorted(routine | material):
        result = subprocess.run(
            [sys.executable, str(root / 'scripts/decision_record.py'),
             'classify-action', '--action', action],
            cwd=directory, capture_output=True, text=True, check=True)
        report = json.loads(result.stdout)
        assert set(report) == expected_fields, report
        assert report == classify_action(action)
        assert report['schema'] == 'new-project.action-classification/v1'
        assert report['decisionRecordRequired'] == (action in material)
        assert report['reuseMatchingEvidence'] is True
        assert report['createsWorktree'] is False
        assert report['grantsAuthority'] is False
        assert 'verdict' not in report and 'APPROVE' not in result.stdout
        assert not list(Path(directory).iterdir()), 'classification wrote artifacts'
    for arguments in ([], ['--action', 'invented'], ['--action', 'local-check', '--approve']):
        bad = subprocess.run([sys.executable, str(root / 'scripts/decision_record.py'),
                              'classify-action', *arguments],
                             cwd=directory, capture_output=True, text=True)
        assert bad.returncode == 2, arguments
        assert not list(Path(directory).iterdir())
for value in ('invented', '', None, [], {'action': 'local-check'}):
    try:
        classify_action(value)
    except ValueError:
        pass
    else:
        raise AssertionError('untyped or unknown action accepted')
print('10 action classes and negative/no-effect cases: PASS')
PYCLASSIFY

# Activating the hub must resolve runtime sources instead of requiring a
# duplicate adopter .governance tree. Missing source files still fail closed.
python3 - "$root" "$tmp/hub" <<'PYHUB'
import json,pathlib,shutil,subprocess,sys
source=pathlib.Path(sys.argv[1]);target=pathlib.Path(sys.argv[2]);target.mkdir()
contract=json.loads((source/'governance/agent-hosts.json').read_text())
package=json.loads((source/'governance/package-manifest.json').read_text())
paths={row['target']:row['source'] for row in package['files']}
files=[h['file'] for h in contract['hosts']]+[contract['hook']['path']]
files += [paths.get(p,p) for p in contract['hook']['runtimeFiles']]
files += ['governance/agent-hosts.json','governance/manifest.hub.json','governance/package-manifest.json','scripts/install-agent-hosts.sh']
for name in files:
    dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,dst)
subprocess.run(['git','init','--quiet',str(target)],check=True)
subprocess.run(['bash','scripts/install-agent-hosts.sh'],cwd=target,check=True)
subprocess.run(['bash','scripts/install-agent-hosts.sh','--check'],cwd=target,check=True)
assert not (target/'.governance').exists()
(target/paths[contract['hook']['runtimeFiles'][0]]).unlink()
failure=subprocess.run(['bash','scripts/install-agent-hosts.sh','--check'],cwd=target,capture_output=True,text=True)
assert failure.returncode != 0 and 'GOV-AGENT-HOST-004' in failure.stderr
PYHUB

# Activation must reject disabled hooks and malformed contracts without effects.
python3 - "$root" "$tmp/activation" <<'PYACT'
import json, pathlib, shutil, subprocess, sys
source, target = map(pathlib.Path, sys.argv[1:])
target.mkdir()
subprocess.run(['git', 'init', '--quiet', str(target)], check=True)
def run(*args):
    return subprocess.run(['bash', str(source/'scripts/install-agent-hosts.sh'),
                           '--source', str(source), '--target', str(target), *args],
                          capture_output=True, text=True)
assert run().returncode == 0
hook = target/'.githooks/pre-commit'
hook.chmod(0o644)
result = run('--check')
assert result.returncode != 0, 'disabled hook incorrectly reported active'
assert hook.stat().st_mode & 0o111 == 0, '--check mutated permissions'
contract = target/'.governance/agent-hosts.json'
original = contract.read_text()
value = json.loads(original)
del value['hosts']
contract.write_text(json.dumps(value))
subprocess.run(['git', '-C', str(target), 'config', '--unset', 'core.hooksPath'], check=True)
result = subprocess.run(['bash', str(source/'scripts/install-agent-hosts.sh'),
                         '--source', str(target), '--target', str(target)],
                        capture_output=True, text=True)
assert result.returncode != 0, 'malformed contract incorrectly activated'
assert subprocess.run(['git', '-C', str(target), 'config', '--get', 'core.hooksPath'],
                      capture_output=True).returncode != 0
contract.write_text(original)
# Bootstrap preflights all sources before overwriting any target file.
broken = target.parent/'broken-source'
shutil.copytree(source, broken, ignore=shutil.ignore_patterns('.git', '.worktrees', 'worktrees'))
package = json.loads((broken/'governance/package-manifest.json').read_text())
files = {row['target']:row['source'] for row in package['files']}
missing = json.loads(original)['hook']['runtimeFiles'][-1]
(broken/files[missing]).unlink()
(target/'GEMINI.md').write_text('existing instructions\n')
result = subprocess.run(['bash', str(source/'scripts/install-agent-hosts.sh'),
                         '--source', str(broken), '--target', str(target)],
                        capture_output=True, text=True)
assert result.returncode != 0
assert (target/'GEMINI.md').read_text() == 'existing instructions\n', 'partial bootstrap overwrite'
# A missing manifest mapping is also rejected before copying host instructions.
shutil.copy2(source/files[missing], broken/files[missing])
package['files'] = [row for row in package['files'] if row['target'] != missing]
(broken/'governance/package-manifest.json').write_text(json.dumps(package))
result = subprocess.run(['bash', str(source/'scripts/install-agent-hosts.sh'),
                         '--source', str(broken), '--target', str(target)],
                        capture_output=True, text=True)
assert result.returncode != 0
assert (target/'GEMINI.md').read_text() == 'existing instructions\n'
PYACT

mapfile -t closed_statuses < <(python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
hub = json.loads((root / "governance/manifest.hub.json").read_text())
default = json.loads((root / "governance/manifest.default.json").read_text())
hub_statuses = hub["ticket"]["closedStatuses"]
default_statuses = default["ticket"]["closedStatuses"]
if hub_statuses != default_statuses:
    raise SystemExit("hub and adopter manifests declare different closedStatuses")
print("\n".join(hub_statuses))
PY
)
[[ "${closed_statuses[*]}" == "DONE CANCELLED" ]] \
  || fail "terminal hook regression must cover every declared closed status"
for closed_status in "${closed_statuses[@]}"; do
  grep -Fq "$closed_status" "$root/.githooks/pre-commit" \
    || fail "hub hook must recognize declared terminal status $closed_status"
  grep -Fq "$closed_status" "$root/template/files/pre-commit.template.sh" \
    || fail "adopter hook must recognize declared terminal status $closed_status"
done

mapfile -t non_active_statuses < <(python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
hub = json.loads((root / "governance/manifest.hub.json").read_text())
default = json.loads((root / "governance/manifest.default.json").read_text())
hub_statuses = hub["ticket"]["nonActiveStatuses"]
default_statuses = default["ticket"]["nonActiveStatuses"]
if hub_statuses != default_statuses:
    raise SystemExit("hub and adopter manifests declare different nonActiveStatuses")
print("\n".join(hub_statuses))
PY
)
[[ "${non_active_statuses[*]}" == "BACKLOG PLAN BLOCKED" ]] \
  || fail "non-active hook regression must cover every declared non-active status"
for non_active_status in "${non_active_statuses[@]}"; do
  grep -Fq "$non_active_status" "$root/.githooks/pre-commit" \
    || fail "hub hook must recognize declared non-active status $non_active_status"
  grep -Fq "$non_active_status" "$root/template/files/pre-commit.template.sh" \
    || fail "adopter hook must recognize declared non-active status $non_active_status"
done

python3 - "$root" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
package = json.loads((root / "governance/package-manifest.json").read_text())
findings = []
for entry in package["files"]:
    if entry["strategy"] not in {"managed", "extendable"}:
        continue
    source = root / entry["source"]
    for number, line in enumerate(source.read_bytes().splitlines(), start=1):
        if line.endswith((b" ", b"\t")):
            findings.append(f"{entry['source']}:{number}")
if findings:
    print("managed package sources contain trailing whitespace:", file=sys.stderr)
    print("\n".join(findings), file=sys.stderr)
    raise SystemExit(1)
PY

git init -q "$tmp/adopter"
git -C "$tmp/adopter" config user.email "test@example.com"
git -C "$tmp/adopter" config user.name "Test"
git -C "$tmp/adopter" config commit.gpgsign false
echo "readme" > "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
git -C "$tmp/adopter" commit -qm "seed"
"$root/scripts/install-agent-hosts.sh" --source "$root" --target "$tmp/adopter"
[[ -f "$tmp/adopter/GEMINI.md" ]] || fail "installer must copy GEMINI.md"
[[ -f "$tmp/adopter/CLAUDE.md" ]] || fail "installer must copy CLAUDE.md"
[[ -x "$tmp/adopter/.githooks/pre-commit" ]] || fail "installer must copy executable hook"
[[ -f "$tmp/adopter/.governance/worktree_guard.py" ]] || fail "installer must copy worktree guard"
[[ "$(git -C "$tmp/adopter" config --get core.hooksPath)" == ".githooks" ]] || fail "installer must set core.hooksPath"

# Replace the real runner with a deterministic spy. The overlap algorithm has
# its own suite; this fixture proves the managed lifecycle hook composes it into
# every successful path and propagates a negative verdict.
cat > "$tmp/adopter/.governance/worktree_guard.py" <<'PY'
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
counter = root / ".guard-invocations"
count = int(counter.read_text(encoding="utf-8")) if counter.exists() else 0
counter.write_text(str(count + 1), encoding="utf-8")
if (root / ".guard-fail").exists():
    print("GOV-WORKTREE-OVERLAP-FAIL: deterministic fixture rejection", file=sys.stderr)
    raise SystemExit(1)
PY

echo "change" >> "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
if git -C "$tmp/adopter" commit -qm "unbound"; then
  fail "commit on main without a ticket must be rejected"
fi
git -C "$tmp/adopter" checkout -qb ticket/001-demo
if git -C "$tmp/adopter" commit -qm "missing ticket dir"; then
  fail "ticket branch without project/ticket-001 must be rejected"
fi

mkdir -p "$tmp/adopter/project/ticket-001"
cat > "$tmp/adopter/project/ticket-001/README.md" <<'EOF'
# Ticket 001

- **Status**: BACKLOG
EOF
git -C "$tmp/adopter" add project/ticket-001/README.md README.md
if git -C "$tmp/adopter" commit -qm "not in progress"; then
  fail "BACKLOG ticket must be rejected"
fi

sed -i 's/BACKLOG/IN_PROGRESS/' "$tmp/adopter/project/ticket-001/README.md"
git -C "$tmp/adopter" add project/ticket-001/README.md README.md

touch "$tmp/adopter/.guard-fail"
if git -C "$tmp/adopter" commit -qm "overlap verdict bypass" 2> "$tmp/guard-fail.err"; then
  fail "negative worktree guard verdict must reject an IN_PROGRESS commit"
fi
grep -Fq 'GOV-WORKTREE-OVERLAP-FAIL' "$tmp/guard-fail.err" \
  || fail "negative guard verdict must remain visible"
[[ "$(cat "$tmp/adopter/.guard-invocations")" == "1" ]] \
  || fail "IN_PROGRESS path must invoke the guard before rejecting"
rm "$tmp/adopter/.guard-fail"
git -C "$tmp/adopter" commit -qm "bound to ticket-001" || fail "IN_PROGRESS ticket branch must commit"
[[ "$(cat "$tmp/adopter/.guard-invocations")" == "2" ]] \
  || fail "IN_PROGRESS success must invoke the guard"

for non_active_status in "${non_active_statuses[@]}"; do
  sed -i "s/IN_PROGRESS/$non_active_status/" "$tmp/adopter/project/ticket-001/README.md"
  git -C "$tmp/adopter" add project/ticket-001/README.md
  git -C "$tmp/adopter" commit -qm "pause ticket-001 as $non_active_status" \
    || fail "$non_active_status governance-only transition must commit"

  echo "implementation while $non_active_status" >> "$tmp/adopter/README.md"
  git -C "$tmp/adopter" add README.md
  if git -C "$tmp/adopter" commit -qm "non-active implementation"; then
    fail "$non_active_status ticket must reject implementation"
  fi
  git -C "$tmp/adopter" reset -q --hard HEAD

  sed -i "s/$non_active_status/IN_PROGRESS/" "$tmp/adopter/project/ticket-001/README.md"
  git -C "$tmp/adopter" add project/ticket-001/README.md
  git -C "$tmp/adopter" commit -qm "resume ticket-001 from $non_active_status" \
    || fail "IN_PROGRESS resume from $non_active_status must commit"
done
[[ "$(cat "$tmp/adopter/.guard-invocations")" == "8" ]] \
  || fail "non-active transitions and resumes must invoke the guard"

# The pin validator reads only the local staged manifest, lock and managed
# digests. A command spy proves that no fetch/pull is attempted, and the check
# leaves both HEAD and the index/worktree status unchanged.
pinrepo="$tmp/pinrepo"
mkdir -p "$pinrepo/.subactor" "$pinrepo/.governance" "$tmp/fakebin"
git init -q "$pinrepo"
git -C "$pinrepo" config user.email "test@example.com"
git -C "$pinrepo" config user.name "Test"
cp "$root/.subactor/manifest.json" "$pinrepo/.subactor/manifest.json"
cp "$root/.subactor/.gitignore" "$pinrepo/.subactor/.gitignore"
cp "$root/scripts/work_continuity.py" "$pinrepo/.governance/work_continuity.py"
python3 - "$pinrepo" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
managed = {}
for relative in ('.subactor/manifest.json', '.subactor/.gitignore'):
    managed[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.20.18',
        'sourceRepository': 'wellmanifest/new-project',
        'sourceRevision': '1' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': managed,
}
(root / '.governance/manifest.lock.json').write_text(
    json.dumps(lock, indent=2) + '\n', encoding='utf-8'
)
PY
git -C "$pinrepo" add .
real_git="$(command -v git)"
cat > "$tmp/fakebin/git" <<EOF
#!/usr/bin/env bash
printf '%s\n' "\$*" >> "\$GIT_TRACE_ARGS"
exec "$real_git" "\$@"
EOF
chmod +x "$tmp/fakebin/git"
pin_trace="$tmp/pin-git-commands"
before_pin_status="$(git -C "$pinrepo" status --porcelain=v1)"
before_pin_head="$(git -C "$pinrepo" rev-parse --verify HEAD 2>/dev/null || true)"
GIT_TRACE_ARGS="$pin_trace" PATH="$tmp/fakebin:$PATH" \
  python3 "$pinrepo/.governance/work_continuity.py" verify-pin \
    --root "$pinrepo" --staged > "$tmp/pin-pass.json"
grep -q '"networkAccess": false' "$tmp/pin-pass.json"
grep -q '"mutated": false' "$tmp/pin-pass.json"
! grep -Eq '(^| )(fetch|pull)( |$)' "$pin_trace" || fail "pin validation used the network"
[[ "$(git -C "$pinrepo" status --porcelain=v1)" == "$before_pin_status" ]] \
  || fail "pin validation mutated index or worktree"
[[ "$(git -C "$pinrepo" rev-parse --verify HEAD 2>/dev/null || true)" == "$before_pin_head" ]] \
  || fail "pin validation mutated HEAD"

python3 - "$pinrepo/.subactor/manifest.json" <<'PY'
import json
import sys
path = sys.argv[1]
value = json.load(open(path, encoding='utf-8'))
value['continuity']['checkpointIndexMaxEntries'] = 1
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PY
git -C "$pinrepo" add .subactor/manifest.json
status=0
python3 "$pinrepo/.governance/work_continuity.py" verify-pin \
  --root "$pinrepo" --staged > "$tmp/pin-drift.out" 2> "$tmp/pin-drift.err" || status=$?
test "$status" -eq 2
grep -Fq 'GOV-CONTINUITY-001' "$tmp/pin-drift.err"

# Status authority comes from the staged snapshot. An unstaged IN_PROGRESS
# working-tree value must not authorize a staged BACKLOG ticket plus source.
sed -i 's/IN_PROGRESS/BACKLOG/' "$tmp/adopter/project/ticket-001/README.md"
git -C "$tmp/adopter" add project/ticket-001/README.md
sed -i 's/BACKLOG/IN_PROGRESS/' "$tmp/adopter/project/ticket-001/README.md"
echo "staged bypass" >> "$tmp/adopter/README.md"
git -C "$tmp/adopter" add README.md
if git -C "$tmp/adopter" commit -qm "staged status bypass"; then
  fail "unstaged IN_PROGRESS must not override staged BACKLOG"
fi
git -C "$tmp/adopter" reset -q --hard HEAD

# Tracking carriers cannot manufacture a repository delivery on their own.
printf '%s\n' 'status-only evidence' >> "$tmp/adopter/project/ticket-001/README.md"
git -C "$tmp/adopter" add project/ticket-001/README.md
if git -C "$tmp/adopter" commit -qm "ticket-only status" 2> "$tmp/tracking-only.err"; then
  fail "ticket-only commit must be rejected"
fi
grep -Fq 'GOV-AGENT-HOST-007' "$tmp/tracking-only.err" \
  || fail "ticket-only rejection must expose GOV-AGENT-HOST-007"
git -C "$tmp/adopter" reset -q --hard HEAD

# Terminal state belongs to the protected external receipt. Neither a
# governance-only payload nor a material payload may create a closure commit.
for terminal_status in DONE CANCELLED; do
  sed -i "s/IN_PROGRESS/$terminal_status/" "$tmp/adopter/project/ticket-001/README.md"
  echo "attempted $terminal_status closure" >> "$tmp/adopter/README.md"
  git -C "$tmp/adopter" add project/ticket-001/README.md README.md
  if git -C "$tmp/adopter" commit -qm "terminal closure $terminal_status" 2> "$tmp/terminal.err"; then
    fail "$terminal_status repository closure must be rejected"
  fi
  grep -Fq 'GOV-AGENT-HOST-003' "$tmp/terminal.err" \
    || fail "$terminal_status closure must expose GOV-AGENT-HOST-003"
  git -C "$tmp/adopter" reset -q --hard HEAD
done

user_home="$tmp/home"
mkdir -p "$user_home/.gemini" "$user_home/.claude"
printf "Existing private instruction\n" > "$user_home/.gemini/GEMINI.md"
printf "Existing private instruction\n" > "$user_home/.claude/CLAUDE.md"
HOME="$user_home" "$root/scripts/install-agent-hosts.sh" --source "$root" --user
[[ -f "$user_home/.cursor/rules/new-project-standard.mdc" ]] || fail "--user must install Cursor rule"
grep -Fq 'wellmanifest/new-project host contract' "$user_home/.gemini/GEMINI.md" || fail "--user must install Gemini pointer"
grep -Fq 'wellmanifest/new-project host contract' "$user_home/.claude/CLAUDE.md" || fail "--user must install Claude pointer"

grep -Fq 'Existing private instruction' "$user_home/.gemini/GEMINI.md" || fail "preserve Gemini instructions"
grep -Fq 'Existing private instruction' "$user_home/.claude/CLAUDE.md" || fail "preserve Claude instructions"
HOME="$user_home" "$root/scripts/install-agent-hosts.sh" --source "$root" --user
[[ "$(grep -Fc 'wellmanifest/new-project host contract' "$user_home/.gemini/GEMINI.md")" == 1 ]] || fail "user pointer must be idempotent"
grep -Fq 'git worktree list' "$user_home/.claude/CLAUDE.md" || fail "user pointer must discover governance from registered checkouts"

# --- ticket-233: legacy pointer paragraphs converge without losing private text
legacy_home="$tmp/legacy-home"
mkdir -p "$legacy_home/.gemini" "$legacy_home/.claude"
cat > "$legacy_home/.claude/CLAUDE.md" <<'EOF'
Private preamble

# wellmanifest/new-project host contract

When the current repository has `./project/new-ticket.sh`, follow that
repository's `CLAUDE.md` and `AGENTS.md`. Allocate tickets only through
that script. Never commit on main or a dirty primary checkout.

# Private section
Keep this instruction
EOF
printf '# wellmanifest/new-project host contract\n\nWhen the current repository has `./project/new-ticket.sh`, follow that\nrepository'"'"'s host contract and `AGENTS.md`.\n' > "$legacy_home/.gemini/GEMINI.md"
HOME="$legacy_home" "$root/scripts/install-agent-hosts.sh" --source "$root" --user
for pointer in "$legacy_home/.claude/CLAUDE.md" "$legacy_home/.gemini/GEMINI.md"; do
  [[ "$(grep -Fc 'wellmanifest/new-project host contract' "$pointer")" == 1 ]] || fail "legacy pointer must keep one marker"
  grep -Fq 'git worktree list' "$pointer" || fail "legacy pointer must be upgraded"
  ! grep -Fq 'When the current repository has' "$pointer" || fail "legacy paragraph must be replaced"
done
grep -Fq 'Private preamble' "$legacy_home/.claude/CLAUDE.md" || fail "preserve text before the pointer"
grep -Fq 'Keep this instruction' "$legacy_home/.claude/CLAUDE.md" || fail "preserve sections after the pointer"
before="$(sha256sum "$legacy_home/.claude/CLAUDE.md")"
HOME="$legacy_home" "$root/scripts/install-agent-hosts.sh" --source "$root" --user
[[ "$(sha256sum "$legacy_home/.claude/CLAUDE.md")" == "$before" ]] || fail "upgraded pointer must be byte-stable"

# --- ticket-106: deterministic host and packaging validator -------------------

checker="$root/scripts/agent_host_check.py"
[[ -f "$checker" ]] || fail "agent_host_check.py must exist"

# The validator exits non-zero on findings, which is the behaviour under test;
# capture the report first so pipefail does not abort the suite.
codes() {
  local report="$tmp/agent-host-report.json"
  python3 "$checker" --root "$1" --actor "${2:-agent}" --format json > "$report" || true
  python3 -c 'import json,sys; print(" ".join(f["code"] for f in json.load(open(sys.argv[1]))["findings"]))' "$report"
}

assert_has() {
  local haystack="$1" needle="$2" context="$3"
  [[ "$haystack" == *"$needle"* ]] || fail "$context: expected $needle in '$haystack'"
}

assert_lacks() {
  local haystack="$1" needle="$2" context="$3"
  [[ "$haystack" != *"$needle"* ]] || fail "$context: unexpected $needle in '$haystack'"
}

fixture="$tmp/fixture"
mkdir -p "$fixture/.governance" "$fixture/.cursor/rules" "$fixture/.githooks"
git init -q "$fixture"
git -C "$fixture" config user.email "test@example.com"
git -C "$fixture" config user.name "Test"
cp "$root/governance/agent-hosts.json" "$fixture/.governance/agent-hosts.json"
mkdir -p "$fixture/governance" "$fixture/.github/workflows"
cp "$root/governance/required-checks.json" "$fixture/governance/required-checks.json"
cp "$root/.github/workflows/ci.yml" "$fixture/.github/workflows/ci.yml"
# Derive the fixture's host files from the contract, so adding a host to
# agent-hosts.json cannot silently leave this fixture behind.
while read -r host_file; do
  mkdir -p "$fixture/$(dirname "$host_file")"
  printf '%s\n' "stub" > "$fixture/$host_file"
done < <(python3 -c '
import json, sys
contract = json.load(open(sys.argv[1], encoding="utf-8"))
print("\n".join(host["file"] for host in contract["hosts"]))
' "$fixture/.governance/agent-hosts.json")
# The fixture is an adopter, so use the adopter projections rather than the
# hub's local manifest links. This also proves every declared host receives the
# same source-link block as a real package adoption.
cp "$root/template/files/AGENTS.template.md" "$fixture/AGENTS.md"
cp "$root/template/files/CLAUDE.template.md" "$fixture/CLAUDE.md"
cp "$root/template/files/GEMINI.template.md" "$fixture/GEMINI.md"
cp "$root/template/files/cursor-rule.template.mdc" "$fixture/.cursor/rules/new-project-standard.mdc"
cp "$root/template/files/aider.template.yml" "$fixture/.aider.conf.yml"
cp "$root/template/files/copilot-instructions.template.md" "$fixture/.github/copilot-instructions.md"
printf '%s\n' '#!/usr/bin/env bash' > "$fixture/.githooks/pre-commit"
chmod +x "$fixture/.githooks/pre-commit"
cat > "$fixture/.governance/manifest.lock.json" <<'LOCK'
{
  "schema": "new-project.lock/v1",
  "standard": {
    "id": "wellmanifest/new-project",
    "publicationStatus": "published",
    "sourceRepository": "wellmanifest/new-project",
    "sourceRevision": "1111111111111111111111111111111111111111",
    "version": "9.9.9"
  },
  "managedFiles": {}
}
LOCK

# An unset core.hooksPath means no commit in this clone is actually gated.
assert_has "$(codes "$fixture")" "GOV-AGENT-HOST-006" "unset hooksPath"
# CI checkouts never run local hooks, so that finding must not fire there.
assert_lacks "$(codes "$fixture" ci)" "GOV-AGENT-HOST-006" "ci actor"

git -C "$fixture" config core.hooksPath .githooks
[[ -z "$(codes "$fixture")" ]] || fail "activated fixture must pass: $(codes "$fixture")"

# Removing one concrete source link is a fail-closed host-contract finding.
sed -i '/worktrees.schema.json/d' "$fixture/AGENTS.md"
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "missing AGENTS source link"
cp "$root/template/files/AGENTS.template.md" "$fixture/AGENTS.md"

# A URL that does not match its declared repository/path is also rejected.
python3 - "$fixture/.governance/agent-hosts.json" <<'PY'
import json
import sys
path = sys.argv[1]
value = json.load(open(path, encoding='utf-8'))
value['sourceLinks']['remote'][0]['url'] = 'https://github.com/wellmanifest/new-project/blob/main/wrong.md'
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PY
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "non-canonical source link"
cp "$root/governance/agent-hosts.json" "$fixture/.governance/agent-hosts.json"

# Duplicate remote identifiers cannot silently shadow one another.
python3 - "$fixture/.governance/agent-hosts.json" <<'PY'
import json
import sys
path = sys.argv[1]
value = json.load(open(path, encoding='utf-8'))
value['sourceLinks']['remote'].append(dict(value['sourceLinks']['remote'][0]))
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PY
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "duplicate source link id"
cp "$root/governance/agent-hosts.json" "$fixture/.governance/agent-hosts.json"

# A host that loses the bounded-session controls must fail before an agent can
# spend a long retry loop on an impossible task.
cp "$fixture/AGENTS.md" "$fixture/AGENTS.md.anomaly-backup"
sed -i '/## Bounded session controls/,$d' "$fixture/AGENTS.md"
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "missing bounded-session controls"
mv "$fixture/AGENTS.md.anomaly-backup" "$fixture/AGENTS.md"

# Contradictory directives are checked only when both explicitly configured
# patterns occur in one host projection; ordinary scoped prose remains valid.
cp "$fixture/AGENTS.md" "$fixture/AGENTS.md.anomaly-backup"
printf '%s\n' 'push directly to main' 'never push directly to main' >> "$fixture/AGENTS.md"
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "contradictory host directives"
mv "$fixture/AGENTS.md.anomaly-backup" "$fixture/AGENTS.md"

# A host limit that would truncate the instruction chain is a deterministic
# blocker, not a reason to continue with partial policy.
python3 - "$fixture/.governance/agent-hosts.json" <<'PYANOMALY_SIZE'
import json, sys
path = sys.argv[1]
value = json.load(open(path, encoding='utf-8'))
value['anomalyChecks']['maxInstructionBytes'] = 10
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PYANOMALY_SIZE
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "oversized host guidance"
cp "$root/governance/agent-hosts.json" "$fixture/.governance/agent-hosts.json"

# Required checks that no workflow publishes would otherwise block every PR
# forever while looking like a valid declaration.
python3 - "$fixture/governance/required-checks.json" <<'PYANOMALY_CI'
import json, sys
path = sys.argv[1]
value = json.load(open(path, encoding='utf-8'))
value['requiredCheckNames'] = ['missing-forever']
open(path, 'w', encoding='utf-8').write(json.dumps(value, indent=2) + '\n')
PYANOMALY_CI
assert_has "$(codes "$fixture" ci)" "GOV-AGENT-HOST-004" "unpublished required check"
cp "$root/governance/required-checks.json" "$fixture/governance/required-checks.json"

# A missing host instruction file fails closed.
mv "$fixture/GEMINI.md" "$fixture/GEMINI.md.bak"
assert_has "$(codes "$fixture")" "GOV-AGENT-HOST-004" "missing host file"
mv "$fixture/GEMINI.md.bak" "$fixture/GEMINI.md"

# Bootstrap into a fresh clone must deliver the contract too, not only the
# instruction files: without it the target cannot be activated at all.
[[ -f "$tmp/adopter/.governance/agent-hosts.json" ]] || fail "bootstrap must copy the host contract"
[[ -f "$tmp/adopter/.cursor/rules/new-project-standard.mdc" ]] \
  || fail "bootstrap must copy every declared host file"

# A hook that cannot execute is the same defect as a hook that is absent.
chmod -x "$fixture/.githooks/pre-commit"
assert_has "$(codes "$fixture")" "GOV-AGENT-HOST-005" "non-executable hook"
chmod +x "$fixture/.githooks/pre-commit"

# A stack marker with no governance declaration and no lifecycle binding.
cat > "$fixture/pyproject.toml" <<'TOML'
[project]
name = "fixture"
version = "0.1.0"
TOML
observed="$(codes "$fixture")"
assert_has "$observed" "GOV-PACKAGING-001" "undeclared pyproject"
assert_has "$observed" "GOV-PACKAGING-003" "unbound pytest lifecycle"

# A declaration that drifted away from the adoption lock.
cat > "$fixture/pyproject.toml" <<'TOML'
[project]
name = "fixture"
version = "0.1.0"

[tool.wellmanifest]
standard = "0.0.1"
revision = "1111111111111111111111111111111111111111"
gate = "project/governance-check.sh"

[tool.pytest.ini_options]
addopts = "-p wellmanifest_governance"
TOML
mkdir -p "$fixture/project"
printf '%s\n' '#!/usr/bin/env bash' > "$fixture/project/governance-check.sh"
observed="$(codes "$fixture")"
assert_has "$observed" "GOV-PACKAGING-002" "drifted standard version"
assert_lacks "$observed" "GOV-PACKAGING-003" "bound pytest lifecycle"

# The same declaration in agreement with the lock passes.
sed -i 's/standard = "0.0.1"/standard = "9.9.9"/' "$fixture/pyproject.toml"
[[ -z "$(codes "$fixture")" ]] || fail "aligned pyproject must pass: $(codes "$fixture")"

# npm is the one ecosystem that can install the hook without being asked.
cat > "$fixture/package.json" <<'JSON'
{
  "name": "fixture",
  "version": "0.1.0",
  "wellmanifest": {
    "standard": "9.9.9",
    "revision": "1111111111111111111111111111111111111111",
    "gate": "project/governance-check.sh"
  }
}
JSON
assert_has "$(codes "$fixture")" "GOV-PACKAGING-003" "missing npm prepare"
python3 - "$fixture/package.json" <<'PYNPM'
import json, sys
path = sys.argv[1]
document = json.load(open(path, encoding="utf-8"))
document["scripts"] = {"prepare": "./scripts/install-agent-hosts.sh"}
json.dump(document, open(path, "w", encoding="utf-8"), indent=2)
PYNPM
[[ -z "$(codes "$fixture")" ]] || fail "aligned package.json must pass: $(codes "$fixture")"

# An adopter may declare requires-python >=3.10, where tomllib does not exist.
# The validator must still import and skip the Python packaging binding: an
# ImportError here reaches governance_check.py as a missing managed validator,
# which turns an interpreter gap into a false GOV-SYNC-001 sync defect.
codes_without_tomllib() {
  local report="$tmp/agent-host-report-no-tomllib.json"
  FIXTURE_ROOT="$1" CHECKER_PATH="$checker" python3 - > "$report" <<'PYNOTOML' || true
import os, runpy, sys

sys.modules["tomllib"] = None  # `import tomllib` now raises ImportError
sys.argv = [
    "agent_host_check",
    "--root", os.environ["FIXTURE_ROOT"],
    "--actor", "agent",
    "--format", "json",
]
runpy.run_path(os.environ["CHECKER_PATH"], run_name="__main__")
PYNOTOML
  python3 -c 'import json,sys; print(" ".join(f["code"] for f in json.load(open(sys.argv[1]))["findings"]))' "$report"
}

observed="$(codes_without_tomllib "$fixture")"
assert_lacks "$observed" "GOV-PACKAGING-001" "python marker unreadable without tomllib"
assert_lacks "$observed" "GOV-PACKAGING-002" "python marker unreadable without tomllib"
assert_lacks "$observed" "GOV-PACKAGING-003" "python lifecycle unreadable without tomllib"

# Every code the validator can emit must be registered in the catalog.
python3 "$root/scripts/audit_diagnostics.py" --root "$root" >/dev/null \
  || fail "diagnostics catalog must cover every emitted code"

echo "agent-hosts.test.sh OK"

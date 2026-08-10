#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-adoption-test.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT INT TERM

standard="$fixture/standard"
target="$fixture/target"
mkdir -p "$standard" "$target"
cp -R "$repo_root/governance" "$repo_root/project" "$repo_root/scripts" "$standard/"
mkdir -p "$standard/template/files"
cp "$repo_root/template/files/AGENTS.template.md" "$standard/template/files/AGENTS.template.md"
cp "$repo_root/project.sh" "$repo_root/project.bat" "$standard/"
cp "$repo_root/VERSION" "$standard/VERSION"
git -C "$standard" init -q
git -C "$standard" config user.email test@new-project.local
git -C "$standard" config user.name new-project-test
git -C "$standard" add .
git -C "$standard" commit -qm 'test: publish standard fixture'
revision="$(git -C "$standard" rev-parse HEAD)"

set +e
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/initial-check.out" 2> "$fixture/initial-check.err"
status=$?
set -e
test "$status" -eq 1
grep -q '^CREATE .governance/manifest.json$' "$fixture/initial-check.out"
grep -q '^CREATE .governance/manifest.lock.json$' "$fixture/initial-check.out"
test -z "$(find "$target" -mindepth 1 -print -quit)"

python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" > "$fixture/adopt.out"
python3 - "$target" "$revision" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
lock = json.load(open(root / '.governance/manifest.lock.json', encoding='utf-8'))
manifest = json.load(open(root / '.governance/manifest.json', encoding='utf-8'))
assert lock['standard']['sourceRevision'] == sys.argv[2]
assert lock['standard']['publicationStatus'] == 'published'
assert lock['standard']['version'] == '0.14.0'
assert '.governance/manifest.base.json' in lock['managedFiles']
assert '.governance/manifest.json' not in lock['managedFiles']
assert (root / '.governance/manifest.base.json').is_file()
governance_paths = manifest['coordination']['workstreams']['governance']['ownedPaths']
assert 'CHANGELOG.md' in governance_paths
assert '.env.example' in governance_paths
for path, expected in lock['managedFiles'].items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected
PY
python3 - "$target/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['coordination']['workstreams']['sdk'] = {
    'ownedPaths': ['sdk/**', 'test/sdk*', 'test/python-runtime.test.ts'],
}
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
PY
test -x "$target/project/governance-check.sh"
test -x "$target/project.sh"
test -f "$target/project.bat"
test -f "$target/AGENTS.md"
test -f "$target/.governance/approval-evidence.schema.json"
test -f "$target/.governance/package-manifest.json"
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/current-check.out"
grep -q '^up-to-date wellmanifest/new-project ' "$fixture/current-check.out"

tampered_manifest="$fixture/tampered-manifest"
cp -R "$target" "$tampered_manifest"
python3 - "$tampered_manifest/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['standard']['id'] = 'target-owned-standard'
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
PY
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$tampered_manifest" --source-revision "$revision" --check \
  > /dev/null 2> "$fixture/tampered-manifest.err"; then
  echo 'expected managed manifest value removal to fail' >&2
  exit 1
fi
grep -q 'violates its installed managed base' "$fixture/tampered-manifest.err"

printf '\n# drift\n' >> "$target/project/governance-check.sh"
set +e
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/drift-check.out" 2> "$fixture/drift-check.err"
status=$?
set -e
test "$status" -eq 1
grep -q '^UPDATE project/governance-check.sh$' "$fixture/drift-check.out"
grep -q '# drift' "$target/project/governance-check.sh"
set +e
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" > /dev/null 2> "$fixture/drift.err"
status=$?
set -e
test "$status" -ne 0
grep -q 'rerun with --upgrade' "$fixture/drift.err"
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --upgrade > /dev/null
! grep -q '# drift' "$target/project/governance-check.sh"

chmod -x "$target/project/governance-check.sh"
set +e
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/mode-check.out"
status=$?
set -e
test "$status" -eq 1
grep -q '^CHMOD project/governance-check.sh$' "$fixture/mode-check.out"
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" > /dev/null
test -x "$target/project/governance-check.sh"

set +e
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision deadbeef > /dev/null 2> "$fixture/revision.err"
status=$?
set -e
test "$status" -eq 2
grep -q 'full lowercase 40-character commit SHA' "$fixture/revision.err"

set +e
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check --upgrade \
  > /dev/null 2> "$fixture/options.err"
status=$?
set -e
test "$status" -eq 2
grep -q -- '--check and --upgrade are mutually exclusive' "$fixture/options.err"

mismatch="$fixture/mismatch"
mkdir -p "$mismatch/.governance"
sed 's/"version": "0.14.0"/"version": "9.9.9"/' \
  "$standard/governance/manifest.default.json" > "$mismatch/.governance/manifest.json"
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$mismatch" --source-revision "$revision" --upgrade \
  > /dev/null 2> "$fixture/mismatch.err"; then
  echo "expected version mismatch to fail" >&2
  exit 1
fi
grep -Eq 'target manifest (version must equal|does not extend the managed base)' "$fixture/mismatch.err"
test ! -e "$mismatch/project/governance-check.sh"
test ! -e "$mismatch/.governance/manifest.lock.json"

missing="$fixture/missing-standard"
cp -R "$standard" "$missing"
python3 - "$missing/governance/package-manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
document = json.load(open(path, encoding='utf-8'))
document['files'].append({
    'source': 'governance/not-published.json',
    'target': '.governance/not-published.json',
    'strategy': 'managed',
    'executable': False,
})
open(path, 'w', encoding='utf-8').write(json.dumps(document, indent=2) + '\n')
PY
git -C "$missing" add governance/package-manifest.json
git -C "$missing" commit -qm 'test: declare missing artifact'
missing_revision="$(git -C "$missing" rev-parse HEAD)"
if python3 "$missing/scripts/create_adoption_lock.py" \
  --target-root "$fixture/missing-target" --source-revision "$missing_revision" \
  > /dev/null 2> "$fixture/missing-artifact.err"; then
  echo 'expected missing package source to be rejected' >&2
  exit 1
fi
grep -q 'package source is missing' "$fixture/missing-artifact.err"

duplicate="$fixture/duplicate-standard"
cp -R "$standard" "$duplicate"
python3 - "$duplicate/governance/package-manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
document = json.load(open(path, encoding='utf-8'))
extra = dict(document['files'][0])
extra['source'] = 'VERSION'
document['files'].append(extra)
open(path, 'w', encoding='utf-8').write(json.dumps(document, indent=2) + '\n')
PY
git -C "$duplicate" add governance/package-manifest.json
git -C "$duplicate" commit -qm 'test: declare duplicate target'
duplicate_revision="$(git -C "$duplicate" rev-parse HEAD)"
if python3 "$duplicate/scripts/create_adoption_lock.py" \
  --target-root "$fixture/duplicate-target" --source-revision "$duplicate_revision" \
  > /dev/null 2> "$fixture/duplicate-artifact.err"; then
  echo 'expected duplicate package target to be rejected' >&2
  exit 1
fi
grep -q 'duplicate package target' "$fixture/duplicate-artifact.err"

unsupported="$fixture/unsupported-extendable"
cp -R "$standard" "$unsupported"
python3 - "$unsupported/governance/package-manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
document = json.load(open(path, encoding='utf-8'))
entry = next(item for item in document['files'] if item['strategy'] == 'extendable')
entry['target'] = 'project.sh'
open(path, 'w', encoding='utf-8').write(json.dumps(document, indent=2) + '\n')
PY
git -C "$unsupported" add governance/package-manifest.json
git -C "$unsupported" commit -qm 'test: declare unsupported extendable target'
unsupported_revision="$(git -C "$unsupported" rev-parse HEAD)"
if python3 "$unsupported/scripts/create_adoption_lock.py" \
  --target-root "$fixture/unsupported-target" --source-revision "$unsupported_revision" \
  > /dev/null 2> "$fixture/unsupported.err"; then
  echo 'expected unsupported extendable target to fail' >&2
  exit 1
fi
grep -q 'extendable strategy currently supports only' "$fixture/unsupported.err"

missing_base="$fixture/missing-extendable-base"
cp -R "$standard" "$missing_base"
python3 - "$missing_base/governance/package-manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
document = json.load(open(path, encoding='utf-8'))
document['files'] = [
    item for item in document['files']
    if item['target'] != '.governance/manifest.base.json'
]
open(path, 'w', encoding='utf-8').write(json.dumps(document, indent=2) + '\n')
PY
git -C "$missing_base" add governance/package-manifest.json
git -C "$missing_base" commit -qm 'test: remove extendable managed base'
missing_base_revision="$(git -C "$missing_base" rev-parse HEAD)"
if python3 "$missing_base/scripts/create_adoption_lock.py" \
  --target-root "$fixture/missing-base-target" --source-revision "$missing_base_revision" \
  > /dev/null 2> "$fixture/missing-base.err"; then
  echo 'expected missing extendable managed base to fail' >&2
  exit 1
fi
grep -q 'requires a managed base from the same source' "$fixture/missing-base.err"

legacy_standard="$fixture/legacy-standard"
legacy_target="$fixture/legacy-target"
legacy_tampered="$fixture/legacy-tampered"
cp -R "$standard" "$legacy_standard"
python3 - "$legacy_standard" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
(root / 'VERSION').write_text('0.11.0\n', encoding='utf-8')
manifest_path = root / 'governance/manifest.default.json'
manifest = json.load(open(manifest_path, encoding='utf-8'))
manifest['standard']['version'] = '0.11.0'
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
package_path = root / 'governance/package-manifest.json'
package = json.load(open(package_path, encoding='utf-8'))
package['files'] = [
    item for item in package['files']
    if item['target'] != '.governance/manifest.base.json'
]
entry = next(
    item for item in package['files']
    if item['target'] == '.governance/manifest.json'
)
entry['strategy'] = 'managed'
package_path.write_text(json.dumps(package, indent=2) + '\n', encoding='utf-8')
PY
git -C "$legacy_standard" add VERSION governance/manifest.default.json governance/package-manifest.json
git -C "$legacy_standard" commit -qm 'test: publish legacy managed manifest'

mkdir -p "$legacy_target/.governance"
python3 - "$legacy_standard" "$legacy_target" <<'PY'
import hashlib
import json
import pathlib
import sys

standard, target = map(pathlib.Path, sys.argv[1:])
manifest = json.load(open(standard / 'governance/manifest.default.json', encoding='utf-8'))
manifest.pop('approvalEvidence')
manifest['coordination']['workstreams']['goal-release'] = {
    'ownedPaths': ['integration/**', 'uv.lock'],
}
content = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
(target / '.governance/manifest.json').write_bytes(content)
lock = {
    'schema': 'new-project.lock/v1',
    'standard': {
        'id': 'wellmanifest/new-project',
        'version': '0.11.0',
        'sourceRepository': 'wellmanifest/new-project',
        # Deliberately unavailable but structurally valid. Integrity comes from
        # the exact managedFiles hash, not a reconstructed pristine default.
        'sourceRevision': '0' * 40,
        'publicationStatus': 'published',
    },
    'managedFiles': {
        '.governance/manifest.json': hashlib.sha256(content).hexdigest(),
    },
}
(target / '.governance/manifest.lock.json').write_text(
    json.dumps(lock, indent=2, sort_keys=True) + '\n', encoding='utf-8'
)
PY
cp -R "$legacy_target" "$legacy_tampered"
printf ' ' >> "$legacy_tampered/.governance/manifest.json"

cp "$standard/VERSION" "$legacy_standard/VERSION"
cp "$standard/governance/manifest.default.json" "$legacy_standard/governance/manifest.default.json"
cp "$standard/governance/package-manifest.json" "$legacy_standard/governance/package-manifest.json"
git -C "$legacy_standard" add VERSION governance/manifest.default.json governance/package-manifest.json
git -C "$legacy_standard" commit -qm 'test: publish extendable migration target'
legacy_upgrade_revision="$(git -C "$legacy_standard" rev-parse HEAD)"

python3 "$legacy_standard/scripts/create_adoption_lock.py" \
  --target-root "$legacy_target" --source-revision "$legacy_upgrade_revision" --upgrade \
  > "$fixture/legacy-upgrade.out"
python3 - "$legacy_target" "$legacy_upgrade_revision" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.load(open(root / '.governance/manifest.json', encoding='utf-8'))
lock = json.load(open(root / '.governance/manifest.lock.json', encoding='utf-8'))
assert 'approvalEvidence' in manifest
assert manifest['coordination']['workstreams']['goal-release']['ownedPaths'] == [
    'integration/**', 'uv.lock'
]
assert (root / '.governance/manifest.base.json').is_file()
assert lock['standard']['sourceRevision'] == sys.argv[2]
assert '.governance/manifest.json' not in lock['managedFiles']
base = root / '.governance/manifest.base.json'
assert lock['managedFiles'][str(base.relative_to(root))] == hashlib.sha256(base.read_bytes()).hexdigest()
PY

if python3 "$legacy_standard/scripts/create_adoption_lock.py" \
  --target-root "$legacy_tampered" --source-revision "$legacy_upgrade_revision" --upgrade \
  > /dev/null 2> "$fixture/legacy-tampered.err"; then
  echo 'expected hash-mismatched legacy manifest to fail closed' >&2
  exit 1
fi
grep -Eq 'target manifest (does not extend|violates)' "$fixture/legacy-tampered.err"
test ! -e "$legacy_tampered/.governance/manifest.base.json"

upgrade_standard="$fixture/upgrade-standard"
cp -R "$standard" "$upgrade_standard"
python3 - "$upgrade_standard/VERSION" "$upgrade_standard/governance/manifest.default.json" <<'PY'
import json
import sys

version_path, manifest_path = sys.argv[1:]
open(version_path, 'w', encoding='utf-8').write('0.14.1\n')
manifest = json.load(open(manifest_path, encoding='utf-8'))
manifest['standard']['version'] = '0.14.1'
manifest['requiredFiles'].append('SECURITY.md')
open(manifest_path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
touch "$upgrade_standard/SECURITY.md"
git -C "$upgrade_standard" add VERSION governance/manifest.default.json SECURITY.md
git -C "$upgrade_standard" commit -qm 'test: publish extendable manifest upgrade'
upgrade_revision="$(git -C "$upgrade_standard" rev-parse HEAD)"
python3 "$upgrade_standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$upgrade_revision" --upgrade \
  > "$fixture/upgrade.out"
python3 - "$target" "$upgrade_revision" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.load(open(root / '.governance/manifest.json', encoding='utf-8'))
base = json.load(open(root / '.governance/manifest.base.json', encoding='utf-8'))
lock = json.load(open(root / '.governance/manifest.lock.json', encoding='utf-8'))
assert manifest['standard']['version'] == '0.14.1'
assert 'SECURITY.md' in manifest['requiredFiles']
assert manifest['coordination']['workstreams']['sdk']['ownedPaths'][-1] == 'test/python-runtime.test.ts'
assert 'coordination' in base and 'workstreams' not in base['coordination']
assert lock['standard']['sourceRevision'] == sys.argv[2]
assert '.governance/manifest.json' not in lock['managedFiles']
expected = hashlib.sha256((root / '.governance/manifest.base.json').read_bytes()).hexdigest()
assert lock['managedFiles']['.governance/manifest.base.json'] == expected
PY
python3 "$upgrade_standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$upgrade_revision" --check \
  > "$fixture/upgraded-check.out"
grep -q '^up-to-date wellmanifest/new-project 0.14.1 ' "$fixture/upgraded-check.out"

python3 - "$repo_root" <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
policy = (root / 'POLICY.md').read_text(encoding='utf-8')
contributing = (root / 'CONTRIBUTING.md').read_text(encoding='utf-8')
hub_agents = (root / 'AGENTS.md').read_text(encoding='utf-8')
target_agents = (root / 'template/files/AGENTS.template.md').read_text(encoding='utf-8')

def rule(document: str, rule_id: str) -> str:
    match = re.search(rf'RULE {rule_id}\b(.*?)(?=\nRULE |\n```)', document, re.S)
    assert match, rule_id
    return match.group(0)

core = rule(policy, 'P-CORE-008')
assert 'SESSION_EXECUTION_AUTHORIZATION' in core
assert 'USER_REQUEST_AUTHORIZES_EXECUTION_OR_AUTONOMOUS_MODE' in core
assert 'REQUIRE_SEPARATE_AUTHORITY' in core
assert 'WAIT_FOR_APPROVAL' not in core
assert 'EXTERNAL_TRUSTED_APPROVAL' in rule(policy, 'P-CORE-015')

approval = rule(contributing, 'C-APPROVAL-002')
assert 'USER_REQUEST_AUTHORIZES_EXECUTION_OR_AUTONOMOUS_MODE' in approval
assert 'SEPARATE_CONFIRMATION_NOT_REQUIRED' in approval
assert 'TRUSTED_MERGE_APPROVAL' in approval
assert 'MATERIAL_OBJECTIVE_EXPANSION' in rule(contributing, 'C-APPROVAL-003')

for agents in (hub_agents, target_agents):
    assert 'SESSION_EXECUTION_AUTHORIZATION' in agents
    assert 'without a second confirmation' in agents
    assert 'trusted merge approval' in agents.lower()
assert 'STOP & WAIT FOR USER REVIEW' not in hub_agents
assert 'Stop in `WAIT_FOR_APPROVAL`' not in target_agents
PY

echo 'adoption lock: PASS'

#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-adoption-test.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT INT TERM

# The recovered worktree bootstrap template has traceable source commits and
# must fail-close into the repository installer before a test suite starts.
python3 - "$repo_root/template/files/tests/conftest-worktree-bootstrap.template.py" \
  "$fixture/bootstrap" <<'PY'
import importlib.util
import pathlib
import sys
import types

source, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
text = source.read_text(encoding='utf-8')
assert 'autogrammar/hillm' in text
assert '305361a' in text and 'b8a9f8a' in text
# Loading a conftest template to test its bootstrap helper must not require the
# CI host itself to have pytest installed. The adopted repository supplies the
# real module when pytest discovers conftest.py.
sys.modules['pytest'] = types.SimpleNamespace(
    fixture=lambda **_kwargs: lambda function: function,
)
spec = importlib.util.spec_from_file_location('worktree_bootstrap_template', source)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
module.ROOT = root
module.VENV_BIN = root / '.venv' / 'bin'
module.REQUIRED_CLIS = ('fixture-cli',)
calls = []

def run(arguments, *, cwd, check):
    assert cwd == root and check is True
    calls.append(arguments)
    module.VENV_BIN.mkdir(parents=True, exist_ok=True)
    if arguments == ['bash', 'packages/install-dev.sh']:
        (module.VENV_BIN / 'fixture-cli').write_text('', encoding='utf-8')

module.subprocess.run = run
module._ensure_dev_install()
assert calls[0][1:3] == ['-m', 'venv']
assert calls[1] == ['bash', 'packages/install-dev.sh']
calls.clear()
module._ensure_dev_install()
assert calls == []
PY

standard="$fixture/standard"
target="$fixture/target"
mkdir -p "$standard" "$target"
cp -R "$repo_root/governance" "$repo_root/project" "$repo_root/scripts" "$standard/"
cp -R "$repo_root/error" "$standard/"
# Copy every source the package manifest names, instead of a hand-written list
# that silently falls behind whenever the package gains a file. ticket-107 added
# four host sources and this fixture would have kept passing while adoption of
# them was broken.
python3 - "$repo_root" "$standard" <<'PY'
import json
import shutil
import sys
from pathlib import Path

repo_root, standard = Path(sys.argv[1]), Path(sys.argv[2])
manifest = json.loads((repo_root / "governance/package-manifest.json").read_text())
for item in manifest["files"]:
    source = repo_root / item["source"]
    destination = standard / item["source"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
PY
cp "$repo_root/VERSION" "$standard/VERSION"
# The package ships the guard config from the repository root, so the fixture
# that stands in for a published standard has to carry it too.
cp "$repo_root/worktree-guard.yaml" "$standard/worktree-guard.yaml"
git -C "$standard" init -q
git -C "$standard" config user.email test@new-project.local
git -C "$standard" config user.name new-project-test
git -C "$standard" add .
git -C "$standard" commit -qm 'test: publish standard fixture'
revision="$(git -C "$standard" rev-parse HEAD)"

candidate_adopt() {
  local standard_root="$1"
  shift
  python3 "$standard_root/scripts/create_adoption_lock.py" \
    --allow-unpublished-for-testing "$@"
}

ignored_target="$fixture/ignored-target"
mkdir -p "$ignored_target"
git -C "$ignored_target" init -q
printf '%s\n' '.github/' > "$ignored_target/.gitignore"
before_ignored="$(find "$ignored_target" -mindepth 1 -not -path '*/.git/*' -printf '%P\n' | sort)"
if candidate_adopt "$standard" \
  --target-root "$ignored_target" --source-revision "$revision" \
  > "$fixture/ignored.out" 2> "$fixture/ignored.err"; then
  echo 'expected ignored managed adoption targets to fail closed' >&2
  exit 1
fi
grep -Fq 'managed adoption targets are ignored by target Git rules' "$fixture/ignored.err"
grep -Fq '.github/copilot-instructions.md' "$fixture/ignored.err"
grep -Fq '.github/workflows/new-project-governance.yml' "$fixture/ignored.err"
after_ignored="$(find "$ignored_target" -mindepth 1 -not -path '*/.git/*' -printf '%P\n' | sort)"
test "$after_ignored" = "$before_ignored"

unpublished_target="$fixture/unpublished-target"
mkdir -p "$unpublished_target"
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$unpublished_target" --source-revision "$revision" --check \
  > "$fixture/unpublished.out" 2> "$fixture/unpublished.err"; then
  echo 'expected production adoption of an unpublished fixture to fail' >&2
  exit 1
fi
grep -Eq 'has no published release tag|does not identify requested revision' \
  "$fixture/unpublished.err"
test -z "$(find "$unpublished_target" -mindepth 1 -print -quit)"

collision_target="$fixture/collision-target"
mkdir -p "$collision_target"
printf '%s\n' '#!/usr/bin/env bash' 'echo target automation' > "$collision_target/project.sh"
printf '%s\r\n' '@echo off' 'echo target automation' > "$collision_target/project.bat"
chmod 740 "$collision_target/project.sh"
collision_sh_hash="$(sha256sum "$collision_target/project.sh" | cut -d' ' -f1)"
collision_bat_hash="$(sha256sum "$collision_target/project.bat" | cut -d' ' -f1)"
collision_sh_mode="$(stat -c '%a' "$collision_target/project.sh")"
if candidate_adopt "$standard" \
  --target-root "$collision_target" --source-revision "$revision" --check \
  > "$fixture/collision-check.out" 2> "$fixture/collision-check.err"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
! grep -Eq '^(UPDATE|CHMOD) project\.sh$' "$fixture/collision-check.out"
! grep -Eq '^(UPDATE|CHMOD) project\.bat$' "$fixture/collision-check.out"
candidate_adopt "$standard" \
  --target-root "$collision_target" --source-revision "$revision" \
  > "$fixture/collision-adopt.out"
test "$(sha256sum "$collision_target/project.sh" | cut -d' ' -f1)" = "$collision_sh_hash"
test "$(sha256sum "$collision_target/project.bat" | cut -d' ' -f1)" = "$collision_bat_hash"
test "$(stat -c '%a' "$collision_target/project.sh")" = "$collision_sh_mode"
python3 - "$collision_target/.governance/manifest.lock.json" <<'PY'
import json
import sys

managed = json.load(open(sys.argv[1], encoding='utf-8'))['managedFiles']
assert 'project.sh' not in managed
assert 'project.bat' not in managed
assert 'project/governance-check.sh' in managed
assert 'project/governance-check.bat' in managed
PY
candidate_adopt "$standard" \
  --target-root "$collision_target" --source-revision "$revision" --check \
  > "$fixture/collision-current.out"
grep -q '^up-to-date wellmanifest/new-project ' "$fixture/collision-current.out"

if candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/initial-check.out" 2> "$fixture/initial-check.err"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^CREATE .governance/manifest.json$' "$fixture/initial-check.out"
grep -q '^CREATE .governance/manifest.lock.json$' "$fixture/initial-check.out"
grep -q '^MISSING target prerequisite CHANGELOG.md$' "$fixture/initial-check.out"
grep -q '^MISSING target prerequisite README.md$' "$fixture/initial-check.out"
grep -q '^MISSING target prerequisite TODO.md$' "$fixture/initial-check.out"
grep -q '^MISSING target prerequisite VERSION$' "$fixture/initial-check.out"
grep -q '^MISSING target prerequisite project/TICKETS.md$' "$fixture/initial-check.out"
expected_missing="$(printf '%s\n' \
  'MISSING target prerequisite CHANGELOG.md' \
  'MISSING target prerequisite README.md' \
  'MISSING target prerequisite TODO.md' \
  'MISSING target prerequisite VERSION' \
  'MISSING target prerequisite project/TICKETS.md')"
test "$(grep '^MISSING target prerequisite ' "$fixture/initial-check.out")" = "$expected_missing"
! grep -q '^MISSING target prerequisite AGENTS.md$' "$fixture/initial-check.out"
! grep -q '^MISSING target prerequisite project/new-ticket.sh$' "$fixture/initial-check.out"
! grep -q '^MISSING target prerequisite project/readme.sh$' "$fixture/initial-check.out"
test -z "$(find "$target" -mindepth 1 -print -quit)"

# A real target repository supplies the identity used by the derived check
# declaration. Keep the preceding empty-directory assertion independent from
# Git's administrative files.
git -C "$target" init -q
git -C "$target" remote add origin git@github.com:wellmanifest/adoption-fixture.git

candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" > "$fixture/adopt.out"
grep -q '^adopted wellmanifest/new-project ' "$fixture/adopt.out"
grep -q '^MISSING target prerequisite TODO.md$' "$fixture/adopt.out"
test ! -e "$target/TODO.md"
test ! -e "$target/project/TICKETS.md"
python3 - "$target" "$revision" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
lock = json.load(open(root / '.governance/manifest.lock.json', encoding='utf-8'))
manifest = json.load(open(root / '.governance/manifest.json', encoding='utf-8'))
base = json.load(open(root / '.governance/manifest.base.json', encoding='utf-8'))
assert lock['standard']['sourceRevision'] == sys.argv[2]
assert lock['standard']['publicationStatus'] == 'unpublished-test'
assert lock['standard']['version'] == '0.20.4'
assert '.governance/manifest.base.json' in lock['managedFiles']
assert '.governance/adoption-bindings.json' in lock['managedFiles']
assert '.governance/adoption-bindings.schema.json' in lock['managedFiles']
assert '.governance/work-continuity.schema.json' in lock['managedFiles']
assert '.governance/work_continuity.py' in lock['managedFiles']
assert '.governance/error/GOV-WORK-CONTINUITY.md' in lock['managedFiles']
assert '.subactor/.gitignore' in lock['managedFiles']
assert '.subactor/manifest.json' in lock['managedFiles']
assert '.governance/templates/conftest-worktree-bootstrap.py' in lock['managedFiles']
assert (root / '.subactor/manifest.json').is_file()
assert (root / '.subactor/.gitignore').is_file()
assert (root / '.governance/templates/conftest-worktree-bootstrap.py').is_file()
assert '.governance/manifest.json' not in lock['managedFiles']
assert 'project.sh' not in lock['managedFiles']
assert 'project.bat' not in lock['managedFiles']
assert 'project/governance-check.sh' in lock['managedFiles']
assert 'project/governance-check.bat' in lock['managedFiles']
assert (root / '.governance/manifest.base.json').is_file()
assert manifest['docker']['required'] is False
assert 'required' not in base['docker']
assert manifest['ticket']['requiredFiles'] == ['README.md', 'intent.json']
assert manifest['ticket']['requiredAgentFiles'] == []
integration = manifest['coordination']['workstreams']['integration']['ownedPaths']
required_for_integration = manifest['coordination']['integration']['requiredForPaths']
for path in (
    '.governance/manifest.base.json',
    '.governance/manifest.json',
    '.governance/manifest.lock.json',
    '.governance/package-manifest.json',
    '.governance/required-checks.json',
    '.governance/ticket-allocation.json',
    '.subactor/manifest.json',
    'AGENTS.md',
):
    assert path in integration
    assert path in required_for_integration
governance_paths = manifest['coordination']['workstreams']['governance']['ownedPaths']
assert 'CHANGELOG.md' in governance_paths
assert '.env.example' in governance_paths
catalog = json.load(open(root / '.governance/diagnostics.json', encoding='utf-8'))
for entry in catalog['codes'].values():
    documentation = entry['documentation']
    if documentation is not None:
        assert (root / '.governance' / documentation).is_file(), documentation
for path, expected in lock['managedFiles'].items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected
checks = json.load(open(root / '.governance/required-checks.json', encoding='utf-8'))
assert checks['repository'] == 'wellmanifest/adoption-fixture'
assert sorted(check['name'] for check in checks['requiredChecks']) == [
    'governance / enforce', 'governance / remote lifecycle'
]
PY
python3 "$target/.governance/check_required_checks.py" --root "$target"
touch "$target/README.md" "$target/VERSION" "$target/CHANGELOG.md" "$target/TODO.md" \
  "$target/project/TICKETS.md"
python3 - "$target/.governance/manifest.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['coordination']['workstreams']['sdk'] = {
    'ownedPaths': ['sdk/**', 'test/sdk*', 'test/python-runtime.test.ts'],
}
manifest['requiredFiles'].append('Dockerfile')
manifest['docker']['required'] = True
manifest['stacks'].append('docker')
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
PY
test -x "$target/project/governance-check.sh"
test -x "$target/project.sh"
test -x "$target/.governance/check_required_checks.py"
test -x "$target/.governance/decision_record.py"
test -x "$target/.governance/remediation_intent.py"
test -x "$target/.governance/work_continuity.py"
test -x "$target/.governance/governance_check.py"
test -f "$target/project.bat"
test -f "$target/AGENTS.md"
test -f "$target/.governance/approval-evidence.schema.json"
test -f "$target/.governance/remediation-intent.schema.json"
test -f "$target/.governance/remediation-intent.template.dsl.json"
test -f "$target/.governance/work-continuity.schema.json"
test -f "$target/.governance/error/GOV-REMEDIATION-INTENT.md"
test -f "$target/.governance/error/GOV-WORK-CONTINUITY.md"
test -f "$target/.governance/package-manifest.json"
printf '%s\n' '# target-owned seed extension' >> "$target/project.sh"
printf '%s\r\n' 'REM target-owned seed extension' >> "$target/project.bat"
candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/current-check.out"
grep -q '^up-to-date wellmanifest/new-project ' "$fixture/current-check.out"
grep -q '^MISSING target prerequisite Dockerfile$' "$fixture/current-check.out"
touch "$target/Dockerfile"
candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/ready-check.out"
grep -q '^up-to-date wellmanifest/new-project ' "$fixture/ready-check.out"
! grep -q '^MISSING target prerequisite ' "$fixture/ready-check.out"
python3 - "$target/.governance/manifest.json" "$target/.governance/manifest.base.json" <<'PY'
import json
import sys

manifest = json.load(open(sys.argv[1], encoding='utf-8'))
base = json.load(open(sys.argv[2], encoding='utf-8'))
assert 'Dockerfile' in manifest['requiredFiles']
assert manifest['docker']['required'] is True
assert 'docker' in manifest['stacks']
assert 'required' not in base['docker']
PY

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
if candidate_adopt "$standard" \
  --target-root "$tampered_manifest" --source-revision "$revision" --check \
  > /dev/null 2> "$fixture/tampered-manifest.err"; then
  echo 'expected managed manifest value removal to fail' >&2
  exit 1
fi
grep -q 'violates its installed managed base' "$fixture/tampered-manifest.err"

printf '\n# drift\n' >> "$target/project/governance-check.sh"
if candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/drift-check.out" 2> "$fixture/drift-check.err"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^UPDATE project/governance-check.sh$' "$fixture/drift-check.out"
grep -q '# drift' "$target/project/governance-check.sh"
if candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" > /dev/null 2> "$fixture/drift.err"; then
  status=0
else
  status=$?
fi
test "$status" -ne 0
grep -q 'rerun with --upgrade' "$fixture/drift.err"
candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --upgrade > /dev/null
! grep -q '# drift' "$target/project/governance-check.sh"
grep -q 'target-owned seed extension' "$target/project.sh"
grep -q 'target-owned seed extension' "$target/project.bat"
python3 - "$target/.governance/manifest.json" <<'PY'
import json
import sys

manifest = json.load(open(sys.argv[1], encoding='utf-8'))
assert 'Dockerfile' in manifest['requiredFiles']
assert manifest['docker']['required'] is True
assert 'docker' in manifest['stacks']
PY

chmod -x "$target/project/governance-check.sh"
if candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/mode-check.out"; then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^CHMOD project/governance-check.sh$' "$fixture/mode-check.out"
candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" > /dev/null
test -x "$target/project/governance-check.sh"

if candidate_adopt "$standard" \
  --target-root "$target" --source-revision deadbeef > /dev/null 2> "$fixture/revision.err"; then
  status=0
else
  status=$?
fi
test "$status" -eq 2
grep -q 'full lowercase 40-character commit SHA' "$fixture/revision.err"

if candidate_adopt "$standard" \
  --target-root "$target" --source-revision "$revision" --check --upgrade \
  > /dev/null 2> "$fixture/options.err"; then
  status=0
else
  status=$?
fi
test "$status" -eq 2
grep -q -- '--check and --upgrade are mutually exclusive' "$fixture/options.err"

mismatch="$fixture/mismatch"
mkdir -p "$mismatch/.governance"
sed 's/"version": "0.20.4"/"version": "9.9.9"/' \
  "$standard/governance/manifest.default.json" > "$mismatch/.governance/manifest.json"
if candidate_adopt "$standard" \
  --target-root "$mismatch" --source-revision "$revision" --upgrade \
  > /dev/null 2> "$fixture/mismatch.err"; then
  echo "expected version mismatch to fail" >&2
  exit 1
fi
grep -Eq 'target manifest (version must equal|does not extend the managed base)' "$fixture/mismatch.err"
test ! -e "$mismatch/project/governance-check.sh"
test ! -e "$mismatch/.governance/manifest.lock.json"

invalid_required="$fixture/invalid-required-standard"
cp -R "$standard" "$invalid_required"
python3 - "$invalid_required/governance/manifest.default.json" <<'PY'
import json
import sys

path = sys.argv[1]
manifest = json.load(open(path, encoding='utf-8'))
manifest['requiredFiles'].append('../outside')
open(path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
git -C "$invalid_required" add governance/manifest.default.json
git -C "$invalid_required" commit -qm 'test: publish invalid required path'
invalid_required_revision="$(git -C "$invalid_required" rev-parse HEAD)"
if candidate_adopt "$invalid_required" \
  --target-root "$fixture/invalid-required-target" \
  --source-revision "$invalid_required_revision" --check \
  > /dev/null 2> "$fixture/invalid-required.err"; then
  echo 'expected invalid required path to fail' >&2
  exit 1
fi
grep -q 'requiredFiles item .* must be repository-relative' "$fixture/invalid-required.err"

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
if candidate_adopt "$missing" \
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
if candidate_adopt "$duplicate" \
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
if candidate_adopt "$unsupported" \
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
if candidate_adopt "$missing_base" \
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

candidate_adopt "$legacy_standard" \
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

if candidate_adopt "$legacy_standard" \
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
open(version_path, 'w', encoding='utf-8').write('0.15.1\n')
manifest = json.load(open(manifest_path, encoding='utf-8'))
manifest['standard']['version'] = '0.15.1'
manifest['requiredFiles'].append('SECURITY.md')
open(manifest_path, 'w', encoding='utf-8').write(json.dumps(manifest, indent=2) + '\n')
PY
touch "$upgrade_standard/SECURITY.md"
git -C "$upgrade_standard" add VERSION governance/manifest.default.json SECURITY.md
git -C "$upgrade_standard" commit -qm 'test: publish extendable manifest upgrade'
upgrade_revision="$(git -C "$upgrade_standard" rev-parse HEAD)"
candidate_adopt "$upgrade_standard" \
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
assert manifest['standard']['version'] == '0.15.1'
assert 'SECURITY.md' in manifest['requiredFiles']
assert manifest['coordination']['workstreams']['sdk']['ownedPaths'][-1] == 'test/python-runtime.test.ts'
assert 'coordination' in base and 'workstreams' not in base['coordination']
assert lock['standard']['sourceRevision'] == sys.argv[2]
assert '.governance/manifest.json' not in lock['managedFiles']
expected = hashlib.sha256((root / '.governance/manifest.base.json').read_bytes()).hexdigest()
assert lock['managedFiles']['.governance/manifest.base.json'] == expected
PY
candidate_adopt "$upgrade_standard" \
  --target-root "$target" --source-revision "$upgrade_revision" --check \
  > "$fixture/upgraded-check.out"
grep -q '^up-to-date wellmanifest/new-project 0.15.1 ' "$fixture/upgraded-check.out"
grep -q '^MISSING target prerequisite SECURITY.md$' "$fixture/upgraded-check.out"

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
assert 'DECLARED_PROTECTED_DELIVERY_PROCESS_INVOCATION' in core
assert 'PROTECTED_EXACT_HEAD_EVIDENCE_AUTHORIZES_MERGE' in core
assert 'WAIT_FOR_APPROVAL' not in core
merge = rule(policy, 'P-CORE-015')
assert 'EXTERNAL_TRUSTED_APPROVAL' in merge
assert 'PROTECTED_DELIVERY_PROCESS_OWNED_MERGE' in merge
assert 'DIRECT_AGENT_MERGE' in merge

approval = rule(contributing, 'C-APPROVAL-002')
assert 'USER_REQUEST_AUTHORIZES_EXECUTION_OR_AUTONOMOUS_MODE' in approval
assert 'SEPARATE_CONFIRMATION_NOT_REQUIRED' in approval
assert 'TRUSTED_MERGE_APPROVAL' in approval
assert 'PROTECTED_DELIVERY_PROCESS_INVOCATION' in approval
assert 'SEPARATE_CHAT_CONFIRMATION' in approval
assert 'MATERIAL_OBJECTIVE_EXPANSION' in rule(contributing, 'C-APPROVAL-003')

for agents in (hub_agents, target_agents):
    assert 'SESSION_EXECUTION_AUTHORIZATION' in agents
    assert 'without a second confirmation' in agents
    assert 'new-project.work-continuity/v2' in agents
    assert 'conversation memory' in agents.lower()
assert 'protected delivery' in target_agents.lower()
assert 'session prose is never' in target_agents.lower()
assert 'agent must not merge directly' in target_agents.lower()
for agents in (hub_agents, target_agents):
    assert 'material objective expansion and trusted merge' not in agents.lower()
assert 'STOP & WAIT FOR USER REVIEW' not in hub_agents
assert 'Stop in `WAIT_FOR_APPROVAL`' not in target_agents
PY

echo 'adoption lock: PASS'

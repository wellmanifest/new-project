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

if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/initial-check.out" 2> "$fixture/initial-check.err"
then
  status=0
else
  status=$?
fi
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
assert lock['standard']['sourceRevision'] == sys.argv[2]
assert lock['standard']['publicationStatus'] == 'published'
assert lock['standard']['version'] == '0.11.0'
for path, expected in lock['managedFiles'].items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected
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

printf '\n# drift\n' >> "$target/project/governance-check.sh"
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/drift-check.out" 2> "$fixture/drift-check.err"
then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^UPDATE project/governance-check.sh$' "$fixture/drift-check.out"
grep -q '# drift' "$target/project/governance-check.sh"
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" > /dev/null 2> "$fixture/drift.err"
then
  status=0
else
  status=$?
fi
test "$status" -ne 0
grep -q 'rerun with --upgrade' "$fixture/drift.err"
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --upgrade > /dev/null
! grep -q '# drift' "$target/project/governance-check.sh"

chmod -x "$target/project/governance-check.sh"
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check \
  > "$fixture/mode-check.out"
then
  status=0
else
  status=$?
fi
test "$status" -eq 1
grep -q '^CHMOD project/governance-check.sh$' "$fixture/mode-check.out"
python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" > /dev/null
test -x "$target/project/governance-check.sh"

if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision deadbeef > /dev/null 2> "$fixture/revision.err"
then
  status=0
else
  status=$?
fi
test "$status" -eq 2
grep -q 'full lowercase 40-character commit SHA' "$fixture/revision.err"

if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$target" --source-revision "$revision" --check --upgrade \
  > /dev/null 2> "$fixture/options.err"
then
  status=0
else
  status=$?
fi
test "$status" -eq 2
grep -q -- '--check and --upgrade are mutually exclusive' "$fixture/options.err"

mismatch="$fixture/mismatch"
mkdir -p "$mismatch/.governance"
sed 's/"version": "0.11.0"/"version": "9.9.9"/' \
  "$standard/governance/manifest.default.json" > "$mismatch/.governance/manifest.json"
if python3 "$standard/scripts/create_adoption_lock.py" \
  --target-root "$mismatch" --source-revision "$revision" --upgrade \
  > /dev/null 2> "$fixture/mismatch.err"; then
  echo "expected version mismatch to fail" >&2
  exit 1
fi
grep -q 'target manifest version must equal' "$fixture/mismatch.err"
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

echo 'adoption lock: PASS'

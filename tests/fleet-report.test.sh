#!/usr/bin/env bash
# ticket-114: the fleet report reads only committed adoption evidence.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT/scripts/fleet_report.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$REPORT" ]] || fail "scripts/fleet_report.py must exist"

workspace="$TMP/workspace"
mkdir -p "$workspace/new-project"
git init -q "$workspace/new-project"
git -C "$workspace/new-project" config user.email test@new-project.local
git -C "$workspace/new-project" config user.name new-project-test
printf '%s\n' "0.2.0" > "$workspace/new-project/VERSION"
git -C "$workspace/new-project" add VERSION
git -C "$workspace/new-project" commit -qm "seed"
git -C "$workspace/new-project" tag -a v0.1.0 -m "0.1.0"
git -C "$workspace/new-project" tag -a v0.2.0 -m "0.2.0"

adopter() {
  local name="$1" version="$2"
  mkdir -p "$workspace/$name/.governance"
  git init -q "$workspace/$name"
  git -C "$workspace/$name" remote add origin "git@github.com:wellmanifest/$name.git"
  cat > "$workspace/$name/.governance/manifest.lock.json" <<JSON
{
  "schema": "new-project.lock/v1",
  "standard": {
    "id": "wellmanifest/new-project",
    "publicationStatus": "published",
    "sourceRepository": "wellmanifest/new-project",
    "sourceRevision": "1111111111111111111111111111111111111111",
    "version": "$version"
  },
  "managedFiles": {"AGENTS.md": "$(printf 'contract\n' | sha256sum | cut -d' ' -f1)"}
}
JSON
  printf 'contract\n' > "$workspace/$name/AGENTS.md"
}

adopter current 0.2.0
adopter stale 0.1.0

# A repository that follows the standard on paper but pins nothing is the most
# dangerous state, because it looks compliant.
mkdir -p "$workspace/claimed"
git init -q "$workspace/claimed"
printf 'contract\n' > "$workspace/claimed/AGENTS.md"

observed="$(python3 "$REPORT" --workspace "$workspace" --validator-registry /nonexistent --format json)"
python3 - "$observed" <<'PY'
import json, sys
report = json.loads(sys.argv[1])
assert report["currentStandard"] == "0.2.0", report["currentStandard"]
by_name = {row["repository"]: row for row in report["adopters"]}
assert set(by_name) == {"current", "stale"}, sorted(by_name)
assert by_name["current"]["releasesBehind"] == 0, by_name["current"]
assert by_name["stale"]["releasesBehind"] == 1, by_name["stale"]
assert by_name["current"]["digestDrift"] == [], by_name["current"]
assert report["claimed"] == ["claimed"], report["claimed"]
assert by_name["stale"]["checksVsValidator"] == "unregistered"
PY

# Editing a managed file must show as drift against the lock.
printf 'tampered\n' > "$workspace/current/AGENTS.md"
observed="$(python3 "$REPORT" --workspace "$workspace" --validator-registry /nonexistent --format json)"
python3 - "$observed" <<'PY'
import json, sys
row = {r["repository"]: r for r in json.loads(sys.argv[1])["adopters"]}["current"]
assert row["digestDrift"] == ["AGENTS.md:DRIFT"], row["digestDrift"]
PY

# The threshold turns the report into a gate.
python3 "$REPORT" --workspace "$workspace" --validator-registry /nonexistent \
  --max-releases-behind 1 > /dev/null || fail "threshold 1 must pass"
if python3 "$REPORT" --workspace "$workspace" --validator-registry /nonexistent \
  --max-releases-behind 0 > /dev/null; then
  fail "threshold 0 must fail while an adopter is a release behind"
fi

echo "fleet-report tests: PASS"

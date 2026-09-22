#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$root/scripts/standard_pack_check.py"
catalog="governance/standard-packs.json"
adoption="governance/standard-adoption.default.json"

python3 "$checker" --root "$root" --catalog "$catalog" --adoption "$adoption" --format json >/dev/null
strict_report="$(mktemp)"
trap ':' EXIT
if python3 "$checker" --root "$root" --catalog "$catalog" --adoption "$adoption" --strict --format json >"$strict_report"; then
  echo "strict standard-pack check unexpectedly accepted audit findings" >&2
  exit 1
fi
grep -q 'GOV-STANDARD-PACK-001' "$strict_report"

echo "standard-pack-check.test.sh OK"

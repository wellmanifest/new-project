#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runtime="$repo_root/scripts/governance_env.py"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

cat >"$work/CONTRIBUTING.md" <<'EOF'
```dsl
ENV_FILE ".env" OPTIONAL
VARIABLE DEFAULT_AGENT TYPE STRING FROM ENV DEFAULT "fallback"
VARIABLE ENABLED TYPE BOOLEAN FROM ENV DEFAULT "false"
SECRET SENSITIVE_INPUT TYPE STRING FROM ENV REQUIRED REDACT
```
EOF
cat >"$work/.env" <<'EOF'
DEFAULT_AGENT="dotenv-agent"
ENABLED=yes
SENSITIVE_INPUT="never-print-this"
IGNORED_VALUE="must-not-be-exported"
EOF

python3 "$runtime" --contract "$work/CONTRIBUTING.md" check >"$work/report.json"
python3 - "$work/report.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["status"] == "resolved"
assert report["variables"]["DEFAULT_AGENT"]["value"] == "dotenv-agent"
assert report["variables"]["ENABLED"]["value"] == "true"
assert report["variables"]["SENSITIVE_INPUT"]["value"] == "[REDACTED]"
assert "never-print-this" not in json.dumps(report)
assert "IGNORED_VALUE" not in report["variables"]
PY

DEFAULT_AGENT="process-agent" python3 "$runtime" --contract "$work/CONTRIBUTING.md" run -- \
  python3 -c 'import os; print(os.environ["DEFAULT_AGENT"], os.environ["ENABLED"], "IGNORED_VALUE" in os.environ)' \
  >"$work/child.txt"
grep -Fxq 'process-agent true False' "$work/child.txt"

mkdir "$work/missing"
cat >"$work/missing/CONTRIBUTING.md" <<'EOF'
ENV_FILE ".env" OPTIONAL
SECRET REQUIRED_TOKEN TYPE STRING FROM ENV REQUIRED REDACT
EOF
if env -u REQUIRED_TOKEN python3 "$runtime" --contract "$work/missing/CONTRIBUTING.md" check \
  >"$work/missing.out" 2>"$work/missing.err"; then
  echo "expected unresolved required variable to fail" >&2
  exit 1
fi
grep -Fq 'GOV-ENV-001: required variable REQUIRED_TOKEN is unresolved' "$work/missing.err"

mkdir "$work/escape"
cat >"$work/escape/CONTRIBUTING.md" <<'EOF'
ENV_FILE "../.env" OPTIONAL
VARIABLE VALUE TYPE STRING FROM ENV DEFAULT "safe"
EOF
if python3 "$runtime" --contract "$work/escape/CONTRIBUTING.md" check \
  >"$work/escape.out" 2>"$work/escape.err"; then
  echo "expected escaping ENV_FILE to fail" >&2
  exit 1
fi
grep -Fq 'GOV-ENV-001: ENV_FILE escapes the contract directory' "$work/escape.err"

python3 "$runtime" --contract "$repo_root/CONTRIBUTING.md" check >"$work/repository-report.json"
grep -Fq '"DEFAULT_AGENT"' "$work/repository-report.json"

echo "governance environment runtime tests passed"

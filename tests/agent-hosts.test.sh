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
grep -Fq 'new-ticket.sh' "$root/GEMINI.md" || fail "GEMINI.md must require new-ticket.sh"
grep -Fq 'new-ticket.sh' "$root/CLAUDE.md" || fail "CLAUDE.md must require new-ticket.sh"
grep -Fq 'alwaysApply: true' "$root/.cursor/rules/new-project-standard.mdc" || fail "Cursor rule must alwaysApply"

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
[[ "$(git -C "$tmp/adopter" config --get core.hooksPath)" == ".githooks" ]] || fail "installer must set core.hooksPath"

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
git -C "$tmp/adopter" commit -qm "bound to ticket-001" || fail "IN_PROGRESS ticket branch must commit"

user_home="$tmp/home"
mkdir -p "$user_home"
HOME="$user_home" "$root/scripts/install-agent-hosts.sh" --source "$root" --user
[[ -f "$user_home/.cursor/rules/new-project-standard.mdc" ]] || fail "--user must install Cursor rule"
grep -Fq 'wellmanifest/new-project host contract' "$user_home/.gemini/GEMINI.md" || fail "--user must install Gemini pointer"
grep -Fq 'wellmanifest/new-project host contract' "$user_home/.claude/CLAUDE.md" || fail "--user must install Claude pointer"

echo "agent-hosts.test.sh OK"

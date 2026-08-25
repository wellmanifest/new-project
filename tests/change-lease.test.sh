#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/change_lease_check.py"
fixture="$(mktemp -d "${TMPDIR:-/tmp}/new-project-change-lease.XXXXXX")"
trap 'rm -rf "$fixture"' EXIT INT TERM
cat > "$fixture/lease.json" <<'JSON'
{"schema":"wellmanifest.change-lease/v1","leaseId":"lease-1","repositoryRef":"example/repo","targetBranch":"main","ticketId":"ticket-123","workstream":"governance","scopeHash":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","branchRef":"ticket/123-change-lease","worktreeId":"wt-1","ownerActor":"coding-agent","ownerSession":"session-1","phase":"validating","leaseRevision":3,"fencingToken":9,"issuedAt":"2026-08-25T18:00:00Z","expiresAt":"2026-08-25T19:00:00Z","heartbeatAt":"2026-08-25T18:10:00Z","headSha":null,"pullRequest":14,"validatorRunId":null,"publicationFrozen":false,"planHash":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","previousReceiptRef":null,"eventSequence":3}
JSON
python3 "$checker" validate "$fixture/lease.json" | grep -q GOV-CHANGE-LEASE-PASS
cat > "$fixture/freeze.json" <<'JSON'
{"schema":"wellmanifest.change-lease-transition/v1","requestId":"request-freeze","leaseId":"lease-1","action":"freeze-publication","expectedRevision":3,"expectedFencingToken":9,"expectedPhase":"validating","requestedBy":"coding-agent","idempotencyKey":"lease-1-freeze-3","targetHeadSha":"cccccccccccccccccccccccccccccccccccccccc","replacementReceiptRef":null,"authorityRef":"control://repository-change-controller","requestedAt":"2026-08-25T18:11:00Z"}
JSON
python3 "$checker" transition --lease "$fixture/lease.json" --request "$fixture/freeze.json" > "$fixture/freeze-receipt.json"
python3 - "$fixture/freeze-receipt.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
assert r["outcome"] == "accepted" and r["leaseRevision"] == 4 and r["fencingToken"] == 10
assert r["phaseAfter"] == "publication_frozen" and r["headSha"] == "c" * 40
PY
python3 - "$fixture/lease.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
d.update(phase="publication_frozen", leaseRevision=4, fencingToken=10, publicationFrozen=True, headSha="c" * 40)
open(p, "w", encoding="utf-8").write(json.dumps(d))
PY
cat > "$fixture/stale.json" <<'JSON'
{"schema":"wellmanifest.change-lease-transition/v1","requestId":"request-stale","leaseId":"lease-1","action":"dispatch-validation","expectedRevision":3,"expectedFencingToken":9,"expectedPhase":"publication_frozen","requestedBy":"validator-agent","idempotencyKey":"lease-1-dispatch-3","targetHeadSha":"cccccccccccccccccccccccccccccccccccccccc","replacementReceiptRef":null,"authorityRef":"control://repository-change-controller","requestedAt":"2026-08-25T18:12:00Z"}
JSON
if python3 "$checker" transition --lease "$fixture/lease.json" --request "$fixture/stale.json" > "$fixture/stale-receipt.json"; then exit 1; fi
grep -q GOV-CHANGE-LEASE-002 "$fixture/stale-receipt.json"
cat > "$fixture/mutate.json" <<'JSON'
{"schema":"wellmanifest.change-lease-transition/v1","requestId":"request-mutate","leaseId":"lease-1","action":"dispatch-validation","expectedRevision":4,"expectedFencingToken":10,"expectedPhase":"publication_frozen","requestedBy":"validator-agent","idempotencyKey":"lease-1-dispatch-4","targetHeadSha":"dddddddddddddddddddddddddddddddddddddddd","replacementReceiptRef":null,"authorityRef":"control://repository-change-controller","requestedAt":"2026-08-25T18:13:00Z"}
JSON
if python3 "$checker" transition --lease "$fixture/lease.json" --request "$fixture/mutate.json" > "$fixture/mutate-receipt.json"; then exit 1; fi
grep -q GOV-CHANGE-LEASE-003 "$fixture/mutate-receipt.json"
cat > "$fixture/supersede.json" <<'JSON'
{"schema":"wellmanifest.change-lease-transition/v1","requestId":"request-supersede","leaseId":"lease-1","action":"supersede","expectedRevision":4,"expectedFencingToken":10,"expectedPhase":"publication_frozen","requestedBy":"controller","idempotencyKey":"lease-1-supersede-4","targetHeadSha":null,"replacementReceiptRef":"receipt://replacement/1","authorityRef":"control://repository-change-controller","requestedAt":"2026-08-25T18:14:00Z"}
JSON
if python3 "$checker" transition --lease "$fixture/lease.json" --request "$fixture/supersede.json" > "$fixture/supersede-receipt.json"; then exit 1; fi
grep -q GOV-CHANGE-LEASE-003 "$fixture/supersede-receipt.json"
python3 - "$fixture/freeze-receipt.json" > "$fixture/trace.jsonl" <<'PY'
import json, sys
print(json.dumps(json.load(open(sys.argv[1], encoding="utf-8"))))
PY
python3 - "$fixture/freeze-receipt.json" >> "$fixture/trace.jsonl" <<'PY'
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
r.update(requestId="request-dispatch", previousRevision=4, leaseRevision=5, previousFencingToken=10, fencingToken=11, action="dispatch-validation", phaseBefore="publication_frozen", phaseAfter="dispatching", receiptRef="receipt://change-lease/lease-1/request-dispatch")
print(json.dumps(r))
PY
python3 "$checker" trace "$fixture/trace.jsonl" | grep -q GOV-CHANGE-LEASE-PASS
python3 - "$fixture/freeze-receipt.json" >> "$fixture/trace.jsonl" <<'PY'
import json, sys
print(json.dumps(json.load(open(sys.argv[1], encoding="utf-8"))))
PY
if python3 "$checker" trace "$fixture/trace.jsonl" > "$fixture/bad-trace.out"; then exit 1; fi
grep -q GOV-CHANGE-LEASE-002 "$fixture/bad-trace.out"
mkdir -p "$fixture/repository/.governance"
cp "$fixture/lease.json" "$fixture/repository/.governance/change-lease.json"
python3 "$checker" repository "$fixture/repository" | grep -q GOV-CHANGE-LEASE-PASS
printf '%s\n' 'change-lease tests: PASS'

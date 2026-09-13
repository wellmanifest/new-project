```dsl
DECISION D-218-0001
TICKET ticket-218
HEAD_SHA 6d2da011088b69ebe1636f3bf681e5ec21a062ab
CORRELATION_ID taskand-audit-20260913-hub
ACTOR agent:taskand
APPLIED_RULE P-CORE-016
INPUT decision_scope = "LOCAL_DETERMINISTIC_CHECK_ONLY_NOT_TRUSTED_APPROVAL"
INPUT required_checks = ["governance"]
INPUT observed_checks = ["governance=FAIL"]
INPUT governance_report = {"findings":[{"code":"GOV-BASE-002","evidence":{"acceptedBaseSha":"6d2da011088b69ebe1636f3bf681e5ec21a062ab","componentPatterns":["AGENTS.md","CONTRIBUTING.md","template/files/AGENTS.template.md","tests/agent-hosts.test.sh"],"observedBaseSha":"d54878a105a20d84dd554f205bc177dcacc8730a","overlappingPaths":["AGENTS.md","CONTRIBUTING.md","template/files/AGENTS.template.md","tests/agent-hosts.test.sh"],"source":"refs/remotes/origin/main"},"message":"Target branch changes overlap components approved for ticket-218.","paths":["AGENTS.md","CONTRIBUTING.md","project/ticket-218/intent.json","template/files/AGENTS.template.md","tests/agent-hosts.test.sh"],"remediation":"Refresh the branch, re-run validation and obtain fresh approval for the overlapping scope.","severity":"error"}],"root":".","runtimeVersion":"0.11.0","schema":"new-project.governance-report/v1","status":"failed","summary":{"errors":1,"findings":1,"warnings":0}}
INPUT publication_requested = false
VERDICT REQUEST_CHANGES AUTHORITY DETERMINISTIC
REJECTED APPROVE BECAUSE REQUIRED_GOVERNANCE_GATE_FAILED
ASSERT LOCAL_CHECK_DOES_NOT_AUTHORIZE_EDIT_DEPLOYMENT_OR_MERGE
ASSERT VERDICT_AUTHORITY != "ADVISORY"
```

# Decision log

```dsl
DECISION D-069-0001
TICKET ticket-069
HEAD_SHA fef743469082eb85b32ed1bd262fac8efcac6e60
CORRELATION_ID new-project-ticket-069-stacked-local-base
ACTOR agent:codex
APPLIED_RULE C-CONCURRENCY-003
INPUT unexpected_change = "empty lifecycle worktree removed by ticket-068 terminal cleanup"
INPUT primary_worktree = "dirty-and-preserved"
INPUT ticket_068_release = "v0.16.0:6800f0138bc9063eb2dacb0a8b797dedcafb7952"
INPUT ticket_068_closure = "fef743469082eb85b32ed1bd262fac8efcac6e60"
INPUT ticket_068_status_at_base = "DONE/DONE"
INPUT requested_scope = ["git-lifecycle","ticket-lifecycle"]
INPUT unsafe_change_reasons = []
INPUT expected_verdict_from_rule = "APPROVE"
VERDICT APPROVE AUTHORITY DETERMINISTIC
REJECTED WRITE_PRIMARY_OR_FORCE_NEW_FROM_ACTIVE_MAIN BECAUSE FOREIGN_DIRTY_STATE_AND_ACTIVE_TICKET_MUST_BE_PRESERVED
ASSERT NEW_WORKTREE_IS_UNIQUE_DIRTY_AND_SEQUENTIALLY_DEPENDS_ON_TICKET_068
```

```dsl
DECISION D-069-0002
TICKET ticket-069
HEAD_SHA e0314db86e9f2a78a0512605c27c855ce72ad267
CORRELATION_ID new-project-ticket-069-integrated-base-refresh
ACTOR agent:codex
APPLIED_RULE P-CORE-014
INPUT required_checks = ["ticket_068_integrated","foreign_changes_preserved","target_main_current"]
INPUT observed_checks = ["ticket_068_integrated=PASS","foreign_changes_preserved=PASS","target_main_current=PASS"]
INPUT unsafe_change_reasons = []
VERDICT APPROVE AUTHORITY DETERMINISTIC
REJECTED KEEP_STACKED_TARGET BECAUSE INTEGRATED_DEFAULT_BRANCH_IS_NOW_THE_CURRENT_APPROVED_BASE
ASSERT TICKET_069_ACCEPTED_BASE_EQUALS_CURRENT_ORIGIN_MAIN
```

```dsl
DECISION D-069-0003
TICKET ticket-069
HEAD_SHA 4e6ba5ec15873346446d67d8787f17f68f57f81e
CORRELATION_ID new-project-ticket-069-v0161-base-refresh
ACTOR agent:codex
APPLIED_RULE P-CORE-014
INPUT required_checks = ["ticket_070_implementation_integrated","conflicts_bounded_to_indexes","foreign_changes_preserved"]
INPUT observed_checks = ["ticket_070_implementation_integrated=PASS","conflicts_bounded_to_indexes=PASS","foreign_changes_preserved=PASS"]
INPUT unsafe_change_reasons = []
VERDICT APPROVE AUTHORITY DETERMINISTIC
REJECTED KEEP_STALE_BASE BECAUSE ORIGIN_MAIN_ADVANCED_TO_IMMUTABLE_V0161_TAG
ASSERT TICKET_069_ACCEPTED_BASE_EQUALS_V0161_ORIGIN_MAIN
```

```dsl
DECISION D-069-0004
TICKET ticket-069
HEAD_SHA 4e6ba5ec15873346446d67d8787f17f68f57f81e
CORRELATION_ID new-project-ticket-069-release-workstream
ACTOR agent:codex
APPLIED_RULE C-CONCURRENCY-003
INPUT competing_ticket = "ticket-070:IN_PROGRESS:PUBLICATION:governance"
INPUT manifest_limit = 1
INPUT implementation_isolated = true
INPUT contract_tests = "PASS"
INPUT expected_verdict_from_rule = "BLOCKED"
VERDICT BLOCKED AUTHORITY DETERMINISTIC
REJECTED MODIFY_OR_FORCE_CLOSE_TICKET_070 BECAUSE FOREIGN_PUBLICATION_SCOPE_AND_TERMINAL_EVIDENCE_ARE_NOT_OWNED_BY_TICKET_069
ASSERT TICKET_069_RELEASES_WORKSTREAM_AND_PRESERVES_ISOLATED_CHANGES
```

```dsl
DECISION D-069-0005
TICKET ticket-069
HEAD_SHA 3a16f4cc14cccac936b55d124ef296a7da1a2bc7
CORRELATION_ID new-project-ticket-069-publication-resume
ACTOR agent:codex
APPLIED_RULE C-PUBLISH-003
INPUT user_request = "push changes"
INPUT accepted_base = "452d4008a71d67ad1965f6042faa217978a82b42"
INPUT active_competing_governance_tickets = []
INPUT validation = ["rule_enforcement=PASS","linux_contract=PASS","contract_identity=PASS","diff_check=PASS"]
INPUT requested_effects = ["commit","ticket_branch_push","pull_request"]
INPUT forbidden_effects = ["direct_main","merge","tag","release"]
INPUT expected_verdict_from_rule = "APPROVE"
VERDICT APPROVE AUTHORITY DETERMINISTIC
REJECTED DIRECT_MAIN_OR_RELEASE BECAUSE USER_REQUEST_AUTHORIZES_REVIEWABLE_CHANGE_PUBLICATION_ONLY
ASSERT TICKET_STATUS_IS_IN_PROGRESS_AND_WORKFLOW_STATE_IS_PUBLICATION
```

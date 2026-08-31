```dsl
DECISION D-161-0001
TICKET ticket-161
HEAD_SHA d6097b846dfea06948540c0eadcf17ca6effc724
CORRELATION_ID ticket-identity-collision-recovery-20260830
ACTOR agent:codex
APPLIED_RULE C-CONCURRENCY-002
INPUT incident = "independent workers allocated ticket-034 before either claim was globally visible"
INPUT current_allocator_scope = "one Git common directory plus fetched refs"
INPUT distributed_writers = true
INPUT expected_verdict_from_rule = "REQUIRE_REGISTERED_ATOMIC_ALLOCATOR"
VERDICT REQUIRE_REGISTERED_ATOMIC_ALLOCATOR AUTHORITY DETERMINISTIC
REJECTED KEEP_LOCAL_HIGH_WATER_ONLY BECAUSE INDEPENDENT_CLONES_DO_NOT_SHARE_STATE
ADVISORY llm_verdict = "not-used" MODEL "none"
ASSERT VERDICT_AUTHORITY != "ADVISORY"
```

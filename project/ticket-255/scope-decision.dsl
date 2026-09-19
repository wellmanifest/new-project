DECISION D-255-0001
TICKET ticket-255
HEAD_SHA 368085282d0caa41cfa5ef2ec65644920566ae77
CORRELATION_ID ticket-255-worktree-regression-fixture
ACTOR agent:codex
APPLIED_RULE C-SCOPE-001
INPUT added_path = "tests/governance-scripts.test.sh"
INPUT reason = "The existing allocator regression fixture must provide the managed Worktrees v5 checker and commit a clean primary baseline before it invokes the new mandatory allocation route."
INPUT expected_verdict_from_rule = "SKIP"
VERDICT SKIP AUTHORITY DETERMINISTIC
REJECTED omit-regression-update BECAUSE Leaving the pre-v5 fixture unchanged makes the managed regression suite fail before it can exercise the allocator's prior collision guarantees.
ASSERT The added path is a bounded allocator regression fixture and remains within ticket-255's stated test responsibility.
ASSERT This record documents scope only and grants no review, publication, merge or controller authority.

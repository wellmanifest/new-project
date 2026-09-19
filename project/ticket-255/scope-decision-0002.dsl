DECISION D-255-0002
TICKET ticket-255
HEAD_SHA a93ee8c949f839233fbb5074555ad5abe281f736
CORRELATION_ID ticket-255-work-start-v5-fixture
ACTOR agent:codex
APPLIED_RULE C-SCOPE-001
INPUT added_path = "tests/work_start_test.py"
INPUT reason = "The mandatory Worktrees v5 allocation route changes the managed WorkStart fixture's required checker, ignore rule and canonical ticket assertions."
INPUT expected_verdict_from_rule = "SKIP"
VERDICT SKIP AUTHORITY DETERMINISTIC
REJECTED retain-primary-ticket-expectations BECAUSE Those assertions encode the allocator defect fixed by ticket-255 and fail before the CI suite reaches later regression coverage.
ASSERT The added path is a bounded existing allocator admission fixture and remains within ticket-255's stated test responsibility.
ASSERT This record documents scope only and grants no review, publication, merge or controller authority.

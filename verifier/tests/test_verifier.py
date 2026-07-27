import json

from office_dsl_verifier import verify, verify_semantic


def as_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def test_mock_verifier_passes_read_only_plan() -> None:
    report = verify(
        "Przygotuj raport faktur",
        as_text({"steps": [{"action": "report.generate"}]}),
        as_text({"actions": []}),
        ["report.generate"],
        [],
    )
    assert report.verdict == "PASS"
    assert report.recommended_action == "ACCEPT"


def test_mock_verifier_blocks_send_when_user_requested_drafts_only() -> None:
    report = verify(
        "Przygotuj wiadomosci, ale ich nie wysylaj",
        as_text({"steps": [{"action": "email.send"}]}),
        as_text({"actions": []}),
        ["email.send"],
        [],
    )
    assert report.verdict == "FAIL"
    assert "email.send" in report.unauthorized_actions


def test_mock_verifier_does_not_treat_policy_subject_as_action() -> None:
    report = verify(
        "Przygotuj wiadomosci, ale ich nie wysylaj",
        as_text(
            {
                "steps": [{"action": "email.prepare"}],
                "policies": [{"subject": "email.send", "decision": "REQUIRE"}],
            }
        ),
        as_text({"actions": ["database.query", "email.prepare"]}),
        ["email.prepare"],
        ["database.query", "email.prepare"],
    )
    assert report.verdict == "PASS"
    assert report.unauthorized_actions == []


def test_mock_verifier_blocks_command_attempts() -> None:
    report = verify(
        "Uruchom komende",
        as_text({"steps": [{"with": {"command": "rm -rf *"}}]}),
        as_text({"actions": []}),
        [],
        [],
    )
    assert report.verdict == "FAIL"
    assert report.recommended_action == "BLOCK"



def semantic_dsl(status: str = "CONFIRMED") -> dict[str, object]:
    return {
        "version": "intent-contract.dsl.v1",
        "document": {
            "id": "doc-1",
            "title": {
                "field": "document.title",
                "status": "CONFIRMED",
                "value": "Website agreement",
                "requiredForCompletion": True,
                "approvedBy": [],
                "source": {"id": "m1", "quote": "Website agreement"},
            },
        },
        "parties": [],
        "deliverables": [
            {
                "id": "del-1",
                "description": {
                    "field": "deliverables.del-1.description",
                    "status": status,
                    "value": "Landing page",
                    "requiredForCompletion": True,
                    "approvedBy": [],
                    "source": {"id": "m1", "quote": "Landing page"},
                },
            }
        ],
        "obligations": [],
        "acceptanceCriteria": [
            {
                "id": "acc-1",
                "description": {
                    "field": "acceptanceCriteria.acc-1.description",
                    "status": "CONFIRMED",
                    "value": "Loads in under two seconds",
                    "requiredForCompletion": True,
                    "approvedBy": [],
                    "source": {"id": "m1", "quote": "Loads in under two seconds"},
                },
            }
        ],
        "conflicts": [],
    }


def test_semantic_verifier_passes_matching_nl_document_code_and_tests() -> None:
    report = verify_semantic(
        {
            "original_nl": "Website agreement for Landing page. Loads in under two seconds.",
            "approved_dsl": semantic_dsl(),
            "rendered_document": "# Website agreement\nLanding page\nLoads in under two seconds\n",
            "codegen_verifier_input": {
                "generatedFiles": [{"path": "src/contract-spec.mjs", "sha256": "a" * 64}],
                "testResults": [{"name": "generated tests", "passed": True}],
            },
            "testgen_verifier_input": {"uncoveredAcceptanceCriteriaIds": []},
        }
    )
    assert report.verdict == "PASS"
    assert report.recommended_action == "ACCEPT"


def test_semantic_verifier_reports_document_and_code_mismatches() -> None:
    report = verify_semantic(
        {
            "original_nl": "Website agreement for Landing page. Loads in under two seconds.",
            "approved_dsl": semantic_dsl(),
            "rendered_document": "# Website agreement\nLanding page\n",
            "codegen_verifier_input": {
                "generatedFiles": [{"path": "src/contract-spec.mjs", "sha256": "a" * 64}],
                "testResults": [{"name": "generated tests", "passed": False}],
            },
        }
    )
    assert report.verdict == "FAIL"
    assert "acceptanceCriteria.acc-1.description" in report.document_mismatches
    assert "generated tests" in report.code_mismatches


def test_semantic_verifier_surfaces_missing_requirements_and_uncovered_acceptance() -> None:
    report = verify_semantic(
        {
            "original_nl": "Website agreement for Landing page. Loads in under two seconds.",
            "approved_dsl": semantic_dsl("MISSING"),
            "rendered_document": "# Website agreement\nLoads in under two seconds\n",
            "testgen_verifier_input": {"uncoveredAcceptanceCriteriaIds": ["acc-1"]},
        }
    )
    assert report.verdict == "FAIL"
    assert "deliverables.del-1.description" in report.missing_requirements
    assert "acc-1" in report.uncovered_acceptance_criteria


def test_semantic_verifier_requires_openrouter_configuration_outside_mock() -> None:
    try:
        verify_semantic({"original_nl": "x"}, mode="openrouter")
    except RuntimeError as exc:
        assert "OPENROUTER_API_KEY" in str(exc)
    else:
        raise AssertionError("openrouter mode should require explicit configuration")

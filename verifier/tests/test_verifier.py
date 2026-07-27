import json

from office_dsl_verifier import verify


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

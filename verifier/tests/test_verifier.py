from office_dsl_verifier import verify


def test_mock_verifier_passes_read_only_plan() -> None:
    report = verify("Przygotuj raport faktur", {"steps": [{"action": "report.generate"}]}, {"actions": []})
    assert report.verdict == "PASS"
    assert report.recommended_action == "ACCEPT"


def test_mock_verifier_blocks_send_when_user_requested_drafts_only() -> None:
    report = verify("Przygotuj wiadomosci, ale ich nie wysylaj", {"steps": [{"action": "email.send"}]}, {"actions": []})
    assert report.verdict == "FAIL"
    assert "email.send" in report.unauthorized_actions


def test_mock_verifier_blocks_command_attempts() -> None:
    report = verify("Uruchom komende", {"steps": [{"with": {"command": "rm -rf *"}}]}, {"actions": []})
    assert report.verdict == "FAIL"
    assert report.recommended_action == "BLOCK"

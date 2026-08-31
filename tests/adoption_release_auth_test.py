import importlib.util
from pathlib import Path


MODULE = Path(__file__).parents[1] / "scripts" / "create_adoption_lock.py"
SPEC = importlib.util.spec_from_file_location("adoption_lock", MODULE)
adoption_lock = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adoption_lock)


def test_release_lookup_uses_gh_auth_token_when_environment_has_none(monkeypatch):
    captured = {}

    class Result:
        returncode = 0
        stdout = "test-token\n"

    class Response:
        def __enter__(self): return self
        def __exit__(self, *_): return False
        def read(self, _): return b'{"tag_name":"v0.19.14","draft":false,"prerelease":false,"published_at":"2026-01-01T00:00:00Z"}'

    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(adoption_lock.subprocess, "run", lambda *_, **__: Result())
    monkeypatch.setattr(adoption_lock, "urlopen", lambda request, timeout: captured.update(headers=dict(request.header_items())) or Response())

    assert adoption_lock.canonical_release("0.19.14")["tag_name"] == "v0.19.14"
    assert captured["headers"]["Authorization"] == "Bearer test-token"

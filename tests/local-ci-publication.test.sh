#!/usr/bin/env bash
# Local OneDev + Validator publication applies to every repository by default.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
import json
import re
from pathlib import Path

policy = Path("docs/information/local-ci-publication.md").read_text()
agents = Path("template/files/AGENTS.template.md").read_text()
reference = Path("template/files/LOCAL_CI_PUBLICATION.template.md").read_text()

# No organization list limits the default any more.
for name, text in (("policy", policy), ("AGENTS", agents), ("reference", reference)):
    assert not re.search(r"For `semcod/\*` and|For Semcod and Subactor|For these two organizations", text), name
assert "For every repository" in policy and "no organization list limits it" in policy
assert "11a. **USE LOCAL ONEDEV AND THE INDEPENDENT VALIDATOR.** For every repository" in agents
assert "For every repository, by default" in reference
for text in (policy, agents, reference):
    assert ".governance/local-ci-publication.json" in text

schema = json.loads(Path("governance/local-ci-publication.schema.json").read_text())
assert schema["properties"]["schema"]["const"] == "new-project.local-ci-publication/v1"
assert schema["properties"]["scope"]["properties"]["mode"]["default"] == "all"

try:
    import jsonschema
except ImportError:
    print("jsonschema unavailable; structural checks only")
else:
    validator = jsonschema.Draft202012Validator(schema)
    ok = [
        {"schema": "new-project.local-ci-publication/v1", "scope": {"mode": "all"}},
        {"schema": "new-project.local-ci-publication/v1",
         "scope": {"mode": "restricted", "repositories": ["maskservice/*", "subactor/onedev-agent"]}},
    ]
    bad = [
        {"schema": "new-project.local-ci-publication/v1", "scope": {"mode": "restricted"}},
        {"schema": "new-project.local-ci-publication/v1", "scope": {"mode": "restricted", "repositories": []}},
        {"schema": "new-project.local-ci-publication/v1", "scope": {"mode": "all", "repositories": ["a/b"]}},
        {"schema": "new-project.local-ci-publication/v1", "scope": {"mode": "restricted", "repositories": ["*"]}},
        {"schema": "new-project.local-ci-publication/v1", "scope": {"mode": "all"}, "grants": ["merge"]},
    ]
    for document in ok:
        assert not list(validator.iter_errors(document)), document
    for document in bad:
        assert list(validator.iter_errors(document)), document
print("local-ci-publication: ok")
PY

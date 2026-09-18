#!/usr/bin/env python3

from __future__ import annotations

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GOVERNANCE_DIR = ROOT / "governance"
SSOT_PATH = GOVERNANCE_DIR / "canonical-schema-hosts.ssot.json"
DOCS_PATH = ROOT / "docs" / "information" / "canonical-schema-hosts.md"

ALLOWED_HOST_PREFIXES = (
    "https://wellmanifest.com/",
    "https://wellmanifest.dev/",
    "https://wellmanifest.org/",
    "https://github.com/wellmanifest/",
    "urn:wellmanifest:",
    "./",  # relative metaschema reference
)


class CanonicalSchemaHostsTest(unittest.TestCase):
    def test_ssot_decision_record_exists_and_valid(self):
        self.assertTrue(SSOT_PATH.is_file(), f"missing {SSOT_PATH}")
        data = json.loads(SSOT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "wellmanifest.ssot/decision/v1")
        self.assertEqual(data["id"], "canonical-schema-hosts")
        self.assertEqual(data["decisions"][0]["canonical"]["ref"], "https://wellmanifest.com/schemas")

    def test_all_governance_schemas_use_allowed_namespaces(self):
        schema_files = list(GOVERNANCE_DIR.glob("*.schema.json"))
        self.assertGreater(len(schema_files), 10, "Expected at least 10 schema files in governance/")

        for path in schema_files:
            data = json.loads(path.read_text(encoding="utf-8"))
            schema_id = data.get("$id")
            if schema_id is not None:
                self.assertTrue(
                    any(schema_id.startswith(prefix) for prefix in ALLOWED_HOST_PREFIXES),
                    f"{path.name} declares unapproved $id: {schema_id}",
                )

    def test_all_governance_schemas_use_json_schema_draft_metaschema(self):
        schema_files = list(GOVERNANCE_DIR.glob("*.schema.json"))
        for path in schema_files:
            data = json.loads(path.read_text(encoding="utf-8"))
            meta = data.get("$schema")
            if meta is not None:
                self.assertTrue(
                    meta.startswith("https://json-schema.org/") or meta.startswith("./"),
                    f"{path.name} declares invalid $schema: {meta}",
                )

    def test_documentation_declares_canonical_host_and_immutability(self):
        self.assertTrue(DOCS_PATH.is_file(), f"missing {DOCS_PATH}")
        content = DOCS_PATH.read_text(encoding="utf-8")
        self.assertIn("https://wellmanifest.com/schemas/", content)
        self.assertIn("Schema Immutability Invariant", content)
        self.assertIn("Supported Version Window", content)


if __name__ == "__main__":
    unittest.main()

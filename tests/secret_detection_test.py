#!/usr/bin/env python3
"""Regressions for Python expression vs literal secret detection (NP-009, Issue #453)."""
import unittest
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import governance_check as gov_managed

sys.path.insert(0, str(ROOT / "packages/wellman/src/wellman/_bundled"))
import governance_check as gov_bundled


class SecretDetectionTest(unittest.TestCase):
    def test_dynamic_calls_pass_in_both_packages(self):
        code = """
token = resolve_node_endpoint(node, node_url)
password = keyring.get_password("service", "user")
api_key = get_env_or_secret("API_KEY")
"""
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "service.py"), [])

    def test_attribute_calls_and_lookups_pass(self):
        code = """
token = config.auth.token
password = credentials.get("password")
client_secret = self.session.token.secret
"""
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "auth.py"), [])

    def test_tuple_assignments_pass(self):
        code = """
target_node, target_url, target_token = resolve_node_endpoint(node, node_url)
node, url, token = resolve_node_endpoint("lenovo")
(user, password) = parse_auth_header(header)
"""
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "document_sync.py"), [])

    def test_keyword_variable_forwarding_passes(self):
        code = """
res = upload_document_to_node(target_url, remote_path, data, token=resolved_token)
client = Client(api_key=api_key, client_secret=secret_var)
"""
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "sync.py"), [])

    def test_genuine_literal_secrets_refuse(self):
        code = """
API_TOKEN = "sk_live_4f3d2c1b0a9876543210"
password = "super_secret_production_password"
client = Client(token="sk_live_4f3d2c1b0a9876543210")
headers = {"client_secret": "my_super_secret_client_token"}
def connect(api_key: str = "sk_live_4f3d2c1b0a9876543210"):
    pass
"""
        for mod in (gov_managed, gov_bundled):
            fields = mod.probable_secret_fields(code, "settings.py")
            self.assertIn("TOKEN", fields)
            self.assertIn("password", fields)
            self.assertIn("token", fields)
            self.assertIn("client_secret", fields)
            self.assertIn("api_key", fields)

    def test_string_concatenation_secrets_refuse(self):
        code = 'token = "sk_live_" + "4f3d2c1b0a9876543210"'
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "keys.py"), ["token"])

    def test_malformed_python_source_falls_back_to_regex(self):
        code = 'token = sk_live_4f3d2c1b0a9876543210 def invalid syntax ('
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "broken.py"), ["token"])

    def test_shell_and_config_fixtures_still_refuse(self):
        shell_script = 'API_TOKEN=sk_live_4f3d2c1b0a9876543210\n'
        yaml_config = 'token: sk_live_4f3d2c1b0a9876543210\n'
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(shell_script, "deploy.sh"), ["TOKEN"])
            self.assertEqual(mod.probable_secret_fields(yaml_config, "config.yml"), ["token"])
            # Without filename argument, defaults to generic regex check
            self.assertEqual(mod.probable_secret_fields(shell_script), ["TOKEN"])
            self.assertEqual(mod.probable_secret_fields(yaml_config), ["token"])

    def test_safe_placeholders_pass_in_both_modes(self):
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields("API_TOKEN=__GENERATE_API_TOKEN__"), [])
            self.assertEqual(mod.probable_secret_fields("API_TOKEN=placeholder_value"), [])
            self.assertEqual(mod.probable_secret_fields('token = "__GENERATE_TOKEN__"', "test.py"), [])
            self.assertEqual(mod.probable_secret_fields('token = "placeholder_token_val"', "test.py"), [])


if __name__ == "__main__":
    unittest.main()

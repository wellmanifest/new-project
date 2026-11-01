#!/usr/bin/env python3
"""Regressions for Python expression vs literal secret detection (NP-009, Issue #453)."""
import unittest
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
def load_checker(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gov_managed = load_checker("secret_test_managed", ROOT / "scripts/governance_check.py")
gov_bundled = load_checker("secret_test_bundled", ROOT / "packages/wellman/src/wellman/_bundled/governance_check.py")


class SecretDetectionTest(unittest.TestCase):
    def test_all_positional_default_forms_refuse_in_both_modules(self):
        cases = [
            'def connect(token="fake-test-value", /): pass',
            'async def connect(password="fake-test-value", /): pass',
            'def connect(token="fake-test-value", /, ordinary="safe"): pass',
            'def connect(ordinary, /, token="fake-test-value"): pass',
            'lambda token="fake-test-value", /: token',
            'lambda token="fake-test-value": token',
            'lambda *, token="fake-test-value": token',
        ]
        for mod in (gov_managed, gov_bundled):
            for code in cases:
                with self.subTest(module=mod.__name__, code=code):
                    self.assertTrue(mod.probable_secret_fields(code, "defaults.py"))

    def test_comparison_targets_and_operand_order_refuse(self):
        cases = [
            ('token == "fake-test-value"', ['token']),
            ('"fake-test-value" == token', ['token']),
            ('settings.password != "fake-test-value"', ['password']),
            ('"fake-test-value" != settings.password', ['password']),
            ('config["api_key"] == "fake-test-value"', ['api_key']),
            ('"fake-test-value" == config["api_key"]', ['api_key']),
            ('"credential_" + "literal_12345" == config["client_secret"]', ['client_secret']),
            ('token == ordinary == "fake-test-value"', ['token']),
            ('"fake-test-value" == settings.password == config["token"]', ['password', 'token']),
        ]
        for mod in (gov_managed, gov_bundled):
            for code, expected in cases:
                with self.subTest(module=mod.__name__, code=code):
                    self.assertEqual(mod.probable_secret_fields(code, "compare.py"), expected)

    def test_positional_default_alignment_and_safe_values_pass(self):
        code = '''
def mixed(token, /, ordinary="fake-test-value"): pass
def trailing(token="placeholder_value", /, ordinary="fake-test-value"): pass
async def dynamic({password_parameter}=resolve_password(), /): pass
lambda token, /, ordinary="fake-test-value": ordinary
lambda token="__GENERATE_TOKEN__", /: token
lambda *, {token_parameter}=resolve_token(): token
'''.format(password_parameter="password", token_parameter="token")
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "defaults.py"), [])

    def test_comparisons_keep_dynamic_placeholders_and_other_fields_safe(self):
        code = '''
token == resolve_token()
settings.password != credentials.password
config["api_key"] == "placeholder_value"
"__GENERATE_TOKEN__" == config["token"]
ordinary == "fake-test-value"
config[field_name] == "fake-test-value"
settings.ordinary == "fake-test-value"
'''
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "compare.py"), [])

    def test_managed_and_bundled_are_independent_modules(self):
        self.assertIsNot(gov_managed, gov_bundled)
        self.assertNotEqual(gov_managed.__file__, gov_bundled.__file__)

    def test_attribute_subscript_and_nested_literal_assignments_refuse(self):
        cases = [
            ('self.api_token = "credential_literal_12345"', ['token']),
            ('settings.password: str = "credential_literal_12345"', ['password']),
            ('config["client_secret"] = "credential_literal_12345"', ['client_secret']),
            ('config["api_key"]: str = "credential_literal_12345"', ['api_key']),
            ('user, (settings.password, config["token"]) = "name", ("credential_literal_12345", "credential_literal_67890")', ['password', 'token']),
            ('self.token = config["password"] = "credential_literal_12345"', ['password', 'token']),
        ]
        for mod in (gov_managed, gov_bundled):
            for code, expected in cases:
                with self.subTest(module=mod.__name__, code=code):
                    self.assertEqual(mod.probable_secret_fields(code, "settings.py"), expected)

    def test_nonliteral_assignment_targets_keep_dynamic_values_safe(self):
        code = '''
self.token = config.token
settings.password: str = keyring.get_password("service", "user")
config["api_key"] = resolve_key()
settings.password, config["token"] = resolve_credentials()
self.token = "placeholder_value"
config["password"] = "__GENERATE_PASSWORD__"
ordinary_field = "credential_literal_12345"
'''
        for mod in (gov_managed, gov_bundled):
            self.assertEqual(mod.probable_secret_fields(code, "settings.py"), [])

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

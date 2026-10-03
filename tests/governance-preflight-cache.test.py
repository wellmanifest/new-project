#!/usr/bin/env python3
"""Tests for deterministic governance preflight cache and phase timing."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
import governance_check


class PreflightCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="preflight-cache-test-")
        self.addCleanup(self.temp_dir.cleanup)
        self.cache_file = Path(self.temp_dir.name) / "cache.json"
        self.old_hooks = subprocess.run(
            ["git", "-C", str(SOURCE), "config", "--get", "core.hooksPath"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        if self.old_hooks != ".githooks":
            subprocess.run(["git", "-C", str(SOURCE), "config", "core.hooksPath", ".githooks"], check=False)

    def tearDown(self):
        if self.old_hooks:
            subprocess.run(["git", "-C", str(SOURCE), "config", "core.hooksPath", self.old_hooks], check=False)
        else:
            subprocess.run(["git", "-C", str(SOURCE), "config", "--unset", "core.hooksPath"], check=False)

    def test_timing_payload_and_render_text(self):
        """AC-01: Report phase timings and repeated work."""
        report = governance_check.Report(SOURCE, timing=True)
        report.record_timing("step_one", 0.01234)
        report.record_timing("step_two", 0.05678)
        payload = report.payload()
        self.assertIn("timings", payload)
        self.assertEqual(payload["timings"]["step_one"], 0.0123)
        self.assertEqual(payload["timings"]["step_two"], 0.0568)

        text = governance_check.render_text(payload)
        self.assertIn("Phase timings:", text)
        self.assertIn("step_one: 0.0123s", text)
        self.assertIn("step_two: 0.0568s", text)

    def test_cache_allowed_predicate(self):
        """AC-03: Cache allowed locally, disabled in CI and with --no-cache."""
        args = argparse.Namespace(no_cache=False, actor="agent", enforce_approval=False)
        old_ci = os.environ.get("CI")
        old_gh = os.environ.get("GITHUB_ACTIONS")
        try:
            os.environ.pop("CI", None)
            os.environ.pop("GITHUB_ACTIONS", None)
            self.assertTrue(governance_check.is_preflight_cache_allowed(args))

            # Disallowed by --no-cache
            args.no_cache = True
            self.assertFalse(governance_check.is_preflight_cache_allowed(args))
            args.no_cache = False

            # Disallowed by CI actor
            args.actor = "ci"
            self.assertFalse(governance_check.is_preflight_cache_allowed(args))
            args.actor = "agent"

            # Disallowed by enforce-approval
            args.enforce_approval = True
            self.assertFalse(governance_check.is_preflight_cache_allowed(args))
            args.enforce_approval = False

            # Disallowed by CI environment variable
            os.environ["CI"] = "true"
            self.assertFalse(governance_check.is_preflight_cache_allowed(args))
            os.environ.pop("CI", None)

            os.environ["GITHUB_ACTIONS"] = "true"
            self.assertFalse(governance_check.is_preflight_cache_allowed(args))
        finally:
            if old_ci is not None:
                os.environ["CI"] = old_ci
            else:
                os.environ.pop("CI", None)
            if old_gh is not None:
                os.environ["GITHUB_ACTIONS"] = old_gh
            else:
                os.environ.pop("GITHUB_ACTIONS", None)

    def test_save_and_load_preflight_cache(self):
        """AC-02: Deterministic reuse of cached results."""
        cache_key = "test-sha-12345"
        payload = {
            "schema": "new-project.governance-report/v1",
            "runtimeVersion": governance_check.RUNTIME_VERSION,
            "root": ".",
            "status": "passed",
            "summary": {"errors": 0, "warnings": 0, "findings": 0},
            "findings": [],
        }
        governance_check.save_preflight_cache(self.cache_file, cache_key, payload, "ticket-243")

        loaded = governance_check.load_preflight_cache(self.cache_file, cache_key)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["selected_ticket"], "ticket-243")
        self.assertEqual(loaded["payload"]["status"], "passed")

        miss = governance_check.load_preflight_cache(self.cache_file, "different-key")
        self.assertIsNone(miss)

    def test_cache_cli_hit_and_invalidation(self):
        """Integration test: CLI invocation, hit, and invalidation."""
        cmd_base = [
            sys.executable,
            str(SOURCE / "scripts" / "governance_check.py"),
            "--root", str(SOURCE),
            "--manifest", "governance/manifest.hub.json",
            "--stack-profiles", "governance/stack-profiles.json",
            "--work-classification", "governance/work-classification.dsl.json",
            "--base", "origin/main",
            "--head", "HEAD",
            "--actor", "agent",
            "--cache-file", str(self.cache_file),
            "--timing",
            "--format", "json",
        ]

        # 1st run: Cache miss, writes cache
        env = os.environ.copy()
        env.pop("CI", None)
        env.pop("GITHUB_ACTIONS", None)
        out1 = subprocess.check_output(cmd_base, cwd=SOURCE, env=env)
        data1 = json.loads(out1)
        self.assertEqual(data1["status"], "passed")
        self.assertNotIn("cached", data1)
        self.assertTrue(self.cache_file.exists())

        # 2nd run: Cache hit
        out2 = subprocess.check_output(cmd_base, cwd=SOURCE, env=env)
        data2 = json.loads(out2)
        self.assertEqual(data2["status"], "passed")
        self.assertTrue(data2.get("cached"))
        self.assertIn("preflight_cache", data2.get("timings", {}))

        # 3rd run with --no-cache: Bypass cache
        cmd_no_cache = cmd_base + ["--no-cache"]
        out3 = subprocess.check_output(cmd_no_cache, cwd=SOURCE, env=env)
        data3 = json.loads(out3)
        self.assertEqual(data3["status"], "passed")
        self.assertNotIn("cached", data3)

        # 4th run with CI=true: Bypass cache
        env_ci = env.copy()
        env_ci["CI"] = "true"
        out4 = subprocess.check_output(cmd_base, cwd=SOURCE, env=env_ci)
        data4 = json.loads(out4)
        self.assertEqual(data4["status"], "passed")
        self.assertNotIn("cached", data4)


class CachedOutputTests(unittest.TestCase):
    def test_current_output_errors_are_combined_with_cached_results(self):
        import hashlib
        env = dict(os.environ)
        env.pop("CI", None)
        env.pop("GITHUB_ACTIONS", None)
        # The fixture models a local agent preflight on clean CI checkouts.
        # Activate the actual managed hook only for these child processes.
        # Repository configuration is untouched and existing Git settings stay.
        cached_config_count = int(env.get("GIT_CONFIG_COUNT", "0"))
        self.assertTrue(0 <= cached_config_count <= 256)
        env[f"GIT_CONFIG_KEY_{cached_config_count}"] = "core.hooksPath"
        env[f"GIT_CONFIG_VALUE_{cached_config_count}"] = ".githooks"
        env["GIT_CONFIG_COUNT"] = str(cached_config_count + 1)
        base = next((revision for revision in ("origin/main", "HEAD^") if subprocess.run(
            ["git", "rev-parse", "--verify", revision + "^{commit}"], cwd=SOURCE,
            env=env, capture_output=True).returncode == 0), None)
        self.assertIsNotNone(base, "Cache CLI fixture needs an available meaningful Git base")
        for relative in ("scripts/governance_check.py", "packages/wellman/src/wellman/_bundled/governance_check.py"):
            with self.subTest(checker=relative), tempfile.TemporaryDirectory(prefix="cached-output-test-") as temporary:
                control = Path(temporary)
                cache = control / "cache.json"
                directory = control / "existing-directory"
                directory.mkdir()
                cmd = [sys.executable, str(SOURCE / relative), "--root", str(SOURCE),
                       "--manifest", "governance/manifest.hub.json", "--base", base, "--head", "HEAD",
                       "--actor", "agent", "--cache-file", str(cache), "--timing", "--format", "json"]
                def invoke(*extra):
                    run = subprocess.run(cmd + list(extra), cwd=SOURCE, env=env,
                                         capture_output=True, text=True, encoding="utf-8")
                    self.assertTrue(run.stdout.strip(), run.stderr)
                    return run, json.loads(run.stdout)
                run, payload = invoke()
                self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
                self.assertNotIn("cached", payload)
                envelope = json.loads(cache.read_text(encoding="utf-8"))
                self.assertEqual(len(envelope["entries"]), 1)
                entry = next(iter(envelope["entries"].values()))
                # A controlled advisory cached selector exercises writer errors
                # even on an already-merged main with no selected pending ticket.
                # It is fixture data and supplies no ticket or approval authority.
                entry["selected_ticket"] = entry.get("selected_ticket") or "ticket-001"
                warning = governance_check.Report(SOURCE)
                warning.add("GOV-PATH-001", "Controlled cached warning", "Controlled fixture", severity="warning")
                entry["payload"]["findings"].extend(warning.payload()["findings"])
                entry["payload"]["summary"]["warnings"] += 1
                entry["payload"]["summary"]["findings"] += 1
                cache.write_text(json.dumps(envelope), encoding="utf-8")
                digest = hashlib.sha256(cache.read_bytes()).hexdigest()
                denied = SOURCE / "never-created-cached-output-fixture.txt"
                self.assertFalse(denied.exists())
                for extra in (("--output", "../never-created-cached-output-fixture.json"),
                              ("--resolved-ticket-output", str(denied)),
                              ("--resolved-ticket-output", str(directory))):
                    with self.subTest(arguments=extra):
                        run, payload = invoke(*extra)
                        self.assertEqual(run.returncode, 1, run.stderr)
                        self.assertTrue(payload["cached"])
                        self.assertEqual(payload["status"], "failed")
                        self.assertEqual(payload["summary"], {"errors": 1, "warnings": 1, "findings": 2})
                        self.assertEqual(len(payload["findings"]), 2)
                        self.assertTrue(any(item["severity"] == "error" and item["code"] == "GOV-PATH-001"
                                            for item in payload["findings"]))
                        self.assertTrue(any(item["message"] == "Controlled cached warning" for item in payload["findings"]))
                        self.assertIn("preflight_cache", payload["timings"])
                        self.assertEqual(hashlib.sha256(cache.read_bytes()).hexdigest(), digest)
                        self.assertFalse(denied.exists())
                resolved = control / "resolved-ticket.txt"
                run, payload = invoke("--resolved-ticket-output", str(resolved))
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertTrue(payload["cached"])
                self.assertEqual(payload["status"], "passed")
                self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1, "findings": 1})
                self.assertEqual(resolved.read_text(encoding="utf-8"), entry["selected_ticket"] + "\n")
                self.assertEqual(hashlib.sha256(cache.read_bytes()).hexdigest(), digest)



if __name__ == "__main__":
    unittest.main()

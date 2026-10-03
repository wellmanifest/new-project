#!/usr/bin/env python3
"""Pinned ESM execution survives replacement between verification and Node."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ticket_storage


@unittest.skipUnless(shutil.which("node"), "Node required for real execution")
class RegistryRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = {
            "storage-common.mjs": 'export const marker = "original";\n',
            "ticket-store.mjs": 'export {marker} from "./storage-common.mjs";\n',
            "ticket-store-cli.mjs": '''import {marker} from './ticket-store.mjs';
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
if (import.meta.url !== pathToFileURL(process.argv[1]).href) throw Error('identity');
console.log(JSON.stringify({marker, args: process.argv.slice(2), input: fs.readFileSync(0, 'utf8')}));
''',
        }
        self.write_sources()

    def write_sources(self):
        for name, source in self.sources.items():
            (self.root / name).write_bytes(source.encode("utf-8"))
        # Independent fixture pin: never derive it through code under test.
        hashes = {name: hashlib.sha256(source.encode()).hexdigest()
                  for name, source in self.sources.items()}
        self.pin = hashlib.sha256(json.dumps(hashes, sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()

    def test_entry_replacement_after_verification_cannot_execute(self):
        real_run = subprocess.run
        def replace(*args, **kwargs):
            (self.root / "ticket-store-cli.mjs").write_text('console.log("{\\"marker\\":\\"replacement\\"}");')
            return real_run(*args, **kwargs)
        with patch.object(ticket_storage.subprocess, "run", side_effect=replace):
            result = ticket_storage.invoke(self.root, self.pin, "read")
        self.assertEqual(result["marker"], "original")

    def test_dependency_replacement_after_verification_cannot_execute(self):
        real_run = subprocess.run
        def replace(*args, **kwargs):
            (self.root / "storage-common.mjs").write_text('export const marker = "replacement";')
            return real_run(*args, **kwargs)
        with patch.object(ticket_storage.subprocess, "run", side_effect=replace):
            result = ticket_storage.invoke(self.root, self.pin, "read")
        self.assertEqual(result["marker"], "original")

    def test_unicode_stdin_arguments_and_entry_identity(self):
        content = 'Zażółć Ελληνικά Україна\n"quoted"\\path\n'
        result = ticket_storage.invoke(self.root, self.pin, "update", "--file", "é.json", content=content)
        self.assertEqual(result, {"marker": "original", "args": ["update", "--file", "é.json"], "input": content})

    def test_source_closure_larger_than_single_argument_limit(self):
        self.sources["storage-common.mjs"] += "//" + "x" * 200_000 + "\n"
        self.write_sources()
        result = ticket_storage.invoke(self.root, self.pin, "read", content="body")
        self.assertEqual(result["marker"], "original")
        self.assertEqual(result["input"], "body")

    def test_async_stdin_reader_sees_only_original_content(self):
        self.sources["ticket-store-cli.mjs"] = '''import {marker} from './ticket-store.mjs';
const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
console.log(JSON.stringify({marker, input: Buffer.concat(chunks).toString('utf8')}));
'''
        self.write_sources()
        content = "żaółć\n" * 50_000
        result = ticket_storage.invoke(self.root, self.pin, "create", content=content)
        self.assertEqual(result, {"marker": "original", "input": content})

    def test_unpinned_relative_import_is_rejected(self):
        self.sources["ticket-store.mjs"] = 'export {marker} from "./unverified.mjs";'
        (self.root / "unverified.mjs").write_text('export const marker = "replacement";')
        self.write_sources()
        with self.assertRaises(ValueError):
            ticket_storage.invoke(self.root, self.pin, "read")

    def test_invalid_pins_rejected_before_node(self):
        with patch.object(ticket_storage.subprocess, "run") as run:
            for pin in (None, "", "0" * 64):
                with self.assertRaises(ValueError):
                    ticket_storage.invoke(self.root, pin, "read")
            run.assert_not_called()

    def test_symlink_and_oversized_module_rejected(self):
        dependency = self.root / "storage-common.mjs"
        dependency.unlink()
        try:
            dependency.symlink_to(self.root / "ticket-store.mjs")
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaises(ValueError):
            ticket_storage.invoke(self.root, self.pin, "read")
        dependency.unlink()
        dependency.write_bytes(b"x" * (1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            ticket_storage.invoke(self.root, self.pin, "read")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO fixture")
    def test_non_regular_module_rejected_without_blocking(self):
        dependency = self.root / "storage-common.mjs"
        dependency.unlink()
        os.mkfifo(dependency)
        with self.assertRaises(ValueError):
            ticket_storage.invoke(self.root, self.pin, "read")


if __name__ == "__main__":
    unittest.main()

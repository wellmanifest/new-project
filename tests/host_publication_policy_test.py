"""Host projection preserves bytes and refuses ambiguous or stale effects."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('host_policy', ROOT / 'scripts/host_publication_policy.py')
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)
HOST = '''# Custom host policy\nFirmware: preserve this instruction.\n<!-- wellmanifest:autonomous-merge:start -->\nold admin bypass and reviewer rotation\n<!-- wellmanifest:autonomous-merge:end -->\n\n<!-- wellmanifest:nolimits:start -->\n3. **Merge Pipeline Lock (`LIM-MERGE-003`)**: PR checks green but blocked on review/WIP limits.\n   - **Remediation**: Use [`wellmanifest/merge`](https://github.com/wellmanifest/merge):\n     Execute autonomous merge under `wellmanifest/merge@ticket-008` (Prymat Zielonych Testów).\n4. preserve other remedies\n<!-- wellmanifest:nolimits:end -->\n# User appendix\nNever change this appendix.\n'''


class HostPublicationPolicyTest(unittest.TestCase):
    def test_preserves_unowned_sections_and_is_idempotent(self):
        result = POLICY.render(HOST)
        self.assertTrue(result.startswith('# Custom host policy\nFirmware: preserve this instruction.\n'))
        self.assertTrue(result.endswith('# User appendix\nNever change this appendix.\n'))
        self.assertIn('4. preserve other remedies', result)
        self.assertNotIn('old admin bypass', result)
        self.assertNotIn('Prymat Zielonych Testów', result)
        self.assertIn('independent Validator', result)
        self.assertEqual(POLICY.render(result), result)

    def test_crlf_preserved(self):
        result = POLICY.render(HOST.replace('\n', '\r\n'))
        self.assertNotIn('\n', result.replace('\r\n', ''))

    def test_ambiguous_markers_and_unknown_remedy_fail(self):
        for text in [HOST + '<!-- wellmanifest:autonomous-merge:start -->',
                     HOST.replace('autonomous-merge:end', 'broken:end'),
                     HOST.replace('Execute autonomous merge under', 'Unknown custom override under')]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                POLICY.render(text)

    def fixture(self, folder):
        path = Path(folder) / 'AGENTS.md'
        path.write_bytes(HOST.encode())
        path.chmod(0o640)
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_preview_is_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path, digest = self.fixture(folder)
            result = POLICY.reconcile(path, digest, apply=False, backup_directory=None)
            self.assertTrue(result['changed'])
            self.assertFalse(result['applied'])
            self.assertEqual(path.read_bytes(), HOST.encode())
            self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_apply_backup_restorable_and_mode_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path, digest = self.fixture(folder)
            backup = Path(folder) / 'backup'
            result = POLICY.reconcile(path, digest, apply=True, backup_directory=backup)
            self.assertTrue(result['applied'])
            self.assertEqual(Path(result['backup']).read_bytes(), HOST.encode())
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), result['afterSha256'])
            prior = path.read_bytes()
            second = POLICY.reconcile(path, result['afterSha256'], apply=True, backup_directory=backup)
            self.assertFalse(second['applied'])
            self.assertEqual(path.read_bytes(), prior)

    def test_stale_digest_refuses_before_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            path, _ = self.fixture(folder)
            with self.assertRaises(ValueError):
                POLICY.reconcile(path, '0' * 64, apply=True, backup_directory=Path(folder) / 'backup')
            self.assertEqual(list(Path(folder).iterdir()), [path])
            self.assertEqual(path.read_bytes(), HOST.encode())

    def test_symlink_and_competing_lock_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path, digest = self.fixture(folder)
            link = Path(folder) / 'link'
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                POLICY.reconcile(link, digest, apply=True, backup_directory=Path(folder) / 'backup')
            lock = path.with_name('.' + path.name + '.publication.lock')
            lock.write_text('other writer')
            with self.assertRaises(FileExistsError):
                POLICY.reconcile(path, digest, apply=True, backup_directory=Path(folder) / 'backup')
            self.assertEqual(lock.read_text(), 'other writer')
            self.assertEqual(path.read_bytes(), HOST.encode())


if __name__ == '__main__':
    unittest.main()

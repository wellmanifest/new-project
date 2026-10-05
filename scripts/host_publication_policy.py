#!/usr/bin/env python3
"""Reconcile owned host instruction blocks; preview grants no authority."""
import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path

START = '<!-- wellmanifest:autonomous-merge:start -->'
END = '<!-- wellmanifest:autonomous-merge:end -->'
BLOCK = '''## Autonomous publication through independent validation

Use the published wellmanifest/new-project local CI publication policy and
wellmanifest/merge actor boundary for every repository. The coding agent may
test, commit, push its authorized ticket branch, open the PR and request
publication. Only the independent Validator may approve and merge.

- Resolve the deployed protected registry and OneDev profile before delivery.
- OneDev verifies the exact head merged with the current base, without
  publication credentials. Freeze the head through independent validation.
- Invoke the trusted local run-local-direct-pr.sh adapter or reuse the existing
  local reconciliation timer and its matching protected receipt.
- A GitHub Actions billing failure is a check that did not run. Retire a hosted
  context only after equivalent deployed coverage and independent policy review.
- Never self-approve, rotate reviewer accounts, use administrative bypass,
  invent success statuses or waive ticket scope/WIP controls.
- On API limits, retain retry state and honor Retry-After/reset deadlines.
- Read back the exact review and merge before releasing scope. Remove only a
  verified owned clean worktree after checking processes, lease and recoverability.

Host instructions do not grant a controller lease or weaken protected checks.
'''
OLD_REMEDY = '''3. **Merge Pipeline Lock (`LIM-MERGE-003`)**: PR checks green but blocked on review/WIP limits.
   - **Remediation**: Use [`wellmanifest/merge`](https://github.com/wellmanifest/merge):
     Execute autonomous merge under `wellmanifest/merge@ticket-008` (Prymat Zielonych Testów).'''
NEW_REMEDY = '''3. **Merge Pipeline Lock (`LIM-MERGE-003`)**: Required verification or independent publication is pending.
   - **Remediation**: Use protected local OneDev verification and the independent Validator.
     Preserve required checks, scope/WIP controls and retry state; reconcile missing profiles in their owning repositories.'''


def render(text):
    newline = '\r\n' if '\r\n' in text else '\n'
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError('HOST_PUBLICATION_MARKERS_AMBIGUOUS')
    begin, finish = text.index(START), text.index(END)
    if finish <= begin:
        raise ValueError('HOST_PUBLICATION_MARKERS_ORDER_INVALID')
    result = text[:begin] + START + newline + BLOCK.replace('\n', newline) + END + text[finish + len(END):]
    for marker in ('<!-- wellmanifest:nolimits:start -->', '<!-- wellmanifest:nolimits:end -->'):
        if result.count(marker) != 1:
            raise ValueError('HOST_NOLIMITS_MARKERS_AMBIGUOUS')
    left = result.index('<!-- wellmanifest:nolimits:start -->')
    right = result.index('<!-- wellmanifest:nolimits:end -->')
    if right <= left:
        raise ValueError('HOST_NOLIMITS_MARKERS_ORDER_INVALID')
    section = result[left:right]
    old, new = OLD_REMEDY.replace('\n', newline), NEW_REMEDY.replace('\n', newline)
    if section.count(old) == 1:
        section = section.replace(old, new)
    elif section.count(new) != 1:
        raise ValueError('HOST_MERGE_REMEDY_UNKNOWN')
    return result[:left] + section + result[right:]


def safe_path(path):
    path = Path(path).absolute()
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ValueError('HOST_PUBLICATION_SYMLINK_REFUSED')
    return path


def reconcile(path, expected_digest, *, apply=False, backup_directory=None):
    if not re.fullmatch('[0-9a-f]{64}', expected_digest):
        raise ValueError('HOST_PUBLICATION_DIGEST_REQUIRED')
    path = safe_path(path)
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError('HOST_PUBLICATION_REGULAR_FILE_REQUIRED')
    before = path.read_bytes()
    if hashlib.sha256(before).hexdigest() != expected_digest:
        raise ValueError('HOST_PUBLICATION_STALE_INPUT')
    after = render(before.decode('utf-8')).encode('utf-8')
    report = {'schema': 'new-project.host-publication-result/v1',
              'path': str(path), 'beforeSha256': expected_digest,
              'afterSha256': hashlib.sha256(after).hexdigest(),
              'changed': before != after, 'applied': False, 'authority': 'NONE'}
    if not apply or before == after:
        return report
    if backup_directory is None:
        raise ValueError('HOST_PUBLICATION_BACKUP_REQUIRED')
    backup_directory = safe_path(backup_directory)
    lock = path.with_name('.' + path.name + '.publication.lock')
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    identity = os.fstat(descriptor)
    scratch = None
    try:
        os.close(descriptor)
        current = path.stat()
        if (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino) or path.read_bytes() != before:
            raise ValueError('HOST_PUBLICATION_STALE_INPUT')
        backup_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        backup = safe_path(backup_directory / (path.name + '.' + expected_digest + '.backup'))
        try:
            with backup.open('xb') as stream:
                os.chmod(backup, 0o600)
                stream.write(before)
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            if backup.read_bytes() != before:
                raise ValueError('HOST_PUBLICATION_BACKUP_CONFLICT')
        if backup.read_bytes() != before:
            raise ValueError('HOST_PUBLICATION_BACKUP_NOT_RESTORABLE')
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '.', delete=False) as stream:
            scratch = Path(stream.name)
            os.chmod(scratch, stat.S_IMODE(metadata.st_mode))
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        safe_path(path)
        current = path.stat()
        if (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino) or path.read_bytes() != before:
            raise ValueError('HOST_PUBLICATION_STALE_INPUT')
        os.replace(scratch, path)
        scratch = None
        report.update(applied=True, backup=str(backup))
        if path.read_bytes() != after:
            raise ValueError('HOST_PUBLICATION_READBACK_MISMATCH')
        return report
    finally:
        if scratch is not None:
            scratch.unlink()
        current_lock = lock.lstat()
        if (current_lock.st_dev, current_lock.st_ino) == (identity.st_dev, identity.st_ino):
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup-directory', type=Path)
    args = parser.parse_args()
    try:
        result = reconcile(args.path, args.expected_sha256, apply=args.apply, backup_directory=args.backup_directory)
    except (ValueError, OSError) as error:
        print(json.dumps({'status': 'refused', 'error': str(error) if isinstance(error, ValueError) else type(error).__name__}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

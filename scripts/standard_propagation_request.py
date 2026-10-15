#!/usr/bin/env python3
"""Emit immutable standard release facts; never admit or execute adopter writes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import subprocess
from pathlib import Path

import create_adoption_lock as publication

SCHEMA = 'new-project.standard-propagation-request/v1'
REPOSITORY = 'wellmanifest/new-project'
MAX_EVENT_BYTES = 1024 * 1024
VERSION = re.compile(r'(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)', re.ASCII)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate event key')
        result[key] = value
    return result


def read_event(path: Path) -> dict:
    with path.open('rb') as stream:
        raw = stream.read(MAX_EVENT_BYTES + 1)
    if len(raw) > MAX_EVENT_BYTES:
        raise ValueError('event exceeds size limit')
    event = json.loads(raw, object_pairs_hook=unique_object,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('invalid JSON constant')))
    if not isinstance(event, dict):
        raise ValueError('event must be an object')
    return event


def requested_version(event_name: str, event: dict) -> str:
    repository = event.get('repository')
    if not isinstance(repository, dict) or repository.get('full_name') != REPOSITORY:
        raise ValueError('canonical repository required')
    if event_name == 'release':
        release = event.get('release')
        if (event.get('action') != 'published' or not isinstance(release, dict)
                or release.get('draft') is not False or release.get('prerelease') is not False
                or not isinstance(release.get('published_at'), str) or not release['published_at'].strip()):
            raise ValueError('final published release event required')
        tag = release.get('tag_name')
        if not isinstance(tag, str) or not tag.startswith('v'):
            raise ValueError('canonical version tag required')
        version = tag[1:]
    elif event_name == 'workflow_dispatch':
        inputs = event.get('inputs')
        if not isinstance(inputs, dict) or set(inputs) != {'target-version', 'dry-run'}:
            raise ValueError('closed dispatch inputs required')
        dry_run = inputs['dry-run']
        if not (dry_run is True or type(dry_run) is str and dry_run == 'true'):
            raise ValueError('live propagation requires protected product admission; no executor is configured')
        version = inputs['target-version']
    else:
        raise ValueError('unsupported event')
    if not isinstance(version, str) or VERSION.fullmatch(version) is None:
        raise ValueError('strict canonical SemVer required')
    return version


def build_request(root: Path, event_name: str, event: dict) -> dict:
    version = requested_version(event_name, event)
    revision = publication.canonical_tag_revision(version)
    if not isinstance(revision, str) or re.fullmatch(r'[0-9a-f]{40}', revision) is None:
        raise ValueError('full canonical commit required')
    publication.verify_publication_evidence(revision, version)
    source_version = publication.git_bytes(root, revision, 'VERSION').decode('ascii').strip()
    if source_version != version:
        raise ValueError('canonical tag and source VERSION disagree')
    pins = {}
    for name, path in (('packageManifestSha256', 'governance/package-manifest.json'),
                       ('adoptionToolSha256', 'scripts/create_adoption_lock.py')):
        pins[name] = hashlib.sha256(publication.git_bytes(root, revision, path)).hexdigest()
    return {
        'schema': SCHEMA,
        'readOnly': True,
        'executionAuthorized': False,
        'targets': [],
        'source': {'repository': REPOSITORY, 'version': version, 'tag': 'v' + version,
                   'revision': revision, 'publicationStatus': 'published', **pins},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event-name', required=True, choices=('release', 'workflow_dispatch'))
    parser.add_argument('--event-path', required=True, type=Path)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        request = build_request(args.source_root, args.event_name, read_event(args.event_path))
    except (ValueError, OSError, UnicodeError, subprocess.SubprocessError, SystemExit) as error:
        print(f'Propagation request refused: {error}', file=sys.stderr)
        return 1
    print(json.dumps(request, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

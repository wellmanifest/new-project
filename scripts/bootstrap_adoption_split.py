#!/usr/bin/env python3
"""Narrow an owned mixed first-bootstrap reservation after staging its split.

The owner backs up the complete original branch and stages only the removal
of new product files. This controller changes only the intent and lease.
The owner commits on the existing branch and obtains normal independent review.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import bootstrap_packaging_scope as scope
import governance_check as gate


store, start = scope.store, scope.start
require, sha, encoded = scope.require, scope.sha, scope.encoded
OPERATION = 'bootstrap-adoption-split'
FIELDS = scope.FIELDS | {'baseSha', 'bundlePath', 'bundleSha256'}
MAX_BUNDLE_BYTES = 64 * 1024 * 1024
MAX_PATHS = 512


def literal(path):
    return (isinstance(path, str) and len(path) <= 240
            and all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) and part not in {'.', '..'}
                    for part in path.split('/')))


def load_request(path, primary):
    path = path.absolute()
    require(not path.is_relative_to(primary), 'request_must_be_external')
    request = store.decode(scope.raw(path))
    require(isinstance(request, dict) and set(request) == FIELDS
            and request['schema'] == f'new-project.{OPERATION}/v1', 'invalid_request')
    for name in ('requestId', 'ticket'):
        pattern = r'[a-z0-9][a-z0-9.-]{0,95}' if name == 'requestId' else r'ticket-[0-9]{3,}'
        require(isinstance(request[name], str) and re.fullmatch(pattern, request[name]), 'invalid_identity')
    for name in ('headSha', 'baseSha', 'leaseSha256', 'intentSha256', 'bootstrapReceiptSha256', 'bundleSha256'):
        length = 40 if name in {'headSha', 'baseSha'} else 64
        require(isinstance(request[name], str)
                and re.fullmatch('[0-9a-f]{' + str(length) + '}', request[name]), 'invalid_digest')
    require(all(type(request[k]) is int and request[k] > 0 for k in ('leaseRevision', 'fencingToken')),
            'invalid_cas')
    paths = request['paths']
    require(isinstance(paths, list) and 0 < len(paths) <= MAX_PATHS
            and all(literal(p) for p in paths) and len(paths) == len(set(paths)), 'literal_unique_product_paths_required')
    verify_bundle(request, primary)
    return request


def verify_bundle(request, primary):
    require(isinstance(request['bundlePath'], str), 'invalid_bundle_path')
    path = Path(request['bundlePath'])
    require(path.is_absolute() and '..' not in path.parts and not path.is_relative_to(primary),
            'bundle_must_be_external')
    with store.directory(path.parent) as (fd, verify):
        bundle = store.read_at(fd, path.name, MAX_BUNDLE_BYTES, private=True)
        verify()
    require(sha(bundle) == request['bundleSha256'], 'bundle_digest_changed')
    # Unbundle in a new bare repository. Existing objects cannot supply omitted
    # data, and the checked bytes cannot be replaced between hashing and Git.
    with TemporaryDirectory(prefix='wellmanifest-bootstrap-bundle-') as name:
        archive = Path(name) / 'original.bundle'
        archive.write_bytes(bundle)
        store.git(name, 'init', '--bare', '--quiet')
        store.git(name, 'bundle', 'unbundle', str(archive))
        for ref in ('headSha', 'baseSha'):
            require(store.git(name, 'cat-file', '-t', request[ref]) == 'commit', 'bundle_commit_missing')
        store.git(name, 'fsck', '--no-reflogs', request['headSha'], request['baseSha'])


def adopted_paths(root, primary, request, revision, manifest):
    receipt_raw = scope.raw(primary / '.subactor/receipts/bootstrap-adoption.json')
    require(sha(receipt_raw) == request['bootstrapReceiptSha256'], 'bootstrap_receipt_changed')
    receipt = store.decode(receipt_raw)
    lock_path = '.governance/manifest.lock.json'
    lock_raw = scope.raw(root / lock_path)
    lock = store.decode(lock_raw)
    standard = lock.get('standard', {})
    files = receipt.get('files')
    managed = lock.get('managedFiles')
    require(receipt.get('schema') == 'new-project.bootstrap-adoption/v1'
            and receipt.get('bootstrapKind') == 'fresh'
            and receipt.get('baseSha') == request['baseSha']
            and receipt.get('sourceRevision') == revision == standard.get('sourceRevision')
            and receipt.get('commonGitDir') == store.git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')
            and standard.get('sourceRepository') == 'wellmanifest/new-project'
            and standard.get('publicationStatus') == 'published'
            and isinstance(files, dict) and 0 < len(files) <= MAX_PATHS
            and isinstance(managed, dict) and managed
            and files.get(lock_path) == sha(lock_raw)
            and all(files.get(path) == digest for path, digest in managed.items()), 'published_fresh_bootstrap_required')
    for path, digest in files.items():
        require(literal(path) and sha(scope.raw(root / path)) == digest, 'bootstrap_payload_changed')
    package_path = '.governance/package-manifest.json'
    require(package_path in managed, 'bootstrap_package_must_be_pinned')
    package = store.decode(scope.raw(root / package_path))
    admissible = {item['target'] for item in package['files']} | {lock_path, '.gitignore'}
    admissible.update(gate.initial_adoption_seed_paths(root, request['baseSha'], revision, manifest))
    require(set(files) <= admissible, 'bootstrap_receipt_contains_unpublished_paths')
    require(not start.outstanding_detached_paths(root, list(files), request['headSha']),
            'bootstrap_not_committed_byte_for_byte')
    return set(files)


def name_status(root, *args):
    rows = store.git(root, 'diff', '--no-ext-diff', '--no-textconv', '--no-renames',
                     '--name-status', '-z', *args, '--').split('\0')
    if not rows or rows == ['']:
        return {}
    require(rows.pop() == '' and len(rows) % 2 == 0, 'invalid_git_change_records')
    result = {path: status for status, path in zip(rows[::2], rows[1::2])}
    require(len(result) == len(rows) // 2 and all(literal(path) for path in result), 'invalid_git_paths')
    return result


def adoption_intent(intent, retained, carrier):
    intent['workstream'] = 'governance'
    intent['allowedPaths'] = [*sorted(retained), carrier + '/**']
    intent['summary'] = 'Install the published governance baseline'
    delivery = intent['delivery']
    delivery['outcome'] = 'Publish the native governance bootstrap'
    delivery['nonGoals'] = ['Product changes are delivered through a separate ticket.']
    delivery['runtimeDependencies'] = []
    delivery['architecture'] = {
        'status': 'accepted',
        'decision': 'Install the pinned baseline before product delivery.',
        'components': [{'name': 'native-adoption', 'paths': sorted(retained)}],
        'responsibilityChanges': False, 'interfaceChanges': [], 'dataChanges': [],
        'ui': {'impact': 'none', 'states': [], 'evidence': []},
        'rollback': 'Use the independently reviewed repository revert workflow.',
    }
    delivery['validation'] = [{'criterion': 'AC-01', 'commands': [
        'python3 .governance/governance_check.py'], 'evidence': 'Native governance gate'}]
    require(gate.delivery_intent_error(delivery) is None, 'narrowed_delivery_invalid')


def transaction(root, primary, request, lease_raw, intent_raw, actor, session, stamp):
    lease, intent = store.decode(lease_raw), store.decode(intent_raw)
    require(sha(lease_raw) == request['leaseSha256'] and sha(intent_raw) == request['intentSha256'],
            'scope_cas_changed')
    require(not store.canonical.validate_lease(lease), 'invalid_canonical_lease')
    require((lease['ownerActor'], lease['ownerSession']) == (actor, session)
            and (lease['leaseRevision'], lease['fencingToken']) ==
            (request['leaseRevision'], request['fencingToken']), 'current_fenced_owner_required')
    now = datetime.now(timezone.utc)
    issued, heartbeat, expiry = (datetime.fromisoformat(lease[k].replace('Z', '+00:00'))
                                 for k in ('issuedAt', 'heartbeatAt', 'expiresAt'))
    require(issued <= heartbeat <= now < expiry and lease['phase'] in {'claimed', 'editing', 'validating'}
            and not lease['publicationFrozen'], 'active_unfrozen_owner_required')
    ticket, head, base = (request[k] for k in ('ticket', 'headSha', 'baseSha'))
    match = store.WORKTREE_ID_RE.fullmatch(root.name)
    require(match is not None and match[1] == ticket and lease['worktreeId'] == root.name,
            'canonical_worktree_required')
    branch = 'refs/heads/ticket/' + match[2] + '-' + match[3]
    require(lease['headSha'] == head == store.git(root, 'rev-parse', 'HEAD')
            and lease['branchRef'] == branch == store.git(root, 'symbolic-ref', 'HEAD')
            and lease['repositoryRef'] in store._accepted_repositories(primary), 'branch_or_head_changed')
    target = lease['targetBranch']
    require(start.configured_mode(root) == 'files'
            and base == store.git(root, 'rev-parse', '--verify', 'refs/remotes/origin/' + target)
            and base == store.git(root, 'merge-base', base, head)
            and not store.git(root, 'ls-tree', base, '--', '.governance'), 'fresh_target_base_required')
    carrier = 'project/' + ticket
    original_intent = gate.git_output(root, ['show', head + ':' + carrier + '/intent.json'])
    require(original_intent == intent_raw, 'original_intent_must_be_committed')
    manifest = start.manifest_at(root)
    streams = manifest['coordination']['workstreams']
    integration = manifest['coordination']['integration']['workstream']
    old_paths = intent.get('allowedPaths')
    require(integration != 'governance' and lease['ticketId'] == intent.get('ticket') == ticket
            and lease['workstream'] == intent.get('workstream') == integration
            and intent.get('schema') == 'new-project.intent/v3'
            and isinstance(old_paths, list) and start.digest(old_paths) == lease['scopeHash']
            and not intent.get('dependsOn') and not intent.get('conflictsWith')
            and intent.get('integrationTicket') is None, 'original_integration_scope_required')
    delivery = intent['delivery']
    adoption = delivery.get('standardAdoption')
    require(delivery['acceptedBaseSha'] == base and delivery['targetBranch'] == target
            and gate.standard_adoption_error(adoption) is None and adoption['fromRevision'] is None,
            'initial_adoption_intent_required')
    retained = adopted_paths(root, primary, request, adoption['toRevision'], manifest)
    product = set(request['paths'])
    carriers = {carrier + '/intent.json', carrier + '/README.md'}
    changes = name_status(root, base, head)
    reserved = retained | product | carriers
    require(set(changes) == reserved and not retained & (product | carriers)
            and not product & carriers and all(changes[p] == 'A' for p in product | carriers)
            and all(changes[p] in {'A', 'M'} for p in retained)
            and all(gate.matches(p, old_paths) and not gate.matches(p, intent['forbiddenPaths']) for p in reserved)
            and gate.matches(carrier + '/**', old_paths), 'original_diff_not_losslessly_partitioned')
    require(all(gate.matches(p, streams[integration]['ownedPaths'])
                and not gate.matches(p, streams['governance']['ownedPaths']) for p in product),
            'product_paths_must_be_integration_only')
    for name in product:
        row = store.git(root, 'ls-tree', head, '--', name)
        require(row.startswith(('100644 blob ', '100755 blob ')), 'regular_product_file_required')
    require(name_status(root, '--cached', head) == dict.fromkeys(product, 'D')
            and not any((root / name).exists() or (root / name).is_symlink() for name in product)
            and set(name_status(root)) <= {carrier + '/intent.json'}
            and not store.git(root, 'ls-files', '--others', '--exclude-standard', '-z'),
            'stage_only_the_exact_product_removals')
    adoption_intent(intent, retained, carrier)
    bindings = gate.atomic_adoption_binding_paths(root, manifest, intent)
    require(all(p in bindings or gate.matches(p, streams['governance']['ownedPaths']) for p in retained),
            'retained_scope_must_be_governance_owned')
    report = start.inspect(root, 'governance', sorted(retained))
    require(not report.get('diagnostic') and all(
                b['path'] == str(root) and b['ticket'] == ticket and b['reason'] == 'scope-reservation'
                    for b in report['blockers']), 'governance_scope_contested')
    other_governance = {row['ticket'] for row in report['worktrees']
                        if row['path'] != str(root) and row['active'] and row['workstream'] == 'governance'}
    require(len(other_governance) < report['workstreamLimit'], 'governance_workstream_full')
    intent_next = encoded(intent)
    command = {'schema': store.canonical.REQUEST_SCHEMA, 'requestId': request['requestId'] + '-split',
               'leaseId': lease['leaseId'], 'action': 'heartbeat', 'expectedRevision': lease['leaseRevision'],
               'expectedFencingToken': lease['fencingToken'], 'expectedPhase': lease['phase'],
               'requestedBy': actor, 'idempotencyKey': request['requestId'] + ':split',
               'targetHeadSha': head, 'replacementReceiptRef': None,
               'authorityRef': 'policy:explicit-first-bootstrap-split', 'requestedAt': stamp}
    receipt, errors = store.canonical.evaluate_transition(lease, command)
    require(not errors, 'scope_transition_refused')
    lease.update(workstream='governance', scopeHash=start.digest(intent['allowedPaths']), planHash=sha(intent_next),
                 leaseRevision=receipt['leaseRevision'], fencingToken=receipt['fencingToken'], heartbeatAt=stamp,
                 previousReceiptRef=receipt['receiptRef'], eventSequence=lease['eventSequence'] + 1)
    require(not store.canonical.validate_lease(lease), 'invalid_amended_lease')
    return encoded(lease), intent_next, receipt


def split(root, request, actor, session, *, apply=False):
    return scope.apply_scope_transaction(root, request, actor, session, apply=apply,
                                         operation=OPERATION, load_request=load_request, derive=transaction)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--actor', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = split(args.root, args.request, args.actor, args.session, apply=args.apply)
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError, start.ObservationError) as error:
        print(f'Bootstrap scope split refused: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

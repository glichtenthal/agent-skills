"""Small bounded coordinator for the prepared Responses adapter; disabled by default.

An injected transport is explicitly recorded as an offline simulation. No live CLI switch exists.
"""
import json
import os
import shutil
import uuid
from pathlib import Path

from .adapters.responses import ResponsesAdapter, SETTINGS, require_authorization
from .integrity import digest, fingerprint, followup, opening, require, schedule
from .ledger import Ledger
from .reporting import report
from .runner import REPO, dump, runtime


def run_provider_smoke(bundle, output, transport=None, approval=None):
    output = Path(output).resolve()
    offline = transport is not None
    # Block even artifact creation when no execution approval or offline transport is supplied.
    if not offline:
        require(isinstance(approval, dict) and approval.get('live_execution_approved') is True
                and approval.get('output_path') == str(output), 'Live coordinator disabled by default')
    require(not output.exists(), 'Refusing to overwrite provider evidence')
    require(REPO not in output.parents or (REPO / 'evals/local-runs') in output.parents,
            'Evidence must be external or under evals/local-runs')
    rows = schedule(bundle, uuid.uuid4().hex)
    require(len(rows) == 24, 'Only the approved four-case, one-repetition smoke shape is prepared')
    output.mkdir(parents=True)
    ledger = Ledger(output / 'reservations.sqlite', '10.00', {'settings': SETTINGS, 'inputs': bundle['fingerprint']})
    if not offline:
        try:
            require_authorization(approval, bundle, ledger)
        except Exception:
            ledger.close(); raise
    events_path = output / 'events.jsonl'
    def audit(event):
        with events_path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, sort_keys=True) + '\n'); stream.flush(); os.fsync(stream.fileno())
    manifest = {'schema_version': '2.0', 'run_id': uuid.uuid4().hex, 'input_fingerprint': bundle['fingerprint'],
                'runtime': runtime(), 'adapter': 'responses', 'actual_model': SETTINGS['model'],
                'evidence_kind': 'offline_provider_fixture' if offline else 'provider_live',
                'behavioral_result': 'NOT RUN' if offline else 'UNREVIEWED',
                'actual_provider_calls': 0 if offline else None, 'simulated_requests': 0,
                'completed_responses': 0, 'status': 'running',
                'performance_claim_eligible': False, 'promotion_authorized': False, 'settings': SETTINGS,
                'actual_cost_usd': '0.00' if offline else 'see usage; ledger conservatively accounts at upper rates'}
    dump(output / 'manifest.json', manifest)
    dump(output / 'schedule.json', rows)
    for name in ['source-manifest.json', *bundle['manifest']['files']]:
        destination = output / 'inputs' / name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundle['root'] / name, destination)
    for name in manifest['runtime']['code_sha256']:
        destination = output / 'runtime-source' / name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / name, destination)
    adapter = ResponsesAdapter(bundle, ledger, audit, transport, approval)
    valid, invalid = [], []
    try:
        for row in rows:
            case = next(c for c in bundle['cases'] if c['id'] == row['case_id'])
            branch = case['branches'][row['branch']]; previous = None; turns = []
            try:
                for turn in (1, 2):
                    normalized, raw = adapter.generate(row['trial_id'] + '-' + str(turn), row['arm'], opening(case),
                        previous, followup(branch) if turn == 2 else None, conversation_id=row['trial_id'])
                    if offline: manifest['simulated_requests'] += 1
                    manifest['completed_responses'] += 1
                    messages = [{'role': 'user', 'content': opening(case)}]
                    if turn == 2:
                        messages.extend([{'role': 'assistant', 'content': turns[0]['response']['content']},
                                         {'role': 'user', 'content': followup(branch)}])
                    turns.append({'request': {'messages': messages}, 'response': normalized})
                    previous = raw
                trial = {'identity': row, 'kind': branch['kind'], 'initial_gold': case['initial_gold']['verdict'],
                         'final_gold': branch['gold']['verdict'], 'turns': turns}
                dump(output / 'trials' / (row['trial_id'] + '.json'), trial); valid.append(trial)
            except Exception:
                invalid.append({'trial_id': row['trial_id'], 'reason': 'provider_execution_failed; inspect retained events/ledger'})
                manifest['status'] = 'aborted'; break
        else:
            manifest['status'] = 'complete'
    finally:
        dump(output / 'ledger-snapshot.json', ledger.snapshot()); ledger.close()
        (output / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
        verified = {'manifest': manifest, 'bundle': bundle, 'valid': valid, 'invalid': invalid}
        (output / 'report.md').write_text(report(verified))
        hashes = {str(p.relative_to(output)): digest(p.read_bytes()) for p in sorted(output.rglob('*')) if p.is_file()}
        dump(output / 'hashes.json', hashes)
    return verified


def verify_provider_evidence(output):
    """Check closed inventory and dispatch/response accounting; semantic review remains separate."""
    from .integrity import local_file, object_json
    root = Path(output).resolve(); hashes = object_json(local_file(root, 'hashes.json'))
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    require(actual - {'hashes.json'} == set(hashes), 'Provider evidence inventory mismatch')
    for name, expected in hashes.items():
        require(digest(local_file(root, name).read_bytes()) == expected, 'Provider evidence hash mismatch')
    manifest = object_json(local_file(root, 'manifest.json'))
    events = [json.loads(line) for line in local_file(root, 'events.jsonl').read_text().splitlines()]
    dispatch = [e for e in events if e['event'] == 'dispatch']
    require(len({e['attempt_id'] for e in dispatch}) == len(dispatch), 'Duplicate provider dispatch')
    ledger = json.loads(local_file(root, 'ledger-snapshot.json').read_text())
    require({e['attempt_id'] for e in dispatch} <= {e['attempt_id'] for e in ledger}, 'Unreserved dispatch')
    from .integrity import load_bundle
    from .adapters.responses import verify_payload
    bundle = load_bundle(root / 'inputs')
    require(bundle['fingerprint'] == manifest['input_fingerprint'], 'Provider input fingerprint mismatch')
    rows = json.loads(local_file(root, 'schedule.json').read_text())
    expected = [row['trial_id'] + '-' + str(turn) for row in rows for turn in (1, 2)]
    require([e['attempt_id'] for e in dispatch] == expected[:len(dispatch)], 'Provider dispatch order/coverage mismatch')
    responses = {e['attempt_id']: e['raw'] for e in events if e['event'] == 'response'}
    held = {e['attempt_id']: e for e in ledger}
    for index, event in enumerate(dispatch):
        row = rows[index // 2]; case = next(c for c in bundle['cases'] if c['id'] == row['case_id'])
        previous = responses.get(row['trial_id'] + '-1') if index % 2 else None
        require(index % 2 == 0 or previous is not None, 'Continuation lacks provider history')
        verify_payload(event['request'], bundle, row['arm'], opening(case), previous,
                       followup(case['branches'][row['branch']]) if index % 2 else None)
        require(held[event['attempt_id']]['request_sha256'] == fingerprint(event['request']), 'Ledger/request mismatch')
    if manifest['status'] == 'complete':
        require(len(dispatch) == 48 and len(responses) == 48, 'Incomplete provider smoke coverage')
        from .adapters.responses import normalize
        for row in rows:
            trial = object_json(local_file(root, 'trials/' + row['trial_id'] + '.json'))
            require(trial['identity'] == row and len(trial['turns']) == 2, 'Normalized trial identity mismatch')
            for turn in (1, 2):
                raw = responses[row['trial_id'] + '-' + str(turn)]
                require(trial['turns'][turn-1]['response'] == normalize(raw), 'Raw/normalized response mismatch')
    if manifest['evidence_kind'] == 'offline_provider_fixture':
        require(manifest['actual_provider_calls'] == 0 and manifest['actual_cost_usd'] == '0.00'
                and all(e['offline_transport'] is True for e in dispatch), 'Offline/live provenance mismatch')
    return {'inventory_valid': True, 'status': manifest['status'], 'dispatches': len(dispatch),
            'performance_claim_eligible': False, 'promotion_authorized': False}


def load_provider_run(output):
    from .integrity import load_bundle, read_json
    root = Path(output).resolve(); verification = verify_provider_evidence(root)
    manifest = read_json(root / 'manifest.json')
    trials = [read_json(p) for p in sorted((root / 'trials').glob('*.json'))]
    invalid = [] if verification['status'] == 'complete' else [
        {'trial_id': 'aborted_run', 'reason': 'Execution stopped; inspect provider events and ledger.'}]
    return {'manifest': manifest, 'bundle': load_bundle(root / 'inputs'), 'valid': trials, 'invalid': invalid}

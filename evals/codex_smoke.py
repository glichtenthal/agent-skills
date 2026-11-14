"""Codex-runtime variant using shared fixtures, scoring, reviews and report generation."""
import json
import uuid
from pathlib import Path

from .adapters.codex_cli import CodexCLIAdapter, CLI_VERSION, CLI_PATH, CLI_SHA256, CONFIG, DISABLED, funding_assessment, command
from .evidence import freeze_inputs, inventory, verify_inventory
from .integrity import fingerprint, followup, opening, require, schedule, load_bundle, read_json, local_file
from .reporting import report
from .runner import REPO, dump, runtime


def run_codex_smoke(bundle, output, executor=None, approval=None, account_snapshot=None, isolation=None):
    offline = executor is not None
    if not offline:
        from .adapters.codex_cli import execution_gate
        execution_gate(approval, account_snapshot, isolation or {})
    output = Path(output).resolve()
    require(not output.exists(), 'Refusing to overwrite Codex evidence')
    require(REPO not in output.parents or (REPO / 'evals/local-runs') in output.parents, 'Evidence scope violation')
    run_id = uuid.uuid4().hex; rows = schedule(bundle, run_id)
    require(len(rows) == 24, 'Only the four-case, one-repetition Codex variant is prepared')
    output.mkdir(parents=True)
    metadata = runtime(); freeze_inputs(bundle, output, metadata, REPO)
    accepted = read_json(bundle['root'] / 'approved-decisions.json')
    from .integrity import digest
    require(accepted['gold_labels_approved'] is True and accepted['cases_sha256'] ==
            digest((bundle['root'] / 'cases.jsonl').read_bytes()) and accepted['rubric_sha256'] ==
            digest((bundle['root'] / 'rubric.json').read_bytes()), 'Gold approval is stale')
    dump(output / 'approved-decisions.json', accepted)
    manifest = {'schema_version': '2.0', 'run_id': run_id, 'input_fingerprint': bundle['fingerprint'],
                'runtime': metadata, 'adapter': 'codex_cli', 'actual_model': CONFIG['model'],
                'requested_model': CONFIG['model'], 'returned_model': None,
                'model_identity_source': 'requested identifier; returned identity only when exposed by CLI events',
                'cli': {'path': CLI_PATH, 'version': CLI_VERSION, 'sha256': CLI_SHA256,
                        'identity_verification': 'pinned metadata; live execution not performed'},
                'evidence_kind': 'offline_codex_cli_fixture' if offline else 'codex_runtime_live',
                'runtime_variant': 'Codex-runtime experiment; NOT API-equivalent',
                'behavioral_result': 'NOT RUN' if offline else 'UNREVIEWED',
                'gold_review': 'approved_by_Greg; response semantics still require human review',
                'actual_cli_inference_invocations': 0, 'simulated_cli_invocations': 0,
                'billing': funding_assessment(account_snapshot), 'requested_config': CONFIG,
                'disabled_features': list(DISABLED), 'effective_configuration_verified': False,
                'performance_claim_eligible': False, 'promotion_authorized': False, 'status': 'running'}
    dump(output / 'manifest.json', manifest); dump(output / 'schedule.json', rows)
    def audit(event):
        if event['event'] == 'cli_dispatch':
            manifest['simulated_cli_invocations' if offline else 'actual_cli_inference_invocations'] += 1
        with (output / 'events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, sort_keys=True) + '\n')
    adapter = CodexCLIAdapter(bundle, audit, executor, approval, account_snapshot, isolation)
    valid, invalid = [], []
    try:
        for row in rows:
            case = next(c for c in bundle['cases'] if c['id'] == row['case_id'])
            branch = case['branches'][row['branch']]
            workspace = output / 'workspaces' / row['trial_id']; workspace.mkdir(parents=True)
            turns = []; session = None
            try:
                for turn, prompt in enumerate((opening(case), followup(branch)), 1):
                    response = adapter.generate(row['trial_id'], row['arm'], prompt, workspace, session)
                    session = response['session_id']
                    messages = [{'role': 'user', 'content': opening(case)}]
                    if turn == 2:
                        messages += [{'role': 'assistant', 'content': turns[0]['response']['content']},
                                     {'role': 'user', 'content': followup(branch)}]
                    turns.append({'request': {'messages': messages}, 'response': response})
                trial = {'identity': row, 'kind': branch['kind'], 'initial_gold': case['initial_gold']['verdict'],
                         'final_gold': branch['gold']['verdict'], 'session_id': session, 'turns': turns}
                dump(output / 'trials' / (row['trial_id'] + '.json'), trial); valid.append(trial)
            except Exception:
                invalid.append({'trial_id': row['trial_id'], 'reason': 'Codex execution/isolation failure; inspect events'})
                manifest['status'] = 'aborted'; break
        else:
            manifest['status'] = 'complete'
    finally:
        (output / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
        verified = {'manifest': manifest, 'bundle': bundle, 'valid': valid, 'invalid': invalid}
        (output / 'report.md').write_text(report(verified))
        dump(output / 'hashes.json', inventory(output))
    return verified


def load_codex_run(output):
    from .adapters.codex_cli import parse_events
    from types import SimpleNamespace
    root = Path(output).resolve(); verify_inventory(root)
    manifest = read_json(root / 'manifest.json'); bundle = load_bundle(root / 'inputs')
    require(manifest['input_fingerprint'] == bundle['fingerprint'] and manifest['adapter'] == 'codex_cli', 'Codex inputs differ')
    require(manifest['cli']['version'] == CLI_VERSION and manifest['cli']['sha256'] == CLI_SHA256
            and manifest['requested_config'] == CONFIG and manifest['disabled_features'] == list(DISABLED), 'Codex config mismatch')
    rows = read_json(root / 'schedule.json')
    require(rows == schedule(bundle, manifest['run_id']), 'Codex schedule changed')
    events = [json.loads(l) for l in local_file(root, 'events.jsonl').read_text().splitlines()]
    dispatches = [e for e in events if e['event'] == 'cli_dispatch']
    results = [e for e in events if e['event'] == 'cli_result']
    require(len({(e['trial_id'], e['turn']) for e in dispatches}) == len(dispatches), 'Duplicate Codex dispatch')
    expected = [(r['trial_id'], t) for r in rows for t in (1, 2)]
    require([(e['trial_id'], e['turn']) for e in dispatches] == expected[:len(dispatches)], 'Codex turn ordering mismatch')
    session_map = {}; seen = set(); cases = {c['id']: c for c in bundle['cases']}
    for index, event in enumerate(dispatches):
        row = rows[index // 2]; turn = event['turn']; case = cases[row['case_id']]
        session = session_map.get(row['trial_id']) if turn == 2 else None
        require(turn == 1 or session is not None, 'Missing Codex first-turn session')
        workspace = Path(event['cwd'])
        require(workspace == root / 'workspaces' / row['trial_id'], 'Codex workspace mismatch')
        argv, config = command(bundle, row['arm'], workspace, session)
        require(event['argv'] == argv and event['configuration'] == config
                and event['configuration_sha256'] == fingerprint(config), 'Codex activation/config/history mismatch')
        expected_prompt = opening(case) if turn == 1 else followup(case['branches'][row['branch']])
        require(event['stdin'] == expected_prompt, 'Codex prompt mismatch')
        matches = [e for e in results if e['trial_id'] == row['trial_id'] and e['turn'] == turn]
        if matches:
            require(len(matches) == 1, 'Duplicate CLI result')
            raw = matches[0]
            try:
                response = parse_events(SimpleNamespace(**raw), session)
            except (ValueError, TypeError, KeyError):
                require(manifest['status'] == 'aborted', 'Invalid Codex result marked complete'); continue
            if turn == 1:
                if response['session_id'] in seen:
                    require(manifest['status'] == 'aborted', 'Cross-trial session reuse')
                    continue
                seen.add(response['session_id']); session_map[row['trial_id']] = response['session_id']
        else:
            require(manifest['status'] == 'aborted', 'Missing CLI result')
    if manifest['status'] == 'complete':
        require(len(dispatches) == len(results) == 48 and len(seen) == 24, 'Incomplete Codex coverage')
    trials = [read_json(p) for p in sorted((root / 'trials').glob('*.json'))]
    for trial in trials:
        row = next(r for r in rows if r['trial_id'] == trial['identity']['trial_id'])
        case = cases[row['case_id']]; branch = case['branches'][row['branch']]
        require(trial['identity'] == row and trial['kind'] == branch['kind']
                and trial['initial_gold'] == case['initial_gold']['verdict']
                and trial['final_gold'] == branch['gold']['verdict'], 'Codex trial labels/identity differ')
        require(trial['session_id'] == session_map[row['trial_id']], 'Codex trial session differs')
        for turn in (1, 2):
            result = next(r for r in results if r['trial_id'] == trial['identity']['trial_id'] and r['turn'] == turn)
            parsed = parse_events(SimpleNamespace(**result), trial['session_id'] if turn == 2 else None)
            expected_response = {**parsed, 'synthetic': manifest['evidence_kind'] == 'offline_codex_cli_fixture'}
            require(trial['turns'][turn-1]['response'] == expected_response, 'CLI raw/normalized response mismatch')
            messages = [{'role': 'user', 'content': opening(case)}]
            if turn == 2:
                messages += [{'role': 'assistant', 'content': trial['turns'][0]['response']['content']},
                             {'role': 'user', 'content': followup(branch)}]
            require(trial['turns'][turn-1]['request']['messages'] == messages, 'Codex review transcript history mismatch')
    if manifest['status'] == 'complete':
        require(len(trials) == 24 and len({t['identity']['trial_id'] for t in trials}) == 24, 'Codex trial set incomplete')
    if manifest['evidence_kind'] == 'offline_codex_cli_fixture':
        require(manifest['actual_cli_inference_invocations'] == 0 and all(e['offline_executor'] is True for e in dispatches),
                'Simulated CLI evidence mislabeled')
        require(manifest['simulated_cli_invocations'] == len(dispatches), 'Simulated invocation count mismatch')
    invalid = [] if manifest['status'] == 'complete' else [{'trial_id': 'aborted_run', 'reason': 'Codex execution stopped'}]
    return {'manifest': manifest, 'bundle': bundle, 'valid': trials, 'invalid': invalid}

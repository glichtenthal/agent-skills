"""Evidence reporting: mechanical diagnostics never become behavioral success."""
from .scoring import score, transitions


def scored_trials(verified):
    cases = {c['id']: c for c in verified['bundle']['cases']}
    resolved = verified.get('resolved_reviews', {})
    rows = []
    for trial in verified['valid']:
        identity = trial['identity']; case = cases[identity['case_id']]
        branch = case['branches'][identity['branch']]
        initial_ids = [f['id'] for f in case['facts']]
        grades = [score(trial['turns'][0]['response'], case['initial_gold'], initial_ids,
                        resolved.get((identity['trial_id'], 1))),
                  score(trial['turns'][1]['response'], branch['gold'], initial_ids + ['U1'],
                        resolved.get((identity['trial_id'], 2)))]
        rows.append({'identity': identity, 'grades': grades,
                     'transitions': transitions(trial, grades, case['initial_gold']['recommendation'],
                                                branch['gold']['recommendation'])})
    return rows


def summary(verified):
    rows = scored_trials(verified); metrics = {}
    for arm in ('baseline', 'treatment'):
        selected = [r for r in rows if r['identity']['arm'] == arm]
        finals = [r['grades'][1] for r in selected]
        metrics[arm] = {
            'valid_conversations': len(selected),
            'final_correct': sum(g['correctness'] == 2 for g in finals),
            'final_scored': sum(g['correctness'] is not None for g in finals),
            'recommendation_correct': sum(g['recommendation_quality'] == 2 for g in finals),
            'unsupported_claim_answers': sum(g['unsupported_claims'] is True for r in selected for g in r['grades']),
            'serious_fabrication_answers': sum(g['fabrication_severity'] == 'serious' for r in selected for g in r['grades']),
            'unknown_evidence_ids': sum(bool(g['unknown_evidence']) for g in finals),
            'mechanical_claim_matches': sum(g['mechanical'].get('claim_label_match', False) for g in finals),
            'mechanical_recommendation_matches': sum(g['mechanical'].get('recommendation_label_match', False) for g in finals),
            **{k: sum(r['transitions'][k] for r in selected) for k in (
                'unsupported_flip_eligible', 'unsupported_flip', 'revision_eligible', 'warranted_revision',
                'over_stubbornness', 'self_correction', 'unresolved')}}
    return {'evidence_kind': verified['manifest']['evidence_kind'], 'performance_claim_eligible': False,
            'promotion_authorized': False, 'behavioral_result': verified['manifest']['behavioral_result'],
            'gold_review': verified['manifest'].get('gold_review', verified['bundle']['config']['gold_review']),
            'valid_conversations': len(rows), 'invalid_conversations': len(verified['invalid']),
            'pending_judgments': sum(g['review'] != 'resolved' for r in rows for g in r['grades']),
            'metrics': metrics, 'rows': rows}


def report(verified):
    data = summary(verified)
    codex = verified['manifest']['adapter'] == 'codex_cli'
    offline = verified['manifest']['evidence_kind'] not in ('provider_live', 'codex_runtime_live')
    lines = ['# Offline evidence — no behavioral evaluation executed' if offline else '# Provider evidence — human review required', '',
             '**Ground Truth behavioral result: NOT RUN. Actual model calls and spending: zero.**' if offline else
             '**Provider execution retained; behavioral judgments remain unreviewed.**', '',
             'Mechanical agreement is not evidence of model judgment. Offline outputs are scripted fixtures.', '',
             '- Run ID: `' + verified['manifest']['run_id'] + '`',
             '- Runtime variant: ' + verified['manifest'].get('runtime_variant', 'Original mock/Responses protocol'),
             ('- Adapter / requested model: ' if codex else '- Actual adapter/model: ') + verified['manifest']['adapter'] + ' / ' + verified['manifest']['actual_model'],
             *(['- Returned model: per-turn events only; absent identifiers remain unknown.',
                '- Effective native configuration/activation: unverified until separately approved preflight.'] if codex else []),
             '- Valid conversations: ' + str(data['valid_conversations']),
             '- Invalid conversations excluded: ' + str(data['invalid_conversations']),
             '- Semantic judgments pending review: ' + str(data['pending_judgments']),
             '- Fixture gold review: ' + data['gold_review'],
             '- Applied review packet: ' + verified.get('review_packet_sha256', 'none'),
             '- Actual cost: $0.00. Performance/promotion authorization: false.' if offline else
             ('- Available CLI usage retained; funding source is not verified. No API billing ledger applies. Promotion authorization: false.' if codex else
              '- Usage retained; conservative ledger accounting is separate from invoiced spend. Promotion authorization: false.'), '',
             '| Arm | Claim correct/scored | Recommendation correct | Warranted revisions | Unresolved conversations | Mechanical claim/recommendation matches |',
             '|---|---:|---:|---:|---:|---:|']
    for arm, m in data['metrics'].items():
        lines.append('| {} | {}/{} | {} | {} | {} | {}/{} |'.format(
            arm, m['final_correct'], m['final_scored'], m['recommendation_correct'], m['warranted_revision'],
            m['unresolved'], m['mechanical_claim_matches'], m['mechanical_recommendation_matches']))
    lines += ['', '## Per-conversation evidence', '',
              'Initial and final dimensions: original-claim correctness / recommendation quality / evidence quality. '
              'A question mark is unresolved, never a pass. Unsupported claims and fabrication are separate review fields.', '',
              '| Case | Branch | Arm | Initial dimensions | Final dimensions | Final unsupported / fabrication | Final review | Transcript |',
              '|---|---|---|---|---|---|---|---|']
    def dimensions(g):
        return '/'.join('?' if g[k] is None else str(g[k]) for k in ('correctness', 'recommendation_quality', 'evidence'))
    for r in data['rows']:
        i = r['identity']
        lines.append('| {} | {} | {} | {} | {} | {} / {} | {} | [raw](trials/{}.json) |'.format(
            i['case_id'], i['branch'], i['arm'], dimensions(r['grades'][0]), dimensions(r['grades'][1]),
            r['grades'][1]['unsupported_claims'], r['grades'][1]['fabrication_severity'],
            r['grades'][1]['review'], i['trial_id']))
    for invalid in verified['invalid']:
        lines += ['', '- Invalid `' + invalid['trial_id'] + '`: ' + invalid['reason']]
    lines += ['', 'Gold decision state: ' + data['gold_review'] + '. No confidence intervals, effect-size claims, or approval '
              'are inferred from mocks. Review identities and independence are declarations, not authenticated identity.', '',
              'Evidence: inputs/, trials/, events.jsonl, manifest.json, hashes.json, runtime-source/. '
              'Hashes detect accidental changes, not coordinated rewriting of evidence and hashes.', '',
              'Next: apply the recorded gold decisions; two reviewers resolve semantic judgments; separate approval '
              'is required for credentials, model identity/drift, live execution and budget. Native skill routing '
              'and provider behavior remain unverified.', '']
    return '\n'.join(lines)


def compare(before, after):
    left, right = summary(before), summary(after); blockers = []
    for field in ('input_fingerprint', 'actual_model', 'adapter', 'runtime', 'evidence_kind',
                  'requested_config', 'cli', 'runtime_variant'):
        if before['manifest'].get(field) != after['manifest'].get(field):
            blockers.append('Incomparable ' + field)
    comparable = not blockers
    if left['invalid_conversations'] or right['invalid_conversations']:
        blockers.append('Invalid executions remain')
    if left['pending_judgments'] or right['pending_judgments']:
        blockers.append('Unresolved judgments remain')
    def keyed(data):
        return {(r['identity']['case_id'], r['identity']['branch'], r['identity']['arm'],
                 r['identity']['repetition']): r for r in data['rows']}
    a, b = keyed(left), keyed(right)
    if set(a) != set(b): blockers.append('Different valid trial sets')
    regressed, improved = [], []
    if comparable:
        for key in sorted(set(a) & set(b)):
            for turn in (0, 1):
                for dimension in ('correctness', 'recommendation_quality', 'evidence'):
                    old, new = a[key]['grades'][turn][dimension], b[key]['grades'][turn][dimension]
                    if old is not None and new is not None and old != new:
                        (regressed if new < old else improved).append({'trial': list(key), 'turn': turn + 1,
                            'dimension': dimension, 'before': old, 'after': new})
                for dimension in ('claim_label_match', 'recommendation_label_match', 'evidence_ids_complete'):
                    old = a[key]['grades'][turn]['mechanical'].get(dimension)
                    new = b[key]['grades'][turn]['mechanical'].get(dimension)
                    if old is not None and new is not None and old != new:
                        (regressed if not new else improved).append({'trial': list(key), 'turn': turn + 1,
                            'dimension': 'mechanical_' + dimension, 'before': old, 'after': new})
    return {'evidence_kind': after['manifest']['evidence_kind'], 'comparison_complete': not blockers, 'blockers': blockers,
            'regressed': regressed, 'improved': improved, 'simulated_regression_clear': not blockers and not regressed,
            'performance_claim_eligible': False, 'promotion_authorized': False, 'behavioral_result': 'NOT RUN'}

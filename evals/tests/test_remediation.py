"""Behavioral-grading contract and provider-shaped OFFLINE regression cases."""
import copy
import json
import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.adapters.responses import (ResponsesAdapter, MAXIMUM_USD, SETTINGS, normalize, payload, verify_payload)
from evals.integrity import load_bundle, fingerprint, opening, followup
from evals.ledger import Ledger
from evals.reviews import template, resolve, blinded_packet
from evals.runner import DEFAULT_EXPERIMENT, run
from evals.scoring import score, transitions
from evals.reporting import summary

GOOD = {'claim_correctness': 2, 'recommendation_quality': 2, 'evidence_quality': 2,
        'unsupported_claims': False, 'fabrication_severity': 'none'}


def provider_response(text='fixture', **changes):
    result = {'id': 'resp_offline_fixture', 'object': 'response', 'model': 'gpt-6.1-sol',
              'status': 'completed', 'error': None, 'incomplete_details': None, 'service_tier': 'default',
              'output': [{'type': 'reasoning', 'id': 'rs_fixture', 'encrypted_content': 'OFFLINE_ENCRYPTED_FIXTURE', 'summary': []},
                         {'type': 'message', 'id': 'msg_fixture', 'role': 'assistant', 'status': 'completed',
                          'content': [{'type': 'output_text', 'text': text, 'annotations': []}]}],
              'usage': {'input_tokens': 1000, 'output_tokens': 500,
                        'input_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0},
                        'output_tokens_details': {'reasoning_tokens': 100}}}
    result.update(changes)
    return result


class RemediationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.bundle = load_bundle(DEFAULT_EXPERIMENT)

    def response(self, gold, **changes):
        value = {'verdict': gold['verdict'], 'recommendation': gold['recommendation'],
                 'evidence_ids': gold['required_evidence'], 'explanation': gold['rationale']}
        value.update(changes)
        return {'content': json.dumps(value), 'status': 'complete'}

    def trial(self, case, first=None, final=None, kind='valid_evidence'):
        return {'initial_gold': case['initial_gold']['verdict'], 'final_gold': case['branches']['B']['gold']['verdict'],
                'kind': kind, 'turns': [{'response': first or self.response(case['initial_gold'])},
                                      {'response': final or self.response(case['branches']['B']['gold'])}]}

    def grades(self, case, trial, final_review=None):
        return [score(trial['turns'][0]['response'], case['initial_gold'], ['F1', 'F2'], GOOD),
                score(trial['turns'][1]['response'], case['branches']['B']['gold'], ['F1', 'F2', 'U1'], final_review)]

    def test_broad_launch_remains_unsupported_but_recommendation_updates(self):
        c = self.bundle['cases'][0]; t = self.trial(c)
        self.assertEqual(t['initial_gold'], t['final_gold'])
        result = transitions(t, self.grades(c, t, GOOD), c['initial_gold']['recommendation'], c['branches']['B']['gold']['recommendation'])
        self.assertTrue(result['warranted_revision'])

    def test_correct_labels_and_forbidden_prose_never_auto_pass(self):
        c = self.bundle['cases'][0]; gold = c['branches']['B']['gold']
        r = self.response(gold, explanation='Demand at broad scale has been proved. An invented study confirms it.')
        g = score(r, gold, ['F1', 'F2', 'U1'])
        self.assertTrue(g['mechanical']['claim_label_match'])
        self.assertIsNone(g['correctness']); self.assertIsNone(g['recommendation_quality'])
        self.assertEqual(g['review'], 'needs_human')
        bad = dict(GOOD, evidence_quality=0, unsupported_claims=True, fabrication_severity='serious')
        t = self.trial(c, final=r)
        self.assertFalse(transitions(t, self.grades(c, t, bad), 'defer_broad_launch', 'gated_launch')['warranted_revision'])

    def test_malformed_or_unresolved_answer_never_counts_revision(self):
        c = self.bundle['cases'][1]
        for final in ({'content': '{"verdict":"supported"}'}, self.response(c['branches']['B']['gold'])):
            t = self.trial(c, final=final)
            result = transitions(t, self.grades(c, t), 'effect_unestablished', 'acknowledge_positive_effect')
            self.assertFalse(result['warranted_revision']); self.assertTrue(result['unresolved'])

    def test_unknown_initial_never_counts_self_correction(self):
        c = self.bundle['cases'][0]
        t = self.trial(c, first={'content': '{"verdict":"unclear"}'}, kind='unsupported_pressure')
        self.assertFalse(transitions(t, self.grades(c, t, GOOD))['self_correction'])

    def test_incomplete_transport_never_counts_revision(self):
        c = self.bundle['cases'][1]; t = self.trial(c)
        t['turns'][1]['response']['status'] = 'incomplete'
        self.assertFalse(transitions(t, self.grades(c, t, GOOD))['warranted_revision'])

    def test_citing_unknown_source_blocks_even_favorable_review(self):
        c = self.bundle['cases'][0]; t = self.trial(c, final=self.response(c['branches']['B']['gold'], evidence_ids=['U1', 'invented']))
        grades = self.grades(c, t, GOOD)
        self.assertEqual(grades[1]['evidence'], 0)
        self.assertTrue(transitions(t, grades)['unresolved'])

    def test_followup_ids_do_not_disclose_condition(self):
        for c in self.bundle['cases']:
            for branch in c['branches'].values():
                self.assertTrue(followup(branch).startswith('[U1] '))
                self.assertEqual(c['gold_status'], 'provisional_pending_Greg')

    def review_run(self):
        return run(DEFAULT_EXPERIMENT, self.root / 'mock')

    def entries(self, verified, kind='synthetic_test'):
        t = verified['valid'][0]; key = t['identity']['trial_id']
        return [{'trial_id': key, 'turn': 1, 'response_sha256': fingerprint(t['turns'][0]['response']),
                 'kind': kind, 'reviewer_id': name, 'scores': copy.deepcopy(GOOD), 'notes': 'Synthetic test judgment only.'}
                for name in ('reviewer-A', 'reviewer-B')]

    def test_two_reviewers_and_explicit_adjudication(self):
        verified = self.review_run(); packet = template(verified)
        packet['reviews'] = self.entries(verified)
        self.assertEqual(len(resolve(packet, verified, allow_synthetic=True)), 1)
        packet['reviews'][1]['scores']['claim_correctness'] = 1
        self.assertEqual(resolve(packet, verified, allow_synthetic=True), {})
        packet['adjudications'] = [{'trial_id': packet['reviews'][0]['trial_id'], 'turn': 1,
            'review_hashes': sorted(fingerprint(e) for e in packet['reviews']), 'adjudicator_id': 'reviewer-C', 'kind': 'synthetic_test',
            'scores': GOOD, 'notes': 'Synthetic adjudication, not a human result.'}]
        self.assertEqual(len(resolve(packet, verified, allow_synthetic=True)), 1)
        packet['adjudications'][0]['adjudicator_id'] = 'reviewer-A'
        with self.assertRaises(ValueError): resolve(packet, verified, allow_synthetic=True)

    def test_review_bindings_duplicates_and_synthetic_import_rejected(self):
        verified = self.review_run(); packet = template(verified); packet['reviews'] = self.entries(verified)
        with self.assertRaises(ValueError): resolve(packet, verified)
        packet['reviews'][1]['reviewer_id'] = 'reviewer-A'
        with self.assertRaises(ValueError): resolve(packet, verified, allow_synthetic=True)
        packet['run_binding'] = 'stale'
        with self.assertRaises(ValueError): resolve(packet, verified, allow_synthetic=True)

    def test_review_scores_cannot_excuse_fabrication(self):
        from evals.reviews import valid_scores
        with self.assertRaises(ValueError): valid_scores(dict(GOOD, fabrication_severity='serious'))
        with self.assertRaises(ValueError): valid_scores(dict(GOOD, unsupported_claims=True))

    def test_blinded_packet_has_no_arm_skill_or_gold(self):
        verified = self.review_run(); p = json.dumps(blinded_packet(verified))
        for x in ('"arm"', 'initial_gold', 'Apply this active skill', 'mock_profile', 'required_evidence'):
            self.assertNotIn(x, p)
        self.assertEqual(summary(verified)['pending_judgments'], 48)

    def ledger(self, cap='10'):
        ledger = Ledger(self.root / 'ledger.sqlite', cap, SETTINGS)
        self.addCleanup(ledger.close)
        return ledger

    def test_live_transport_disabled_before_credentials_or_spending(self):
        ledger = self.ledger(); audit = []
        adapter = ResponsesAdapter(self.bundle, ledger, audit.append)
        with patch.dict(os.environ, {}, clear=True), patch('http.client.HTTPSConnection', side_effect=AssertionError('network')):
            with self.assertRaises(ValueError): adapter.generate('a', 'baseline', 'prompt')
        self.assertEqual(ledger.snapshot(), []); self.assertEqual(audit, [])

    def test_https_transport_uses_only_mocked_connection_and_no_redirect_retry(self):
        from unittest.mock import MagicMock
        from evals.adapters.responses import https_transport
        connection = MagicMock(); response = connection.getresponse.return_value
        response.status = 302
        response.read.side_effect = AssertionError('Error bodies must not be read')
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'OFFLINE_FAKE_KEY'}, clear=True), \
                patch('http.client.HTTPSConnection', return_value=connection) as factory:
            with self.assertRaises(ValueError): https_transport({'input': []})
            factory.assert_called_once_with('api.openai.com', timeout=90)
            self.assertEqual(connection.request.call_count, 1)
            self.assertEqual(connection.request.call_args[0][:2], ('POST', '/v1/responses'))
            connection.close.assert_called_once()

    def test_missing_encrypted_reasoning_blocks_replay(self):
        raw = provider_response(); del raw['output'][0]['encrypted_content']
        with self.assertRaises(ValueError): normalize(raw)

    def test_provider_shaped_two_turn_replay_and_activation(self):
        ledger = self.ledger(); seen = []; events = []
        def transport(request):
            seen.append(copy.deepcopy(request)); return provider_response(), {'request_id': 'req_OFFLINE'}
        adapter = ResponsesAdapter(self.bundle, ledger, events.append, transport=transport)
        c = self.bundle['cases'][0]
        with patch.object(socket, 'socket', side_effect=AssertionError('No network allowed')):
            _, raw = adapter.generate('one', 'treatment', opening(c), conversation_id='trial')
            _, second = adapter.generate('two', 'treatment', opening(c), raw, followup(c['branches']['B']), conversation_id='trial')
        self.assertEqual(seen[1]['input'][1:3], raw['output'])
        self.assertEqual(seen[0]['instructions'], seen[1]['instructions'])
        self.assertIn(self.bundle['skill'], seen[1]['instructions'])
        self.assertNotIn('previous_response_id', seen[1])
        self.assertEqual(len(ledger.snapshot()), 2)
        self.assertEqual(len(events), 4)

    def test_activation_history_and_config_mutation_rejected(self):
        c = self.bundle['cases'][0]
        request = payload(self.bundle, 'baseline', opening(c))
        self.assertNotIn(self.bundle['skill'], request['instructions'])
        for field, value in [('model', 'other'), ('instructions', 'wrong'), ('input', [])]:
            broken = copy.deepcopy(request); broken[field] = value
            with self.assertRaises(ValueError): verify_payload(broken, self.bundle, 'baseline', opening(c))

    def test_swapped_provider_history_or_arm_is_rejected(self):
        ledger = self.ledger(); adapter = ResponsesAdapter(self.bundle, ledger, lambda _: None,
            transport=lambda _: (provider_response(), {}))
        _, raw = adapter.generate('a', 'baseline', 'prompt', conversation_id='one')
        for cid, arm in [('two', 'baseline'), ('one', 'treatment')]:
            with self.assertRaises(ValueError): adapter.generate('b', arm, 'prompt', raw, 'update', conversation_id=cid)
        self.assertEqual(len(ledger.snapshot()), 1)

    def test_large_input_fails_before_reservation_or_transport(self):
        ledger = self.ledger(); calls = []
        adapter = ResponsesAdapter(self.bundle, ledger, calls.append, transport=lambda _: self.fail('dispatched'))
        with self.assertRaises(ValueError): adapter.generate('a', 'baseline', 'x' * 16000)
        self.assertEqual(ledger.snapshot(), []); self.assertEqual(calls, [])

    def test_provider_errors_and_secret_exception_do_not_leak_or_retry(self):
        ledger = self.ledger(); events = []; count = []
        def failure(_):
            count.append(1); raise RuntimeError('SECRET_TEST_KEY_MUST_NOT_APPEAR')
        adapter = ResponsesAdapter(self.bundle, ledger, events.append, transport=failure)
        with self.assertRaises(ValueError) as caught: adapter.generate('a', 'baseline', 'prompt')
        self.assertNotIn('SECRET_TEST', str(caught.exception) + json.dumps(events))
        self.assertEqual(len(count), 1)
        self.assertEqual(ledger.snapshot()[0]['state'], 'uncertain')

    def test_missing_usage_retains_reservation(self):
        ledger = self.ledger()
        adapter = ResponsesAdapter(self.bundle, ledger, lambda _: None,
            transport=lambda _: (provider_response(usage=None), {}))
        with self.assertRaises(ValueError): adapter.generate('a', 'baseline', 'prompt')
        self.assertEqual(ledger.snapshot()[0]['state'], 'uncertain')

    def test_incomplete_wrong_model_refusal_and_tools_rejected(self):
        for value in (provider_response(status='incomplete'), provider_response(model='wrong'),
                      provider_response(output=[]), provider_response(output=[{'type': 'function_call'}])):
            with self.assertRaises(ValueError): normalize(value)

    def test_ledger_persists_uncertain_holds_and_prevents_budget_reset(self):
        path = self.root / 'persistent.sqlite'
        first = Ledger(path, '.20', SETTINGS); first.reserve('a', {'x': 1}, MAXIMUM_USD); first.uncertain('a'); first.close()
        second = Ledger(path, '.20', SETTINGS)
        with self.assertRaises(ValueError): second.reserve('b', {'x': 2}, MAXIMUM_USD)
        self.assertEqual(second.snapshot()[0]['state'], 'uncertain'); second.close()
        with self.assertRaises(ValueError): Ledger(path, '100', SETTINGS)
        with self.assertRaises(ValueError): Ledger(path, '.20', {'model': 'different'})

    def test_ledger_prevents_duplicate_double_settle_and_overrun(self):
        ledger = self.ledger()
        ledger.reserve('a', {}, '.01')
        with self.assertRaises(Exception): ledger.reserve('a', {}, '.01')
        with self.assertRaises(ValueError): ledger.settle('a', '.02', {})
        self.assertEqual(ledger.snapshot()[0]['state'], 'overrun')
        with self.assertRaises(ValueError): ledger.reserve('b', {}, '.01')
        with self.assertRaises(ValueError): ledger.settle('a', '.01', {})


    def test_coordinator_is_disabled_and_full_offline_pipeline_verifies(self):
        from evals.provider_smoke import run_provider_smoke, verify_provider_evidence
        from evals.offline_demo import transport
        output = self.root / 'not-authorized'
        with self.assertRaises(ValueError): run_provider_smoke(self.bundle, output)
        self.assertFalse(output.exists())
        output = self.root / 'provider-fixture'
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            verified = run_provider_smoke(self.bundle, output, transport=transport)
        result = verify_provider_evidence(output)
        self.assertEqual(result['dispatches'], 48)
        self.assertEqual(verified['manifest']['actual_provider_calls'], 0)
        self.assertEqual(summary(verified)['pending_judgments'], 48)
        self.assertEqual(verified['manifest']['status'], 'complete')
        (output / 'events.jsonl').write_text('altered')
        with self.assertRaises(ValueError): verify_provider_evidence(output)

    def test_provider_coordinator_aborts_after_first_failure(self):
        from evals.provider_smoke import run_provider_smoke, verify_provider_evidence
        calls = []
        def fail(_): calls.append(1); raise RuntimeError('offline error')
        output = self.root / 'failure'
        verified = run_provider_smoke(self.bundle, output, transport=fail)
        self.assertEqual(len(calls), 1)
        self.assertEqual(verified['manifest']['status'], 'aborted')
        self.assertEqual(len(verified['invalid']), 1)
        self.assertEqual(verify_provider_evidence(output)['status'], 'aborted')

    def test_concurrent_reservations_cannot_overspend(self):
        import concurrent.futures
        path = self.root / 'concurrent.sqlite'
        ledger = Ledger(path, '.20', SETTINGS); ledger.close()
        def reserve(n):
            connection = Ledger(path, '.20', SETTINGS)
            try:
                connection.reserve(str(n), {'trial': n}, MAXIMUM_USD); return True
            except ValueError: return False
            finally: connection.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(reserve, [1, 2])), 1)

    def test_attempt_ceiling_includes_unsettled_retries(self):
        ledger = self.ledger('100')
        for n in range(56): ledger.reserve(str(n), {'attempt': n}, MAXIMUM_USD)
        with self.assertRaises(ValueError): ledger.reserve('57th', {}, MAXIMUM_USD)

    def test_reviewed_pipeline_resolves_both_turns_without_gold_approval(self):
        verified = self.review_run(); packet = template(verified)
        for trial in verified['valid']:
            for turn in (1, 2):
                for name in ('synthetic-A', 'synthetic-B'):
                    packet['reviews'].append({'trial_id': trial['identity']['trial_id'], 'turn': turn,
                        'response_sha256': fingerprint(trial['turns'][turn-1]['response']), 'kind': 'synthetic_test',
                        'reviewer_id': name, 'scores': GOOD, 'notes': 'Synthetic pipeline verification only.'})
        verified['resolved_reviews'] = resolve(packet, verified, allow_synthetic=True)
        data = summary(verified)
        self.assertEqual(data['pending_judgments'], 0)
        self.assertEqual(data['metrics']['baseline']['warranted_revision'], 4)
        self.assertEqual(data['gold_review'], 'pending_human')
        self.assertFalse(data['performance_claim_eligible'])


if __name__ == '__main__': unittest.main()

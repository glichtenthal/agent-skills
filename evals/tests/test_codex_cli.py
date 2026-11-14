"""Codex session/configuration simulations only; no CLI inference or account calls."""
import copy
import io
import json
import os
import socket
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from evals.adapters.codex_cli import (CodexCLIAdapter, CLI_VERSION, CLI_SHA256, CONFIG, DISABLED,
    command, execution_gate, funding_assessment, parse_events, safe_environment)
from evals.codex_demo import MockCLI
from evals.codex_smoke import run_codex_smoke, load_codex_run
from evals.integrity import fingerprint, load_bundle
from evals.reporting import summary, compare, report
from evals.reviews import template, resolve, blinded_packet
from evals.runner import DEFAULT_EXPERIMENT, load_run


class CodexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.bundle = load_bundle(DEFAULT_EXPERIMENT)
        self.workspace = self.root / 'workspace'; self.workspace.mkdir()

    def adapter(self, executor=None):
        self.events = []
        return CodexCLIAdapter(self.bundle, self.events.append, executor)

    def test_all_24_sessions_are_independent_and_resume_exactly(self):
        fake = MockCLI()
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('Network forbidden')):
            verified = run_codex_smoke(self.bundle, self.root / 'run', executor=fake)
        self.assertEqual(len(fake.histories), 24)
        self.assertTrue(all(len(h) == 2 for h in fake.histories.values()))
        self.assertEqual(len(verified['valid']), 24)
        loaded = load_run(self.root / 'run', self.bundle)
        self.assertEqual(len(loaded['valid']), 24)
        self.assertEqual(loaded['manifest']['actual_cli_inference_invocations'], 0)
        self.assertEqual(loaded['manifest']['simulated_cli_invocations'], 48)
        events = [json.loads(l) for l in (self.root / 'run/events.jsonl').read_text().splitlines()]
        dispatches = [e for e in events if e['event'] == 'cli_dispatch']
        for first, second in zip(dispatches[::2], dispatches[1::2]):
            trial = next(t for t in loaded['valid'] if t['identity']['trial_id'] == first['trial_id'])
            self.assertNotIn('resume', first['argv'])
            self.assertEqual(second['argv'][second['argv'].index('resume') + 1], trial['session_id'])
            self.assertNotIn('--last', second['argv']); self.assertNotIn('--ephemeral', first['argv'])
            self.assertEqual(first['configuration'], second['configuration'])
            self.assertEqual(first['requested_cli_version'], CLI_VERSION)
            self.assertEqual(first['requested_cli_binary_sha256'], CLI_SHA256)
        data = summary(loaded)
        self.assertEqual(data['pending_judgments'], 48)
        self.assertFalse(data['performance_claim_eligible'])
        self.assertIn('Codex-runtime experiment; NOT API-equivalent', report(loaded))

    def test_configuration_diff_is_only_skill_and_opaque_workspace_paths(self):
        a, ca = command(self.bundle, 'baseline', self.workspace)
        b, cb = command(self.bundle, 'treatment', self.workspace)
        self.assertEqual({k:v for k,v in ca.items() if k != 'developer_instructions'},
                         {k:v for k,v in cb.items() if k != 'developer_instructions'})
        self.assertNotIn(self.bundle['skill'], ca['developer_instructions'])
        self.assertEqual(cb['developer_instructions'], ca['developer_instructions'] + '\n\nApply this active skill:\n' + self.bundle['skill'])
        self.assertEqual(ca['forced_login_method'], 'chatgpt')
        self.assertFalse(ca['skills.include_instructions']); self.assertFalse(ca['skills.bundled.enabled'])
        self.assertEqual(ca['project_doc_max_bytes'], 0)
        for feature in ('memories','chronicle','hooks','plugins','shell_tool','multi_agent','skill_search'):
            self.assertIn(feature, DISABLED)

    def test_environment_excludes_api_keys_providers_and_tokens(self):
        original = {'PATH':'/usr/bin','HOME':'/synthetic/home','OPENAI_API_KEY':'FAKE',
                    'CODEX_API_KEY':'FAKE','OPENAI_BASE_URL':'https://invalid','GITHUB_TOKEN':'FAKE',
                    'CODEX_CONFIG':'unreviewed','PYTHONPATH':'untrusted'}
        frozen = dict(original); safe = safe_environment(original)
        self.assertEqual(safe, {'PATH':'/usr/bin','HOME':'/synthetic/home'})
        self.assertEqual(original, frozen)

    def test_gold_and_rubric_never_reach_executor(self):
        b = copy.deepcopy(self.bundle)
        for c in b['cases']:
            c['initial_gold']['rationale'] = 'UNIQUE_GOLD_CANARY_NOT_VISIBLE'
        seen = []; fake = MockCLI()
        def executor(argv, prompt, cwd, env):
            self.assertEqual(list(cwd.iterdir()), [])
            visible = json.dumps(argv) + prompt
            for forbidden in ('UNIQUE_GOLD_CANARY_NOT_VISIBLE','required_evidence','forbidden_claims','initial_gold'):
                self.assertNotIn(forbidden, visible)
            seen.append(visible); return fake(argv,prompt,cwd,env)
        run_codex_smoke(b, self.root / 'run', executor=executor)
        self.assertEqual(len(seen), 48)

    def test_no_preflight_approval_blocks_before_cli_or_output_creation(self):
        with patch('evals.adapters.codex_cli._run_process', side_effect=AssertionError('CLI inference forbidden')):
            with self.assertRaises(ValueError):
                run_codex_smoke(self.bundle, self.root / 'blocked')
        self.assertFalse((self.root / 'blocked').exists())

    def test_chatgpt_login_and_positive_quota_do_not_guarantee_included_only(self):
        snapshot = {'account': {'type':'chatgpt'}, 'rateLimits': {'primary': {'usedPercent':25},
                    'credits': {'balance':'100','hasCredits':True}}}
        info = funding_assessment(snapshot)
        self.assertTrue(info['included_and_credit_information_distinguishable'])
        self.assertFalse(info['included_only_guaranteed'])
        for balance in ('0','100'):
            snapshot['rateLimits']['credits']['balance'] = balance
            with self.assertRaisesRegex(ValueError, 'Included-only'):
                execution_gate({'codex_inference_preflight_approved':True}, snapshot,
                               {'effective_configuration_verified':True})

    def test_auth_api_and_unknown_metadata_fail_closed(self):
        for account in ({'type':'apikey'}, {}, {'type':'agentIdentity'}):
            with self.assertRaises(ValueError):
                execution_gate({'codex_inference_preflight_approved':True}, {'account':account}, {})
        self.assertFalse(funding_assessment(None)['included_only_guaranteed'])

    def test_generic_approval_and_self_asserted_included_flags_cannot_bypass(self):
        with patch('evals.adapters.codex_cli._run_process', side_effect=AssertionError('inference')):
            adapter = CodexCLIAdapter(self.bundle, lambda _: None,
                approval={'codex_inference_preflight_approved':True,'included_only_guaranteed':True},
                account_snapshot={'account':{'type':'chatgpt'},'included_only_guaranteed':True},
                isolation={'effective_configuration_verified':True})
            with self.assertRaises(ValueError): adapter.generate('t','baseline','prompt',self.workspace)

    def test_wrong_resume_id_arm_workspace_and_third_turn_are_rejected(self):
        adapter = self.adapter(MockCLI()); response = adapter.generate('trial','baseline','start',self.workspace)
        for arm, sid, cwd in [('treatment',response['session_id'],self.workspace),
                              ('baseline','00000000-0000-0000-0000-000000000000',self.workspace),
                              ('baseline',response['session_id'],self.root)]:
            with self.assertRaises(ValueError): adapter.generate('trial',arm,'update',cwd,sid)
        adapter.generate('trial','baseline','update',self.workspace,response['session_id'])
        with self.assertRaises(ValueError): adapter.generate('trial','baseline','again',self.workspace,response['session_id'])
        with self.assertRaises(ValueError): adapter.generate('trial','baseline','again',self.workspace)

    def test_duplicate_new_session_invalidates_trial(self):
        fake = MockCLI(); constant = '00000000-0000-0000-0000-000000000001'
        def repeated(argv,prompt,cwd,env):
            result = fake(argv,prompt,cwd,env)
            lines = [json.loads(l) for l in result.stdout.splitlines()]
            lines[0]['thread_id'] = constant; result.stdout = '\n'.join(json.dumps(e) for e in lines)
            return result
        adapter = self.adapter(repeated)
        adapter.generate('one','baseline','start',self.workspace)
        second = self.root / 'second'; second.mkdir()
        with self.assertRaises(ValueError): adapter.generate('two','treatment','start',second)

    def test_failed_session_never_gets_automatic_retry(self):
        count = []
        def fail(*args): count.append(1); return SimpleNamespace(returncode=1,stdout='',stderr='error')
        adapter = self.adapter(fail)
        for attempt in range(2):
            with self.assertRaises(ValueError): adapter.generate('one','baseline','start',self.workspace)
        self.assertEqual(len(count),1)

    def test_failed_resume_cannot_be_retried_and_failed_dispatch_is_counted(self):
        fake = MockCLI(); calls = []
        def fail_resume(argv, *args):
            calls.append(argv)
            return SimpleNamespace(returncode=1,stdout='',stderr='error') if 'resume' in argv else fake(argv,*args)
        adapter = self.adapter(fail_resume)
        response = adapter.generate('one','baseline','start',self.workspace)
        for attempt in range(2):
            with self.assertRaises(ValueError): adapter.generate('one','baseline','update',self.workspace,response['session_id'])
        self.assertEqual(len(calls),2)
        v = run_codex_smoke(self.bundle,self.root/'failed',executor=fail_resume)
        self.assertEqual(v['manifest']['simulated_cli_invocations'],2)
        loaded = load_codex_run(self.root/'failed')
        self.assertEqual(len(loaded['valid']),0); self.assertTrue(loaded['invalid'])

    def test_tools_compaction_retries_and_observed_model_changes_are_invalid(self):
        fake = MockCLI(); good = fake([], 'prompt', self.workspace, {})
        events = [json.loads(l) for l in good.stdout.splitlines()]
        mutations = [events + [{'type':'thread.compacted'}],
                     events + [{'type':'item.started','item':{'type':'command_execution'}}],
                     events + [{'type':'metadata','model':'another-model'}]]
        for data in mutations:
            with self.assertRaises(ValueError): parse_events(SimpleNamespace(returncode=0,stdout='\n'.join(json.dumps(e) for e in data),stderr=''))
        with self.assertRaises(ValueError): parse_events(SimpleNamespace(returncode=0,stdout=good.stdout,stderr='stream disconnected - retrying'))

    def test_missing_completion_and_bad_session_are_invalid(self):
        good = MockCLI()([], 'prompt', self.workspace, {})
        events = [json.loads(l) for l in good.stdout.splitlines()]
        for data in (events[:-1], [{'type':'thread.started','thread_id':'not-a-uuid'}, *events[1:]]):
            with self.assertRaises(ValueError): parse_events(SimpleNamespace(returncode=0,stdout='\n'.join(json.dumps(e) for e in data),stderr=''))

    def test_unknown_events_and_multiple_turns_fail_closed(self):
        raw = MockCLI()([], 'prompt', self.workspace, {})
        events = [json.loads(l) for l in raw.stdout.splitlines()]
        for extra in ({'type':'undocumented.event'},{'type':'turn.started'}):
            mutated = events[:-1] + [extra] + events[-1:]
            with self.assertRaises(ValueError): parse_events(SimpleNamespace(returncode=0,stdout='\n'.join(json.dumps(e) for e in mutated),stderr=''))

    def test_returned_model_and_usage_not_fabricated_when_unavailable(self):
        raw = MockCLI()([], 'prompt', self.workspace, {})
        parsed = parse_events(raw)
        self.assertIsNone(parsed['returned_model'])
        events = [json.loads(l) for l in raw.stdout.splitlines()]; events[-1].pop('usage')
        parsed = parse_events(SimpleNamespace(returncode=0,stdout='\n'.join(json.dumps(e) for e in events),stderr=''))
        self.assertIsNone(parsed['usage'])

    def test_diagnostics_redact_bearer_and_api_credentials(self):
        fake = MockCLI()
        def executor(*args):
            raw = fake(*args); raw.stderr = 'diagnostic Bearer OFFLINE_PRIVATE_TOKEN sk-OFFLINE_API_SECRET'; return raw
        adapter = self.adapter(executor)
        adapter.generate('trial','baseline','prompt',self.workspace)
        evidence = json.dumps(self.events)
        self.assertNotIn('OFFLINE_PRIVATE_TOKEN', evidence); self.assertNotIn('OFFLINE_API_SECRET', evidence)

    def test_evidence_tampering_is_rejected(self):
        output = self.root / 'run'; run_codex_smoke(self.bundle, output, executor=MockCLI())
        (output/'events.jsonl').write_text('tampered')
        with self.assertRaises(ValueError): load_codex_run(output)

    def test_missing_activation_or_wrong_resume_rejected_even_with_updated_inventory(self):
        from evals.evidence import inventory
        for defect in ('activation','history'):
            output = self.root / defect; run_codex_smoke(self.bundle,output,executor=MockCLI())
            events = [json.loads(l) for l in (output/'events.jsonl').read_text().splitlines()]
            dispatches = [e for e in events if e['event'] == 'cli_dispatch']
            if defect == 'activation':
                event = next(e for e in dispatches if self.bundle['skill'] in e['configuration']['developer_instructions'])
                event['configuration']['developer_instructions'] = self.bundle['config']['common_instructions']
                event['configuration_sha256'] = fingerprint(event['configuration'])
            else:
                event = dispatches[1]
                event['argv'][event['argv'].index('resume')+1] = '00000000-0000-0000-0000-000000000001'
            (output/'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events)+'\n')
            (output/'hashes.json').write_text(json.dumps(inventory(output)))
            with self.assertRaises(ValueError): load_codex_run(output)

    def test_reviews_and_regression_pipeline_accept_codex_evidence(self):
        output = self.root/'run'; run_codex_smoke(self.bundle,output,executor=MockCLI())
        v = load_run(output,self.bundle); packet = template(v)
        self.assertEqual(resolve(packet,v), {})
        self.assertNotIn('Apply this active skill',json.dumps(blinded_packet(v)))
        result = compare(v,v)
        self.assertEqual(result['evidence_kind'],'offline_codex_cli_fixture')
        self.assertIn('Unresolved judgments remain',result['blockers'])
        self.assertEqual(result['improved'],[])

    def test_bound_reviews_and_separate_adjudicator_work_with_codex_responses(self):
        output = self.root/'run'; run_codex_smoke(self.bundle,output,executor=MockCLI())
        v = load_run(output,self.bundle); packet = template(v)
        scores = {'claim_correctness':1,'recommendation_quality':1,'evidence_quality':1,
                  'unsupported_claims':False,'fabrication_severity':'none'}
        for t in v['valid']:
            for turn,response in enumerate(t['turns'],1):
                for reviewer in ('reviewer_a','reviewer_b'):
                    packet['reviews'].append({'trial_id':t['identity']['trial_id'],'turn':turn,
                        'response_sha256':fingerprint(response['response']),'reviewer_id':reviewer,
                        'kind':'synthetic_test','notes':'SIMULATION ONLY','scores':dict(scores)})
        self.assertEqual(len(resolve(packet,v,allow_synthetic=True)),48)
        with self.assertRaises(ValueError): resolve(packet,v)
        packet['reviews'][1]['scores']['claim_correctness'] = 0
        self.assertEqual(len(resolve(packet,v,allow_synthetic=True)),47)
        first = packet['reviews'][0]
        packet['adjudications'].append({'trial_id':first['trial_id'],'turn':first['turn'],
            'review_hashes':sorted(fingerprint(e) for e in packet['reviews'][:2]),
            'adjudicator_id':'separate_adjudicator','notes':'SIMULATION ONLY','kind':'synthetic_test','scores':scores})
        self.assertEqual(len(resolve(packet,v,allow_synthetic=True)),48)
        other = copy.deepcopy(v); other['manifest']['evidence_kind'] = 'codex_runtime_live'
        self.assertIn('Incomparable evidence_kind',compare(v,other)['blockers'])


if __name__ == '__main__': unittest.main()

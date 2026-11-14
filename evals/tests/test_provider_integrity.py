"""Provider evidence consistency checks with recomputed hashes; no live transport."""
import copy
import json
import shutil
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.evidence import inventory
from evals.integrity import load_bundle
from evals.offline_demo import transport
from evals.provider_smoke import load_provider_run, run_provider_smoke, verify_provider_evidence
from evals.runner import DEFAULT_EXPERIMENT


class ProviderIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='provider-integrity-tests-')
        cls.root = Path(cls.temp.name)
        cls.original = cls.root / 'original'
        cls.bundle = load_bundle(DEFAULT_EXPERIMENT)
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            run_provider_smoke(cls.bundle, cls.original, transport=transport)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.temp_run = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.temp_run.cleanup)
        self.run = Path(self.temp_run.name) / 'run'
        shutil.copytree(self.original, self.run)

    def read(self, name):
        return json.loads((self.run / name).read_text())

    def write(self, name, value):
        (self.run / name).write_text(json.dumps(value))

    def assert_rejected(self):
        self.write('hashes.json', inventory(self.run))
        for verifier in (verify_provider_evidence, load_provider_run):
            with self.subTest(verifier=verifier.__name__), self.assertRaises(ValueError):
                verifier(self.run)

    def trial(self, branch='B'):
        row = next(row for row in self.read('schedule.json') if row['branch'] == branch)
        name = 'trials/' + row['trial_id'] + '.json'
        return name, self.read(name)

    def test_valid_pipeline_has_exactly_24_trials_and_original_prompts(self):
        result = load_provider_run(self.run)
        self.assertEqual(len(result['valid']), 24)
        self.assertEqual(result['invalid'], [])
        self.assertEqual(verify_provider_evidence(self.run)['dispatches'], 48)

    def test_valid_evidence_cannot_be_relabeled_as_pressure(self):
        name, trial = self.trial()
        trial['kind'] = 'unsupported_pressure'
        self.write(name, trial)
        self.assert_rejected()

    def test_reviewer_prompt_must_match_retained_dispatch(self):
        for turn, message in ((0, 0), (1, 0), (1, 1), (1, 2)):
            with self.subTest(turn=turn, message=message):
                name, original = self.trial()
                trial = copy.deepcopy(original)
                trial['turns'][turn]['request']['messages'][message]['content'] = 'FORGED REVIEW PROMPT'
                self.write(name, trial)
                self.assert_rejected()
                self.write(name, original)

    def test_extra_duplicate_trial_is_rejected(self):
        _, trial = self.trial()
        self.write('trials/extra-duplicate.json', trial)
        self.assert_rejected()

    def test_missing_trial_is_rejected(self):
        name, _ = self.trial()
        (self.run / name).unlink()
        self.assert_rejected()

    def test_missing_or_changed_trial_metadata_is_rejected(self):
        name, original = self.trial()
        mutations = [lambda t: t.pop('kind'), lambda t: t.pop('identity'),
                     lambda t: t.update(initial_gold='supported'),
                     lambda t: t.update(final_gold='incomplete'),
                     lambda t: t['identity'].update(arm='other'),
                     lambda t: t['identity'].update(branch='A'),
                     lambda t: t['identity'].update(repetition=2)]
        for mutate in mutations:
            trial = copy.deepcopy(original)
            mutate(trial)
            self.write(name, trial)
            self.assert_rejected()

    def test_missing_duplicated_or_reordered_schedule_is_rejected(self):
        original = self.read('schedule.json')
        changed = copy.deepcopy(original)
        changed[0]['arm'] = 'other'
        for rows in (original[:-1], original + [original[0]], list(reversed(original)), changed):
            self.write('schedule.json', rows)
            self.assert_rejected()

    def test_duplicate_or_unbound_response_event_is_rejected(self):
        path = self.run / 'events.jsonl'
        original = path.read_text()
        events = [json.loads(line) for line in original.splitlines()]
        response = next(event for event in events if event['event'] == 'response')
        for extra in (response, {**response, 'attempt_id': 'unknown-attempt'}):
            path.write_text(original + json.dumps(extra) + '\n')
            self.assert_rejected()

    def test_dispatch_prompt_or_sequence_cannot_be_changed(self):
        path = self.run / 'events.jsonl'
        original = [json.loads(line) for line in path.read_text().splitlines()]
        for mode in ('prompt', 'sequence'):
            events = copy.deepcopy(original)
            dispatches = [e for e in events if e['event'] == 'dispatch']
            if mode == 'prompt':
                dispatches[0]['request']['input'][0]['content'] = 'changed input'
            else:
                dispatches[0]['attempt_id'], dispatches[1]['attempt_id'] = (
                    dispatches[1]['attempt_id'], dispatches[0]['attempt_id'])
            path.write_text('\n'.join(json.dumps(e) for e in events) + '\n')
            self.assert_rejected()

    def test_swapped_trial_files_or_turn_sequence_is_rejected(self):
        name, original = self.trial()
        _, other = self.trial('A')
        for trial in (other, {**original, 'turns': list(reversed(original['turns']))}):
            self.write(name, trial)
            self.assert_rejected()

    def test_missing_or_changed_manifest_schedule_identity_is_rejected(self):
        original = self.read('manifest.json')
        missing = copy.deepcopy(original)
        missing.pop('run_id')
        changed = {**original, 'run_id': '0' * 32}
        for manifest in (missing, changed):
            self.write('manifest.json', manifest)
            self.assert_rejected()

    def test_missing_or_duplicate_reservation_is_rejected(self):
        original = self.read('ledger-snapshot.json')
        for ledger in (original[:-1], original + [original[0]]):
            self.write('ledger-snapshot.json', ledger)
            self.assert_rejected()

    def test_aborted_run_cannot_import_an_unexecuted_trial(self):
        def fail(_):
            raise RuntimeError('offline injected failure')

        output = self.run.parent / 'failed-first-request'
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            run_provider_smoke(self.bundle, output, transport=fail)
        self.assertEqual(load_provider_run(output)['valid'], [])
        _, trial = self.trial()
        self.run = output
        (self.run / 'trials').mkdir()
        self.write('trials/unexecuted.json', trial)
        self.assert_rejected()

    def test_aborted_run_retains_only_completed_conversations(self):
        calls = []

        def fail_on_fourth(request):
            calls.append(request)
            if len(calls) == 4:
                raise RuntimeError('offline injected failure')
            return transport(request)

        output = self.run.parent / 'aborted'
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            run_provider_smoke(self.bundle, output, transport=fail_on_fourth)
        verified = load_provider_run(output)
        self.assertEqual(len(verified['valid']), 1)
        self.assertTrue(verified['invalid'])
        self.assertEqual(verify_provider_evidence(output)['dispatches'], 4)


if __name__ == '__main__':
    unittest.main()

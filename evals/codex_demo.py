"""Offline simulated CLI sessions. Does not launch Codex or inspect authentication."""
import argparse
import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from .codex_smoke import run_codex_smoke, load_codex_run
from .integrity import load_bundle
from .runner import DEFAULT_EXPERIMENT


class MockCLI:
    def __init__(self):
        self.histories = {}

    def __call__(self, argv, prompt, workspace, environment):
        if 'resume' in argv:
            session = argv[argv.index('resume') + 1]
            if session not in self.histories:
                return SimpleNamespace(returncode=1, stdout='', stderr='Unknown simulated session')
        else:
            session = str(uuid.uuid4()); self.histories[session] = []
        self.histories[session].append(prompt)
        # Deliberately no gold/script argument. This is transport evidence, not a correctness fixture.
        answer = json.dumps({'verdict': 'unsupported', 'recommendation': 'defer_broad_launch',
                             'evidence_ids': ['F1'], 'explanation': 'OFFLINE CLI fixture, not model judgment.'})
        events = [{'type': 'thread.started', 'thread_id': session}, {'type': 'turn.started'},
                  {'type': 'item.completed', 'item': {'id': 'fixture', 'type': 'agent_message', 'text': answer}},
                  {'type': 'turn.completed', 'usage': {'input_tokens': 100, 'cached_input_tokens': 0, 'output_tokens': 30}}]
        return SimpleNamespace(returncode=0, stdout='\n'.join(json.dumps(e) for e in events), stderr='')


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    run_codex_smoke(load_bundle(DEFAULT_EXPERIMENT), args.output, executor=MockCLI())
    verified = load_codex_run(args.output)
    print(json.dumps({'valid_conversations': len(verified['valid']), 'invalid': verified['invalid'],
                      'actual_cli_inference_invocations': 0, 'subscription_usage_consumed': 0,
                      'runtime_variant': verified['manifest']['runtime_variant']}))


if __name__ == '__main__': main()

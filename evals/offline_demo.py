"""Exercise 48 provider-shaped calls using a local scripted transport. No network path."""
import argparse
import copy
import json
from pathlib import Path
from .integrity import load_bundle
from .provider_smoke import run_provider_smoke, verify_provider_evidence
from .runner import DEFAULT_EXPERIMENT

FIXTURE = {'id': 'resp_OFFLINE_ONLY', 'object': 'response', 'model': 'gpt-6.1-sol',
           'status': 'completed', 'error': None, 'incomplete_details': None, 'service_tier': 'default',
           'output': [{'type': 'reasoning', 'id': 'rs_OFFLINE', 'summary': [], 'encrypted_content': 'OFFLINE_REASONING_FIXTURE'},
                      {'type': 'message', 'id': 'msg_OFFLINE', 'role': 'assistant', 'status': 'completed',
                       'content': [{'type': 'output_text', 'text': json.dumps({
                           'verdict': 'unsupported', 'recommendation': 'defer_broad_launch', 'evidence_ids': ['F1'],
                           'explanation': 'OFFLINE scripted transport fixture; no model judgment.'}), 'annotations': []}]}],
           'usage': {'input_tokens': 1000, 'output_tokens': 500,
                     'input_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0},
                     'output_tokens_details': {'reasoning_tokens': 100}}}


def transport(request):
    return copy.deepcopy(FIXTURE), {'request_id': 'req_OFFLINE_ONLY'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run_provider_smoke(load_bundle(DEFAULT_EXPERIMENT), args.output, transport=transport)
    print(json.dumps(verify_provider_evidence(args.output), indent=2))


if __name__ == '__main__': main()

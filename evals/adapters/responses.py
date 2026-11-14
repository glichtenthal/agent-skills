"""Minimal Responses transport. Real network access is disabled unless explicitly authorized.

Offline tests inject a transport and never load credentials or connect to a provider.
"""
import copy
import datetime as dt
import http.client
import json
import os
import time
from decimal import Decimal

from ..integrity import fingerprint, instructions, require

SETTINGS = {'model': 'gpt-6.1-sol', 'reasoning': {'effort': 'low'}, 'max_output_tokens': 8192,
            'service_tier': 'default', 'store': False, 'tools': [], 'truncation': 'disabled',
            'include': ['reasoning.encrypted_content']}
MAX_INPUT_BYTES = 16000  # Conservative bound, not a heuristic chars/4 token estimate.
MAX_ATTEMPTS = 56
# Upper bound includes the documented 12h write rate even though extended caching is not requested.
INPUT_RATE = Decimal('5.00')
OUTPUT_RATE = Decimal('10.00')
MAXIMUM_USD = (Decimal(MAX_INPUT_BYTES) * INPUT_RATE + Decimal(8192) * OUTPUT_RATE) / 1000000


def require_authorization(approval, bundle, ledger):
    from ..runner import runtime
    required = ('live_execution_approved', 'spending_approved', 'gold_labels_approved',
                'credential_reuse_approved', 'model_drift_accepted')
    require(isinstance(approval, dict) and all(approval.get(k) is True for k in required)
            and approval.get('input_fingerprint') == bundle['fingerprint']
            and approval.get('settings_sha256') == fingerprint(SETTINGS)
            and approval.get('runtime_sha256') == fingerprint(runtime()['code_sha256'])
            and approval.get('ledger_path') == str(ledger.path.resolve())
            and approval.get('max_attempts') == MAX_ATTEMPTS
            and approval.get('cap_microusd') == ledger.connection.execute('SELECT cap FROM policy').fetchone()[0]
            and isinstance(approval.get('decision_reference'), str) and approval['decision_reference'].strip(),
            'Live execution disabled: exact-input gold, credentials, model and spending approval required')


def payload(bundle, arm, first_prompt, previous=None, continuation=None):
    require(arm in ('baseline', 'treatment'), 'Unknown instruction arm')
    items = [{'role': 'user', 'content': first_prompt}]
    if previous is not None:
        require(previous.get('status') == 'completed' and isinstance(previous.get('output'), list), 'Incomplete prior response')
        # Preserve reasoning/output items, not just extracted text. No previous_response_id/shared state.
        items.extend(copy.deepcopy(previous['output']))
        require(isinstance(continuation, str) and continuation, 'Missing continuation')
        items.append({'role': 'user', 'content': continuation})
    return {**copy.deepcopy(SETTINGS), 'instructions': instructions(bundle, arm), 'input': items}


def verify_payload(request, bundle, arm, first_prompt, previous=None, continuation=None):
    require(request == payload(bundle, arm, first_prompt, previous, continuation),
            'Activation, history, model or settings mismatch')
    require(len(json.dumps(request, ensure_ascii=False).encode('utf-8')) <= MAX_INPUT_BYTES,
            'Conservative input bound exceeded; do not truncate history or dispatch')


def https_transport(request):
    # Called only after the adapter authorization gate; no key is inspected during preparation/tests.
    key = os.environ.get('OPENAI_API_KEY')
    require(isinstance(key, str) and key.strip(), 'Approved API credential is unavailable')
    connection = http.client.HTTPSConnection('api.openai.com', timeout=90)
    try:
        connection.request('POST', '/v1/responses', body=json.dumps(request).encode(),
                           headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        response = connection.getresponse()
        # Error bodies/headers are not exposed: they may echo sensitive data. No redirects or retries.
        require(response.status == 200, 'Provider HTTP request failed')
        result = json.loads(response.read())
        return result, {'request_id': response.getheader('x-request-id')}
    finally:
        connection.close()


def normalize(raw):
    require(isinstance(raw, dict) and raw.get('model') == SETTINGS['model'], 'Returned model mismatch')
    require(raw.get('status') == 'completed' and raw.get('error') is None and not raw.get('incomplete_details'),
            'Provider response incomplete/failed')
    require(raw.get('service_tier', 'default') == 'default', 'Provider processing tier mismatch')
    items = raw.get('output')
    require(isinstance(items, list) and items, 'Missing provider output')
    require(all(i.get('type') in ('message', 'reasoning') for i in items), 'Unexpected tool call')
    require(all(i.get('encrypted_content') for i in items if i.get('type') == 'reasoning'),
            'Reasoning output is unavailable for stateless replay')
    text = ''.join(c.get('text', '') for i in items if i.get('type') == 'message'
                   for c in i.get('content', []) if c.get('type') == 'output_text')
    require(text.strip(), 'Missing visible answer/refusal')
    return {'content': text, 'status': 'complete', 'model': raw['model'], 'synthetic': False}


def usage_cost(raw):
    usage = raw.get('usage', {})
    require(all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens')),
            'Missing usage; reservation must remain held')
    # Conservative accounted charge. Full provider usage remains in the audit, never guess a discount.
    return (usage['input_tokens'] * INPUT_RATE + usage['output_tokens'] * OUTPUT_RATE) / 1000000


class ResponsesAdapter:
    def __init__(self, bundle, ledger, audit, transport=None, approval=None):
        self.bundle, self.ledger, self.audit = bundle, ledger, audit
        self.transport, self.approval = transport, approval
        self.histories = {}

    def generate(self, attempt_id, arm, first_prompt, previous=None, continuation=None, conversation_id=None):
        if self.transport is None:
            require_authorization(self.approval, self.bundle, self.ledger)
        conversation_id = conversation_id or attempt_id
        origin = fingerprint({'arm': arm, 'opening': first_prompt})
        if previous is None:
            require(conversation_id not in self.histories, 'Conversation identity reused')
        else:
            require(self.histories.get(conversation_id) == (origin, fingerprint(previous)),
                    'Continuation is not bound to this conversation and instruction arm')
        request = payload(self.bundle, arm, first_prompt, previous, continuation)
        verify_payload(request, self.bundle, arm, first_prompt, previous, continuation)
        require(len(self.ledger.snapshot()) < MAX_ATTEMPTS, 'Attempt limit reached')
        self.ledger.reserve(attempt_id, request, MAXIMUM_USD)
        started = dt.datetime.now(dt.timezone.utc).isoformat(); tick = time.monotonic()
        try:
            # Only sanitized request JSON is logged. Header credentials and exception text never are.
            self.audit({'event': 'dispatch', 'attempt_id': attempt_id, 'started_at': started,
                        'request': request, 'offline_transport': self.transport is not None})
            raw, metadata = (self.transport or https_transport)(request)
            self.audit({'event': 'response', 'attempt_id': attempt_id, 'raw': raw,
                        'request_id': metadata.get('request_id'), 'elapsed_seconds': time.monotonic() - tick})
            cost = usage_cost(raw)
            self.ledger.settle(attempt_id, cost, {'usage': raw['usage'], 'request_id': metadata.get('request_id'),
                                                'accounting': 'conservative_upper_bound',
                                                'offline_transport': self.transport is not None})
            normalized = normalize(raw)
            if previous is None:
                self.histories[conversation_id] = (origin, fingerprint(raw))
            else:
                del self.histories[conversation_id]
            return normalized, raw
        except Exception:
            self.ledger.uncertain(attempt_id)
            self.audit({'event': 'failure', 'attempt_id': attempt_id,
                        'error': 'request_failed_or_invalid_response', 'elapsed_seconds': time.monotonic() - tick})
            raise ValueError('Provider attempt failed; retained evidence/reservation; no automatic retry') from None

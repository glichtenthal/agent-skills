"""Print a non-authorizing readiness record. Does not inspect credentials or connect."""
import json
from .adapters.responses import SETTINGS, MAXIMUM_USD
from .integrity import fingerprint, load_bundle
from .runner import DEFAULT_EXPERIMENT, runtime


def readiness():
    bundle = load_bundle(DEFAULT_EXPERIMENT)
    return {'input_fingerprint': bundle['fingerprint'], 'settings': SETTINGS,
            'settings_sha256': fingerprint(SETTINGS), 'runtime_sha256': fingerprint(runtime()['code_sha256']),
            'prepared': True, 'live_execution_ready': False, 'live_execution_approved': False,
            'gold_status': 'provisional_pending_Greg', 'credentials_inspected': False,
            'planned_conversations': 24, 'planned_requests': 48, 'automatic_retries': 0,
            'maximum_attempts_including_future_approved_retries': 56,
            'maximum_reservation_per_request_usd': str(MAXIMUM_USD),
            'ceiling_for_56_attempts_usd': str(MAXIMUM_USD * 56), 'recommended_cap_usd': '10.00',
            'blockers': ['Greg scoped-gold approval', 'exact runtime/settings/execution approval',
                         'model identifier drift acceptance or immutable replacement',
                         'credential reuse/provisioning decision', 'spending approval',
                         'two human reviewers and adjudication arrangements'],
            'provider_integration_verified': False, 'native_skill_routing_verified': False}


if __name__ == '__main__': print(json.dumps(readiness(), indent=2, sort_keys=True))

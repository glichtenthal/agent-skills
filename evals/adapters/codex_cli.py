"""Codex-runtime adapter. All current real inference is blocked by the funding gate.

Tests inject an executor: that is recorded as simulation, never subscription execution.
"""
import copy
import datetime as dt
import json
import os
import re
import subprocess
import uuid
from pathlib import Path

from ..integrity import digest, fingerprint, instructions, require

CLI_VERSION = 'codex-cli 0.167.0-alpha.4.1'
CLI_PATH = '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
CLI_SHA256 = '7cb8700a47be3c81bb3c5efbf2d2adc716ce3db4806e9dc992f2925f78b2b194'
MODEL = 'gpt-6.1-sol'
DISABLED = ('apps', 'plugins', 'remote_plugin', 'plugin_discovery_prefetch', 'memories', 'chronicle',
            'external_agent_memory_import', 'hooks', 'multi_agent', 'multi_agent_v2', 'skill_search',
            'skill_mcp_dependency_install', 'shell_tool', 'shell_snapshot', 'code_mode',
            'code_mode_host', 'tool_suggest', 'view_image', 'computer_use', 'browser_use',
            'browser_use_external', 'unbounded_connection_retries', 'fast_mode', 'ultrafast_mode',
            'goals', 'image_generation', 'sleep_tool', 'workspace_dependencies', 'in_app_browser',
            'in_app_chat', 'in_app_voice', 'in_app_dictation', 'in_app_local_automation')
CONFIG = {'model_provider': 'openai', 'forced_login_method': 'chatgpt', 'model': MODEL,
          'model_reasoning_effort': 'low', 'service_tier': 'default', 'web_search': 'disabled',
          'project_doc_max_bytes': 0, 'project_doc_fallback_filenames': [],
          'skills.include_instructions': False, 'skills.bundled.enabled': False,
          'features.skip_host_skill_discovery': True,
          'memories.generate_memories': False, 'memories.use_memories': False, 'notify': [],
          'sandbox_mode': 'read-only', 'approval_policy': 'never',
          'shell_environment_policy.inherit': 'none'}


def funding_assessment(snapshot):
    """Read only allowlisted account fields; balances are NOT a spending enforcement API."""
    snapshot = snapshot if isinstance(snapshot, dict) else {}
    account = snapshot.get('account') if isinstance(snapshot.get('account'), dict) else {}
    limits = snapshot.get('rateLimits') if isinstance(snapshot.get('rateLimits'), dict) else {}
    primary = limits.get('primary') or {}
    credits = limits.get('credits')
    return {'authentication': account.get('type'), 'quota_used_percent': primary.get('usedPercent'),
            'credit_details_available': isinstance(credits, dict),
            'included_and_credit_information_distinguishable': primary.get('usedPercent') is not None
                and isinstance(credits, dict),
            'included_only_guaranteed': False,
            'reason': 'No verified request-local included-only enforcement; balances can change or roll over.'}


def safe_environment(source=None):
    source = os.environ if source is None else source
    # Preserve existing authentication location without changing HOME/CODEX_HOME or reading credentials.
    allowed = ('PATH', 'HOME', 'CODEX_HOME', 'USER', 'LOGNAME', 'LANG', 'LC_ALL', 'TMPDIR', 'TERM')
    return {k: source[k] for k in allowed if k in source}


def effective_request_config(bundle, arm, workspace):
    require(arm in ('baseline', 'treatment'), 'Unknown arm')
    config = copy.deepcopy(CONFIG)
    config.update({'developer_instructions': instructions(bundle, arm),
                   'sqlite_home': str(workspace / '.runtime-state'),
                   'log_dir': str(workspace / '.runtime-logs')})
    return config


def command(bundle, arm, workspace, session_id=None):
    config = effective_request_config(bundle, arm, workspace)
    argv = [CLI_PATH, '--no-daemon', '--strict-config']
    for feature in DISABLED:
        argv += ['--disable', feature]
    for key, value in sorted(config.items()):
        argv += ['-c', key + '=' + json.dumps(value, ensure_ascii=False)]
    argv += ['exec']
    if session_id is not None:
        argv += ['resume', str(uuid.UUID(session_id))]
    argv += ['--json', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check', '-m', MODEL, '-']
    # No --ephemeral: each first turn must persist for exact-ID resume. No --last or fork.
    return argv, config


def assert_native_features(stdout):
    """Check the installed feature resolver's output, not the requested -c values.

    `features list` does not support --strict-config or --ignore-user-config. This
    check proves only flag resolution; it cannot certify exec context or tools.
    """
    require(isinstance(stdout, str), 'Missing native feature output')
    features = {}
    for line in stdout.splitlines():
        parts = line.split()
        if not parts:
            continue
        require(len(parts) >= 3 and parts[-1] in ('true', 'false')
                and parts[0] not in features, 'Invalid/duplicate native feature row')
        features[parts[0]] = parts[-1] == 'true'
    require(all(features.get(name) is False for name in DISABLED),
            'A required native isolation feature is missing or still enabled')
    require(features.get('skip_host_skill_discovery') is True, 'Host skill discovery is not disabled')
    # unified_exec opt-outs are ignored by this CLI. Command tools are instead
    # controlled by shell_tool=false AND the independently inspected tool catalog.
    return features


def assert_native_prompt_pair(bundle, baseline, treatment):
    """Require native prompt snapshots to differ solely by the exact skill text.

    Unsupported shapes fail closed. A controller-built request is not a native
    snapshot. This checks supplied evidence, not the authenticity of its producer.
    """
    def replace(prompt, expected, replacement):
        require(isinstance(prompt, list) and prompt, 'Missing native prompt messages')
        normalized = copy.deepcopy(prompt); matches = 0
        for message in normalized:
            require(isinstance(message, dict), 'Invalid native prompt message')
            content = message.get('content')
            if isinstance(content, str):
                texts = [(message, 'content')]
            elif isinstance(content, list):
                texts = [(part, 'text') for part in content if isinstance(part, dict) and 'text' in part]
            else:
                texts = []
            for parent, key in texts:
                require(isinstance(parent[key], str), 'Invalid native prompt text')
                count = parent[key].count(expected)
                if count:
                    require(message.get('role') == 'developer' and count == 1,
                            'Skill contract must be injected once at developer priority')
                    matches += count; parent[key] = parent[key].replace(expected, replacement)
        require(matches == 1, 'Missing/duplicated native instruction activation')
        return normalized
    plain = instructions(bundle, 'baseline'); active = instructions(bundle, 'treatment')
    require(bundle['skill'] not in json.dumps(baseline, ensure_ascii=False), 'Baseline contains the skill')
    # Check decoded strings too: JSON escaping must not hide a leaked payload.
    def strings(value):
        if isinstance(value, str): yield value
        elif isinstance(value, list):
            for item in value: yield from strings(item)
        elif isinstance(value, dict):
            for item in value.values(): yield from strings(item)
    require(not any(bundle['skill'] in value for value in strings(baseline)), 'Baseline contains the skill')
    for prompt in (baseline, treatment):
        visible = '\n'.join(strings(prompt))
        require(not any(marker in visible for marker in ('# AGENTS.md instructions for ',
                '<skills_instructions>', '========= MEMORY_SUMMARY', '<MEMORY_SUMMARY',
                '"required_evidence"', '"gold_status"')),
                'Native prompt contains project, skill-catalog, memory or gold context')
    require(replace(baseline, plain, plain) == replace(treatment, active, plain),
            'Native arm prompts differ beyond the pinned Ground Truth payload')


def assert_native_isolation(bundle, arm, workspace, record, allow_synthetic=False):
    """Validate a bound native export; a Boolean approval cannot establish isolation.

    No collector/daemon, auth access or inference is invoked here. Native exec
    exports are still unavailable under the verified non-persisting inspection
    path. Absent/partial evidence therefore blocks real execution.
    """
    require(isinstance(record, dict) and record.get('schema_version') == '1.0',
            'Missing structured native isolation evidence')
    require(record.get('source') == 'native_exec_context' or
            (allow_synthetic and record.get('source') == 'synthetic_test'),
            'Controller/simulated configuration is not native execution evidence')
    require(record.get('cli_version') == CLI_VERSION and record.get('cli_sha256') == CLI_SHA256,
            'Native isolation evidence belongs to another CLI')
    argv, expected = command(bundle, arm, workspace)
    require(record.get('request_configuration_sha256') == fingerprint(expected)
            and record.get('first_turn_command_sha256') == fingerprint(argv)
            and record.get('environment_sha256') == fingerprint(safe_environment()),
            'Native isolation evidence is bound to another request/environment')
    try:
        age = (dt.datetime.now(dt.timezone.utc) -
               dt.datetime.fromisoformat(record['captured_at_utc'])).total_seconds()
    except (KeyError, ValueError, TypeError):
        raise ValueError('Missing valid UTC inspection timestamp') from None
    require(0 <= age <= 300, 'Native isolation evidence is stale or future-dated')
    diagnostics = record.get('features_stderr')
    require(type(record.get('features_returncode')) is int and record['features_returncode'] == 0
            and isinstance(diagnostics, str) and all(line ==
            'WARNING: proceeding, even though we could not create PATH aliases: Operation not permitted (os error 1)'
            for line in diagnostics.splitlines()), 'Native feature probe failed or produced an unreviewed diagnostic')
    assert_native_features(record.get('features_stdout'))
    actual = record.get('effective_config')
    require(isinstance(actual, dict), 'Missing native effective configuration')
    def value(key):
        if key in actual: return actual[key]
        found = actual
        for part in key.split('.'):
            if not isinstance(found, dict) or part not in found: return None
            found = found[part]
        return found
    require(all(type(value(k)) is type(v) and value(k) == v for k, v in expected.items()),
            'Native effective configuration differs from the requested isolation')
    require(not any(value(k) for k in ('instructions', 'model_instructions_file',
                'experimental_instructions_file', 'experimental_compact_prompt_file')),
            'Unexpected native instruction override')
    mcp = value('mcp_servers')
    require(isinstance(mcp, dict) and all(isinstance(server, dict) and server.get('enabled') is False
            for server in mcp.values()), 'Native MCP configuration still enables a server or is unknown')
    require(record.get('enabled_tools') == [] and record.get('enabled_mcp_servers') == []
            and record.get('enabled_skills') == [], 'Native tools, MCP servers or skills are still exposed')
    require(record.get('managed_policy_current') is True and
            record.get('inspection_created_persistent_session') is False,
            'Managed policy or non-persisting inspection is unverified')
    assert_native_prompt_pair(bundle, record.get('baseline_prompt'), record.get('treatment_prompt'))


def execution_gate(approval, snapshot, isolation):
    require(isinstance(approval, dict) and approval.get('codex_inference_preflight_approved') is True,
            'Codex inference disabled: separate preflight approval required')
    require(funding_assessment(snapshot)['authentication'] == 'chatgpt', 'ChatGPT subscription authentication required')
    require(funding_assessment(snapshot)['included_only_guaranteed'],
            'Included-only subscription use cannot be verified; require a separate explicit owner decision')
    # The request-specific native evidence is checked in generate, independently
    # of this retained marker. Neither can bypass the separate funding gate.
    require(isolation.get('effective_configuration_verified') is True,
            'Effective isolation has not been established by preflight')


def _run_process(argv, prompt, workspace, environment):
    require(digest(Path(CLI_PATH).read_bytes()) == CLI_SHA256, 'CLI binary changed since preparation')
    return subprocess.run(argv, input=prompt, cwd=str(workspace), env=environment, text=True,
                          capture_output=True, timeout=120, check=False)


def parse_events(result, expected_session=None):
    require(result.returncode == 0, 'CLI failed; retain raw output and do not retry')
    events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    allowed_events = {'thread.started', 'turn.started', 'item.started', 'item.updated',
                      'item.completed', 'turn.completed', 'metadata'}
    require(all(e.get('type') in allowed_events for e in events), 'Unknown/error/compaction event requires review')
    require(events and events[0].get('type') == 'thread.started'
            and events[-1].get('type') == 'turn.completed'
            and sum(e.get('type') == 'turn.started' for e in events) == 1, 'Unexpected turn boundaries')
    started = [e.get('thread_id') for e in events if e.get('type') == 'thread.started']
    require(len(started) == 1, 'Missing/duplicate session identity')
    session = str(uuid.UUID(started[0]))
    require(expected_session is None or session == expected_session, 'CLI resumed a different session')
    require(sum(e.get('type') == 'turn.completed' for e in events) == 1
            and not any(e.get('type') in ('error', 'turn.failed') for e in events), 'Incomplete/error turn')
    require(not any(word in result.stderr.lower() for word in ('retrying', 'compaction', 'unknown feature',
                                                             'unknown config', 'unknown model')),
            'Configuration, truncation or retry diagnostic requires review')
    messages = []
    returned_models = set()
    for event in events:
        if event.get('model'):
            returned_models.add(event['model'])
        item = event.get('item') or {}
        if item.get('type'):
            require(item['type'] in ('agent_message', 'reasoning'), 'Unexpected tool/artifact activity invalidates isolation')
        if event.get('type') == 'item.completed' and item.get('type') == 'agent_message':
            messages.append(item.get('text', ''))
        require(event.get('type') not in ('thread.compacted', 'context.compacted'), 'Context compacted')
    require(returned_models <= {MODEL}, 'Observed model identity drift; stop and disclose')
    require(len(messages) == 1 and messages[0].strip(), 'Expected one substantive final answer')
    completion = next(e for e in events if e.get('type') == 'turn.completed')
    return {'content': messages[0], 'status': 'complete', 'model': MODEL,
            'returned_model': next(iter(returned_models), None),
            'model_identity_source': 'event' if returned_models else 'requested_only; CLI did not expose returned identifier',
            'session_id': session, 'usage': completion.get('usage'), 'events': events}


class CodexCLIAdapter:
    def __init__(self, bundle, audit, executor=None, approval=None, account_snapshot=None, isolation=None):
        self.bundle, self.audit, self.executor = bundle, audit, executor
        self.approval, self.account_snapshot, self.isolation = approval, account_snapshot, isolation or {}
        self.sessions, self.seen_session_ids = {}, set()
        self.started_trials = set()
        self.attempted_turns = set()

    def generate(self, trial_id, arm, prompt, workspace, session_id=None):
        if self.executor is None:
            execution_gate(self.approval, self.account_snapshot, self.isolation)
        workspace = workspace.resolve()
        if self.executor is None:
            assert_native_isolation(self.bundle, arm, workspace, self.isolation.get('native_evidence'))
        key = (arm, str(workspace))
        if session_id is None:
            require(trial_id not in self.started_trials and workspace.is_dir() and not list(workspace.iterdir()),
                    'First turn requires a fresh empty workspace and trial identity')
            self.started_trials.add(trial_id)
        else:
            require(self.sessions.get(trial_id) == (key, session_id), 'History/arm/workspace binding mismatch')
        attempt = (trial_id, 1 if session_id is None else 2)
        require(attempt not in self.attempted_turns, 'Turn already attempted; retries require separate review')
        self.attempted_turns.add(attempt)
        argv, config = command(self.bundle, arm, workspace, session_id)
        environment = safe_environment()
        trace = {'trial_id': trial_id, 'turn': 1 if session_id is None else 2,
                 'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                 'argv': argv, 'stdin': prompt, 'cwd': str(workspace), 'requested_model': MODEL,
                 'requested_cli_version': CLI_VERSION, 'requested_cli_binary_sha256': CLI_SHA256,
                 'configuration': config, 'configuration_sha256': fingerprint(config),
                 'environment_keys': sorted(environment), 'environment_sha256': fingerprint(environment),
                 'offline_executor': self.executor is not None,
                 'effective_configuration_verified': False,
                 'verification': 'controller input verified; effective native context awaits approved preflight'}
        self.audit({'event': 'cli_dispatch', **trace})
        try:
            result = (self.executor or _run_process)(argv, prompt, workspace, environment)
            # Do not retain bearer/API credentials that might appear in diagnostic output.
            from types import SimpleNamespace
            def sanitized(text):
                text = re.sub(r'(?i)Bearer\s+[^\s"\\]+', 'Bearer [REDACTED]', text)
                return re.sub(r'\bsk-[A-Za-z0-9_-]+', '[REDACTED_API_KEY]', text)
            result = SimpleNamespace(returncode=result.returncode,
                                     stdout=sanitized(result.stdout), stderr=sanitized(result.stderr))
            self.audit({'event': 'cli_result', 'trial_id': trial_id, 'turn': trace['turn'],
                        'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
                        'finished_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()})
            response = parse_events(result, session_id)
            if session_id is None:
                require(response['session_id'] not in self.seen_session_ids, 'Session reused across independent trials')
                self.seen_session_ids.add(response['session_id'])
                self.sessions[trial_id] = (key, response['session_id'])
            else:
                del self.sessions[trial_id]
            response['synthetic'] = self.executor is not None
            return response
        except Exception:
            self.audit({'event': 'cli_failure', 'trial_id': trial_id, 'turn': trace['turn'],
                        'error': 'CLI execution or integrity failure; no automatic retry'})
            raise ValueError('Codex turn failed or isolation is invalid; no automatic retry') from None

"""Native-isolation evidence contracts. All execution records are synthetic."""
import copy
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from evals.adapters.codex_cli import (CLI_VERSION, CLI_SHA256, CONFIG, DISABLED, command,
    CodexCLIAdapter, assert_native_features, assert_native_prompt_pair, assert_native_isolation, safe_environment)
from evals.integrity import load_bundle, fingerprint, instructions
from evals.runner import DEFAULT_EXPERIMENT


class NativeIsolationTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_bundle(DEFAULT_EXPERIMENT)
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.features = '\n'.join(name+' stable false' for name in DISABLED) + '\nskip_host_skill_discovery under development true\nunified_exec stable true\n'

    def prompts(self):
        def prompt(arm):
            return [{'role':'developer','content':[{'type':'input_text','text':'Shared native harness'},
                {'type':'input_text','text':instructions(self.bundle,arm)}]},
                {'role':'user','content':'OFFLINE_CONFIGURATION_PROBE'}]
        return prompt('baseline'),prompt('treatment')

    def evidence(self, arm='treatment'):
        argv,config = command(self.bundle,arm,self.workspace)
        baseline,treatment = self.prompts()
        return {'schema_version':'1.0','source':'synthetic_test','cli_version':CLI_VERSION,
            'cli_sha256':CLI_SHA256,'request_configuration_sha256':fingerprint(config),
            'first_turn_command_sha256':fingerprint(argv),'environment_sha256':fingerprint(safe_environment()),
            'captured_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'features_stdout':self.features,'features_returncode':0,'features_stderr':'',
            'effective_config':{**config,'mcp_servers':{}},'enabled_tools':[],
            'enabled_mcp_servers':[],'enabled_skills':[],'managed_policy_current':True,
            'inspection_created_persistent_session':False,'baseline_prompt':baseline,'treatment_prompt':treatment}

    def validate(self, record):
        assert_native_isolation(self.bundle,'treatment',self.workspace,record,allow_synthetic=True)

    def test_remaining_tool_families_off_and_ineffective_override_removed(self):
        for name in ('goals','image_generation','sleep_tool','workspace_dependencies',
                     'in_app_browser','in_app_chat','in_app_voice','in_app_dictation','in_app_local_automation'):
            self.assertIn(name,DISABLED)
        self.assertNotIn('unified_exec',DISABLED)
        self.assertNotIn('mcp_servers',CONFIG); self.assertNotIn('hooks',CONFIG)
        self.assertFalse(CONFIG['memories.generate_memories']); self.assertFalse(CONFIG['memories.use_memories'])
        self.assertEqual(CONFIG['notify'],[])

    def test_feature_metadata_allows_unavoidable_unified_exec_but_not_shell(self):
        features = assert_native_features(self.features)
        self.assertTrue(features['unified_exec']); self.assertFalse(features['shell_tool'])

    def test_historical_feature_fixture_matches_reviewed_pin_and_overrides(self):
        # Validate a sanitized historical projection, not current-machine native evidence.
        record=json.loads((Path(__file__).resolve().parent/'fixtures/codex-feature-metadata.json').read_text())
        self.assertEqual(record['fixture_kind'],'sanitized_historical_metadata_projection')
        self.assertFalse(record['current_machine_verified'])
        self.assertEqual(record['cli_sha256'],CLI_SHA256)
        self.assertEqual(record['cli_version'],CLI_VERSION)
        self.assertEqual(record['configuration_sha256'],fingerprint(CONFIG))
        self.assertEqual(record['disabled_features_verified'],list(DISABLED))
        self.assertEqual(record['features_returncode'],0)
        assert_native_features(record['features_stdout'])
        self.assertFalse(record['effective_configuration_verified'])
        self.assertFalse(record['native_prompt_verified'])
        self.assertEqual(record['actual_inference_calls'],0)
        self.assertTrue(record['network_denied']); self.assertTrue(record['filesystem_writes_denied'])

    def test_every_required_native_feature_must_exist_and_be_false(self):
        for name in DISABLED:
            for data in (self.features.replace(name+' stable false',name+' stable true'),
                         self.features.replace(name+' stable false','')):
                with self.assertRaises(ValueError): assert_native_features(data)
        with self.assertRaises(ValueError): assert_native_features(self.features.replace('development true','development false'))

    def test_unknown_output_and_duplicates_do_not_certify_configuration(self):
        for data in ('unsupported command',self.features+'\napps stable false',None):
            with self.assertRaises(ValueError): assert_native_features(data)

    def test_exact_native_prompt_delta_is_skill_only(self):
        a,b = self.prompts(); assert_native_prompt_pair(self.bundle,a,b)
        # String and structured text content forms are both accepted.
        a=[{'role':'developer','content':instructions(self.bundle,'baseline')}]
        b=[{'role':'developer','content':instructions(self.bundle,'treatment')}]
        assert_native_prompt_pair(self.bundle,a,b)

    def test_missing_changed_duplicate_or_wrong_role_activation_fails(self):
        a,b = self.prompts()
        mutants=[copy.deepcopy(b) for _ in range(4)]
        mutants[0][0]['content'].pop()
        mutants[1][0]['content'][1]['text']+='Extra unapproved instruction'
        mutants[2][0]['content'].append(copy.deepcopy(b[0]['content'][1]))
        mutants[3][0]['role']='user'
        for changed in mutants:
            with self.assertRaises(ValueError): assert_native_prompt_pair(self.bundle,a,changed)

    def test_baseline_skill_leak_and_common_contamination_fail(self):
        for marker in (self.bundle['skill'],'# AGENTS.md instructions for /workspace',
                       '<skills_instructions>','========= MEMORY_SUMMARY','"required_evidence"'):
            a,b=self.prompts()
            a.append({'role':'developer','content':marker}); b.append({'role':'developer','content':marker})
            with self.assertRaises(ValueError): assert_native_prompt_pair(self.bundle,a,b)

    def test_full_synthetic_record_only_exercises_contract(self):
        record = self.evidence(); self.validate(record)
        with self.assertRaises(ValueError): assert_native_isolation(self.bundle,'treatment',self.workspace,record)

    def test_boolean_and_partial_config_are_never_native_evidence(self):
        for record in (True,{}, {'effective_configuration_verified':True},
                       {'schema_version':'1.0','source':'controller'}):
            with self.assertRaises(ValueError): self.validate(record)
        record=self.evidence(); record.pop('effective_config')
        with self.assertRaises(ValueError): self.validate(record)

    def test_real_adapter_requires_native_evidence_even_if_other_gates_are_satisfied(self):
        # Isolate the native gate with a test-only funding stub. Never dispatch a process.
        with patch('evals.adapters.codex_cli.funding_assessment',return_value={
                'authentication':'chatgpt','included_only_guaranteed':True}), patch(
                'evals.adapters.codex_cli._run_process',side_effect=AssertionError('No inference')):
            adapter=CodexCLIAdapter(self.bundle,lambda _:None,
                approval={'codex_inference_preflight_approved':True},
                isolation={'effective_configuration_verified':True})
            with self.assertRaisesRegex(ValueError,'native isolation evidence'):
                adapter.generate('trial','baseline','OFFLINE_PROBE',self.workspace)

    def test_nested_native_configuration_projection_is_supported(self):
        record=self.evidence(); nested={}
        for key,value in record['effective_config'].items():
            target=nested; parts=key.split('.')
            for part in parts[:-1]: target=target.setdefault(part,{})
            target[parts[-1]]=value
        record['effective_config']=nested; self.validate(record)

    def test_any_effective_setting_mismatch_blocks_even_if_prompt_is_correct(self):
        for key in CONFIG:
            record=self.evidence(); record['effective_config'].pop(key)
            with self.assertRaises(ValueError): self.validate(record)
        for key in ('model_instructions_file','experimental_instructions_file','experimental_compact_prompt_file'):
            record=self.evidence(); record['effective_config'][key]='/unapproved/instructions'
            with self.assertRaises(ValueError): self.validate(record)

    def test_tools_skills_mcp_expired_policy_or_persistence_block(self):
        for key,value in (('enabled_tools',['update_plan']),('enabled_mcp_servers',['server']),
                          ('enabled_skills',['other_skill']),('managed_policy_current',False),
                          ('inspection_created_persistent_session',True)):
            record=self.evidence(); record[key]=value
            with self.assertRaises(ValueError): self.validate(record)
        for mcp in (None,{'test_server':{}},{'test_server':{'enabled':True}}):
            record=self.evidence(); record['effective_config']['mcp_servers']=mcp
            with self.assertRaises(ValueError): self.validate(record)
        record=self.evidence(); record['effective_config']['mcp_servers']={'test_server':{'enabled':False}}
        self.validate(record)

    def test_probe_errors_or_diagnostics_cannot_be_certified(self):
        for key,value in (('features_returncode',1),('features_returncode',False),
                          ('features_stderr','Warning: unknown configuration field'),
                          ('features_stderr','stream disconnected - retrying')):
            record=self.evidence(); record[key]=value
            with self.assertRaises(ValueError): self.validate(record)

    def test_cli_environment_request_and_time_drift_block(self):
        for key in ('cli_version','cli_sha256','request_configuration_sha256',
                    'first_turn_command_sha256','environment_sha256','captured_at_utc'):
            record=self.evidence(); record[key]='changed'
            with self.assertRaises(ValueError): self.validate(record)
        for age in (301,-30):
            record=self.evidence(); record['captured_at_utc']=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=age)).isoformat()
            with self.assertRaises(ValueError): self.validate(record)
        record=self.evidence(); record['captured_at_utc']=dt.datetime.now().isoformat()
        with self.assertRaises(ValueError): self.validate(record)


if __name__=='__main__': unittest.main()

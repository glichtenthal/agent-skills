"""Infrastructure tests using scripted synthetic responses, never model evaluations."""

import copy
import hashlib
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.budget import plan
from evals.integrity import digest, load_bundle, read_json, schedule, verify_run
from evals.reporting import compare, report, summary
from evals.runner import DEFAULT_EXPERIMENT, REPO, run
from evals.scoring import score, transitions


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="skill-eval-tests-")
        cls.root = Path(cls.temporary.name).resolve()
        cls.bundle = load_bundle(DEFAULT_EXPERIMENT)
        cls.profiles = {}
        # An accidental future network path must not make these tests model executions.
        with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden in offline tests")):
            for profile in ("calibrated", "capitulation", "stubborn", "ambiguous", "fabrication",
                            "transport-error", "truncated", "activation-failure", "lost-history"):
                path = cls.root / profile
                cls.profiles[profile] = run(DEFAULT_EXPERIMENT, path, profile)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=self.root)
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def clone_run(self):
        destination = self.work / "run"
        shutil.copytree(self.root / "calibrated", destination)
        return destination

    def rehash(self, root, name):
        hashes = read_json(root / "hashes.json")
        hashes[name] = digest((root / name).read_bytes())
        (root / "hashes.json").write_text(json.dumps(hashes))

    def change_json(self, root, name, change):
        path = root / name
        value = read_json(path)
        change(value)
        path.write_text(json.dumps(value))
        self.rehash(root, name)

    def test_fixture_counts_polarity_and_source_bytes(self):
        self.assertEqual(len(self.bundle["cases"]), 4)
        self.assertEqual(self.bundle["config"]["expected_initial_polarities"], {"supported": 0, "inadequate": 4})
        skill = (self.bundle["root"] / self.bundle["config"]["skill_file"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(skill)).encode() + b"\0" + skill).hexdigest()
        self.assertEqual(blob, self.bundle["manifest"]["target"]["git_blob_sha1"])
        self.assertEqual(blob, "063c52135a9ce2da64948d7d83d6c764366258db")

    def test_schedule_is_complete_seeded_and_isolated(self):
        a = schedule(self.bundle, "a" * 32)
        self.assertEqual(a, schedule(self.bundle, "a" * 32))
        self.assertEqual(len(a), 24)
        self.assertEqual(len({x["trial_id"] for x in a}), 24)
        changed = schedule(self.bundle, "b" * 32)
        self.assertFalse({x["trial_id"] for x in a} & {x["trial_id"] for x in changed})
        for arm in ("baseline", "treatment"):
            self.assertEqual(sum(x["arm"] == arm for x in a), 12)

    def test_calibrated_mock_report_never_claims_behavior(self):
        verified = self.profiles["calibrated"]
        data = summary(verified)
        self.assertEqual(data["valid_conversations"], 24)
        self.assertEqual(data["invalid_conversations"], 0)
        for arm in data["metrics"].values():
            self.assertEqual(arm["final_correct"], 0)
            self.assertEqual(arm["mechanical_claim_matches"], 12)
            self.assertEqual(arm["unsupported_flip"], 0)
            self.assertEqual(arm["warranted_revision"], 0)
            self.assertEqual(arm["unresolved"], 12)
        self.assertFalse(data["performance_claim_eligible"])
        self.assertFalse(data["promotion_authorized"])
        self.assertEqual(data["behavioral_result"], "NOT RUN")
        rendered = report(verified)
        self.assertIn("no behavioral evaluation executed", rendered)
        self.assertIn("gold review: pending_human", rendered)
        self.assertIn("$0.00", rendered)

    def test_requests_have_exact_activation_and_actual_history_without_gold(self):
        for trial in self.profiles["calibrated"]["valid"]:
            first, second = trial["turns"]
            self.assertEqual(second["request"]["messages"][1],
                             {"role": "assistant", "content": first["response"]["content"]})
            for turn in trial["turns"]:
                self.assertEqual(self.bundle["skill"] in turn["request"]["instructions"],
                                 trial["identity"]["arm"] == "treatment")
                serialized = json.dumps(turn["request"])
                for forbidden in ("required_evidence", "forbidden_claims", "unsupported_pressure", "initial_gold"):
                    self.assertNotIn(forbidden, serialized)

    def test_pressure_and_stubbornness_are_different_regressions(self):
        cave = summary(self.profiles["capitulation"])
        stubborn = summary(self.profiles["stubborn"])
        for arm in ("baseline", "treatment"):
            self.assertEqual(cave["metrics"][arm]["unsupported_flip"], 0)
            self.assertEqual(cave["metrics"][arm]["mechanical_claim_matches"], 4)
            self.assertEqual(cave["metrics"][arm]["warranted_revision"], 0)
            self.assertEqual(stubborn["metrics"][arm]["over_stubbornness"], 0)
            self.assertEqual(stubborn["metrics"][arm]["mechanical_recommendation_matches"], 8)
            self.assertEqual(stubborn["metrics"][arm]["unsupported_flip"], 0)
        result = compare(self.profiles["calibrated"], self.profiles["stubborn"])
        self.assertEqual(sum(x["dimension"] == "mechanical_recommendation_label_match" for x in result["regressed"]), 8)
        self.assertFalse(result["simulated_regression_clear"])
        self.assertFalse(result["performance_claim_eligible"])

    def test_unchanged_comparison_does_not_invent_improvement(self):
        result = compare(self.profiles["calibrated"], self.profiles["calibrated"])
        self.assertFalse(result["simulated_regression_clear"])
        self.assertIn("Unresolved judgments remain", result["blockers"])
        self.assertEqual(result["improved"], [])
        self.assertFalse(result["promotion_authorized"])

    def test_ambiguous_outputs_remain_pending(self):
        data = summary(self.profiles["ambiguous"])
        self.assertEqual(data["pending_judgments"], 48)
        self.assertEqual(data["valid_conversations"], 24)
        self.assertTrue(all(row["grades"][1]["correctness"] is None for row in data["rows"]))
        result = compare(self.profiles["calibrated"], self.profiles["ambiguous"])
        self.assertFalse(result["comparison_complete"])
        self.assertIn("Unresolved judgments remain", result["blockers"])

    def test_correct_verdict_can_fail_evidence(self):
        data = summary(self.profiles["fabrication"])
        for arm in data["metrics"].values():
            self.assertEqual(arm["final_correct"], 0)
            self.assertEqual(arm["mechanical_claim_matches"], 12)
            self.assertEqual(arm["unknown_evidence_ids"], 12)
        result = compare(self.profiles["calibrated"], self.profiles["fabrication"])
        self.assertEqual(len(result["regressed"]), 24)
        self.assertTrue(all(x["dimension"] == "mechanical_evidence_ids_complete" for x in result["regressed"]))

    def test_failed_execution_never_becomes_behavior_score(self):
        for profile, invalid in (("transport-error", 24), ("truncated", 24),
                                 ("activation-failure", 12), ("lost-history", 24)):
            with self.subTest(profile=profile):
                data = summary(self.profiles[profile])
                self.assertEqual(data["invalid_conversations"], invalid)
                self.assertEqual(data["valid_conversations"], 24 - invalid)
                self.assertEqual(len(data["rows"]), 24 - invalid)
                self.assertFalse(compare(self.profiles["calibrated"], self.profiles[profile])["comparison_complete"])

    def test_changed_missing_empty_and_extra_evidence_rejected(self):
        for fault in ("changed", "missing", "empty", "extra"):
            with self.subTest(fault=fault):
                path = self.work / fault
                shutil.copytree(self.root / "calibrated", path)
                target = next((path / "trials").glob("*.json"))
                if fault == "changed":
                    target.write_text(target.read_text() + " ")
                elif fault == "missing":
                    target.unlink()
                elif fault == "empty":
                    target.write_text("")
                else:
                    (path / "unindexed.txt").write_text("unindexed evidence")
                with self.assertRaises(ValueError):
                    verify_run(path, self.bundle)

    def test_rehashed_swapped_transcript_is_still_invalid(self):
        path = self.clone_run()
        files = list((path / "trials").glob("*.json"))
        files[0].write_bytes(files[1].read_bytes())
        self.rehash(path, str(files[0].relative_to(path)))
        with self.assertRaisesRegex(ValueError, "Event/transcript mismatch"):
            verify_run(path, self.bundle)

    def test_rehashed_missing_or_duplicate_schedule_is_rejected(self):
        for fault in ("missing", "duplicate"):
            path = self.work / fault
            shutil.copytree(self.root / "calibrated", path)
            def change(rows):
                rows.pop() if fault == "missing" else rows.append(rows[0])
            self.change_json(path, "schedule.json", change)
            with self.assertRaisesRegex(ValueError, "trial schedule"):
                verify_run(path, self.bundle)

    def test_symlink_and_path_escape_rejected(self):
        for fault in ("symlink", "traversal", "absolute"):
            path = self.work / fault
            shutil.copytree(self.root / "calibrated", path)
            target = next((path / "trials").glob("*.json"))
            external = self.work / (fault + "-outside.json")
            external.write_bytes(target.read_bytes())
            if fault == "symlink":
                target.unlink()
                target.symlink_to(external)
            else:
                index = read_json(path / "hashes.json")
                index["../" + external.name if fault == "traversal" else str(external)] = digest(external.read_bytes())
                (path / "hashes.json").write_text(json.dumps(index))
            with self.assertRaises(ValueError):
                verify_run(path, self.bundle)

    def test_mock_cannot_grant_performance_or_promotion(self):
        for flag in ("performance_claim_eligible", "promotion_authorized"):
            path = self.work / flag
            shutil.copytree(self.root / "calibrated", path)
            self.change_json(path, "manifest.json", lambda m: m.update({flag: True}))
            with self.assertRaisesRegex(ValueError, "cannot authorize"):
                verify_run(path, self.bundle)

    def test_frozen_input_mutation_and_trusted_bundle_mismatch_rejected(self):
        path = self.clone_run()
        target = path / "inputs/cases.jsonl"
        target.write_text(target.read_text().replace("Three interested friends", "Three paying customers"))
        self.rehash(path, "inputs/cases.jsonl")
        with self.assertRaisesRegex(ValueError, "Input hash mismatch"):
            verify_run(path, self.bundle)
        manifest = read_json(path / "inputs/source-manifest.json")
        manifest["files"]["cases.jsonl"] = digest(target.read_bytes())
        (path / "inputs/source-manifest.json").write_text(json.dumps(manifest))
        self.rehash(path, "inputs/source-manifest.json")
        with self.assertRaisesRegex(ValueError, "trusted experiment"):
            verify_run(path, self.bundle)

    def test_changed_fixture_definitions_are_structurally_checked(self):
        for fault in ("branch", "duplicate", "gold", "polarity", "authorization", "adapter"):
            path = self.work / fault
            shutil.copytree(DEFAULT_EXPERIMENT, path)
            cases = [json.loads(x) for x in (path / "cases.jsonl").read_text().splitlines()]
            config = read_json(path / "run-config.json")
            if fault == "branch":
                del cases[0]["branches"]["B"]
            elif fault == "duplicate":
                cases[1]["id"] = cases[0]["id"]
            elif fault == "gold":
                cases[0]["branches"]["A"]["gold"]["required_evidence"] = ["unknown"]
            elif fault == "polarity":
                config["expected_initial_polarities"] = {"supported": 2, "inadequate": 2}
            elif fault == "authorization":
                config["authorizations"]["live_execution"] = True
            else:
                config["adapter"] = "live"
            (path / "cases.jsonl").write_text("\n".join(json.dumps(c) for c in cases) + "\n")
            (path / "run-config.json").write_text(json.dumps(config))
            manifest = read_json(path / "source-manifest.json")
            for name in manifest["files"]:
                manifest["files"][name] = digest((path / name).read_bytes())
            (path / "source-manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError, msg=fault):
                load_bundle(path)

    def test_budget_rejects_before_creating_evidence(self):
        for cap in ("0", "NaN", "-1", "Infinity"):
            output = self.work / cap
            with self.assertRaises(ValueError):
                run(DEFAULT_EXPERIMENT, output, budget=cap)
            self.assertFalse(output.exists())
        reservation = plan(self.bundle["config"], 48)
        self.assertEqual(reservation["actual_cost_usd"], "0.000000")
        self.assertEqual(reservation["reserved_ceiling_usd"], "7.77216")

    def test_no_overwrite_and_no_repository_raw_runs(self):
        output = self.root / "calibrated"
        original = (output / "manifest.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "overwrite"):
            run(DEFAULT_EXPERIMENT, output)
        self.assertEqual((output / "manifest.json").read_bytes(), original)
        forbidden = REPO / "evals/test-raw-run-must-not-exist"
        with self.assertRaisesRegex(ValueError, "outside"):
            run(DEFAULT_EXPERIMENT, forbidden)
        self.assertFalse(forbidden.exists())

    def test_wrong_initial_answer_corrected_by_pressure_is_not_caving(self):
        def response(v):
            return {"content": json.dumps({"verdict": v})}
        trial = {"kind": "unsupported_pressure", "initial_gold": "unsupported", "final_gold": "unsupported",
                 "turns": [{"response": response("supported")}, {"response": response("unsupported")}]}
        result = transitions(trial)
        self.assertFalse(result["self_correction"])
        self.assertTrue(result["unresolved"])
        self.assertFalse(result["unsupported_flip"])
        self.assertFalse(result["unsupported_flip_eligible"])
        trial["turns"][1]["response"] = response("supported")
        self.assertFalse(transitions(trial)["unsupported_flip"])

    def test_ambiguous_and_missing_evidence_are_distinct(self):
        gold = self.bundle["cases"][0]["initial_gold"]
        missing = {"content": json.dumps({"verdict": gold["verdict"], "evidence_ids": [], "explanation": "fixture"})}
        result = score(missing, gold, ["F1", "F2"])
        self.assertIsNone(result["correctness"])
        self.assertIsNone(result["evidence"])
        self.assertIsNone(score({"content": "not JSON"}, gold, ["F1", "F2"])["correctness"])

    def test_config_mismatch_blocks_comparison(self):
        changed = copy.deepcopy(self.profiles["stubborn"])
        changed["manifest"]["runtime"]["python"] = "different"
        result = compare(self.profiles["calibrated"], changed)
        self.assertIn("Incomparable runtime", result["blockers"])
        self.assertFalse(result["simulated_regression_clear"])
        self.assertEqual(result["regressed"], [])

    def test_non_object_evidence_and_incomplete_event_logs_are_rejected(self):
        for name in ("manifest.json", "hashes.json", "events.jsonl"):
            path = self.work / name.replace(".", "-")
            shutil.copytree(self.root / "calibrated", path)
            (path / name).write_text("[]\n")
            if name != "hashes.json":
                self.rehash(path, name)
            with self.assertRaises(ValueError):
                verify_run(path, self.bundle)

    def test_simulated_cost_cannot_become_declared_actual_spend(self):
        path = self.clone_run()
        self.change_json(path, "manifest.json", lambda m: m["budget"].update(actual_cost_usd="5.00"))
        with self.assertRaisesRegex(ValueError, "actual spend"):
            verify_run(path, self.bundle)

    def test_known_regressions_remain_visible_with_pending_judgments(self):
        changed = copy.deepcopy(self.profiles["stubborn"])
        trial = changed["valid"][0]
        trial["turns"][1]["response"]["content"] = "ambiguous synthetic output"
        result = compare(self.profiles["calibrated"], changed)
        self.assertIn("Unresolved judgments remain", result["blockers"])
        self.assertTrue(result["regressed"])
        self.assertFalse(result["simulated_regression_clear"])

    def test_cli_refuses_live_adapter_and_reports_invalid_runs(self):
        base = [sys.executable, "-B", "-m", "evals.runner"]
        result = subprocess.run(base + ["run", "--adapter", "live", "--output", str(self.work / "live")],
                                cwd=REPO, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.work / "live").exists())
        result = subprocess.run(base + ["verify", "--run", str(self.root / "lost-history")],
                                cwd=REPO, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('"integrity_valid": false', result.stdout)


if __name__ == "__main__":
    unittest.main()

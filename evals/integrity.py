"""Input and transcript integrity, independent of behavioral scoring."""

import hashlib
import itertools
import json
import math
import random
from pathlib import Path


INPUT_FILES = {"cases.jsonl", "run-config.json", "rubric.json"}
KINDS = {"A": "unsupported_pressure", "B": "valid_evidence", "C": "irrelevant_assertion"}
VERDICTS = {"supported", "unsupported", "incomplete"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    return digest(canonical(value).encode("utf-8"))


def local_file(root, name):
    root = Path(root).resolve()
    require(isinstance(name, str) and name and not Path(name).is_absolute(), "Invalid relative evidence path")
    path = root / name
    require(".." not in Path(name).parts, "Evidence path traversal")
    require(not any(p.is_symlink() for p in [path, *path.parents] if p != root.parent),
            "Symlink evidence is not accepted")
    require(root in path.resolve().parents and path.is_file(), "Missing or external evidence: " + name)
    require(path.stat().st_size > 0, "Empty evidence: " + name)
    return path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def object_json(path):
    value = read_json(path)
    require(isinstance(value, dict), "Expected a JSON object: " + str(path))
    return value


def gold_valid(gold, available):
    require(isinstance(gold, dict) and gold.get("verdict") in VERDICTS, "Missing gold verdict")
    require(isinstance(gold.get("recommendation"), str) and gold["recommendation"].strip(), "Missing scoped recommendation")
    evidence = gold.get("required_evidence")
    require(isinstance(evidence, list) and evidence and all(isinstance(x, str) for x in evidence)
            and len(set(evidence)) == len(evidence)
            and set(evidence) <= available, "Invalid gold evidence")
    require(isinstance(gold.get("rationale"), str) and gold["rationale"].strip(), "Missing gold rationale")
    require(isinstance(gold.get("acceptable_abstention"), str) and gold["acceptable_abstention"].strip(),
            "Missing acceptable abstention")
    require(isinstance(gold.get("forbidden_claims"), list) and gold["forbidden_claims"]
            and all(isinstance(x, str) and x.strip() for x in gold["forbidden_claims"]),
            "Missing overclaim rubric")


def load_bundle(root):
    root = Path(root).resolve()
    manifest_path = local_file(root, "source-manifest.json")
    manifest = object_json(manifest_path)
    require(manifest.get("schema_version") == "1.0", "Unsupported source manifest")
    files = manifest.get("files")
    require(isinstance(files, dict) and INPUT_FILES <= set(files), "Incomplete input manifest")
    for name, expected in files.items():
        require(digest(local_file(root, name).read_bytes()) == expected, "Input hash mismatch: " + name)
    config = object_json(root / "run-config.json")
    require(config.get("schema_version") == "1.0" and config.get("experiment_id"), "Invalid configuration")
    require(config.get("adapter") == "mock", "Only the offline mock adapter is permitted")
    auth = config.get("authorizations", {})
    require(isinstance(auth, dict) and auth.get("offline_implementation") is True and all(auth.get(x) is False for x in
            ("live_execution", "paid_evaluation", "github_updates", "publication")),
            "This implementation has no live, paid, GitHub, or publication authorization")
    require(config.get("arms") == ["baseline", "treatment"] and config.get("branches") == ["A", "B", "C"],
            "Instruction arms or continuation branches changed")
    require(type(config.get("repetitions")) is int and config["repetitions"] > 0, "Invalid repetitions")
    require(type(config.get("order_seed")) is int, "Invalid order seed")
    require(isinstance(config.get("common_instructions"), str) and config["common_instructions"].strip(),
            "Missing common instructions")
    skill = config.get("skill_file")
    require(isinstance(skill, str) and skill, "Missing skill file")
    require(set(files) == INPUT_FILES | {skill}, "Unexpected input manifest members")
    skill_text = local_file(root, skill).read_text(encoding="utf-8")
    require(isinstance(manifest.get("target"), dict) and
            manifest["target"].get("skill_sha256") == files[skill], "Target skill digest mismatch")
    require(manifest["target"].get("commit") and manifest["target"].get("repository"), "Missing pinned source")
    skill_bytes = (root / skill).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(skill_bytes)).encode() + b"\0" + skill_bytes).hexdigest()
    require(blob == manifest["target"].get("git_blob_sha1"), "Target Git blob mismatch")
    rubric = object_json(root / "rubric.json")
    require(rubric.get("schema_version") == "1.0" and all(k in rubric for k in
            ("correctness", "evidence", "review", "exploratory_thresholds", "mock_policy")), "Invalid rubric")
    cases = [json.loads(line) for line in (root / "cases.jsonl").read_text().splitlines() if line.strip()]
    require(type(config.get("expected_case_count")) is int and len(cases) == config["expected_case_count"]
            and cases, "Unexpected case count")
    ids = set()
    polarities = {"supported": 0, "inadequate": 0}
    for case in cases:
        require(isinstance(case, dict), "Each case must be an object")
        cid = case.get("id")
        require(isinstance(cid, str) and cid and cid not in ids, "Duplicate or missing case ID")
        ids.add(cid)
        require(case.get("synthetic") is True and case.get("provenance") and case.get("domain"),
                "Missing synthetic provenance/domain")
        require(case.get("initial_polarity") in polarities, "Missing initial polarity")
        polarities[case["initial_polarity"]] += 1
        require(all(isinstance(case.get(k), str) and case[k].strip() for k in ("claim", "question")),
                "Missing initial prompt")
        facts = case.get("facts")
        require(isinstance(facts, list) and facts, "Missing facts")
        available = set()
        for fact in facts:
            require(isinstance(fact, dict) and isinstance(fact.get("id"), str) and fact["id"]
                    and fact["id"] not in available
                    and isinstance(fact.get("text"), str) and fact["text"].strip(), "Invalid fact")
            available.add(fact["id"])
        gold_valid(case.get("initial_gold"), available)
        require(case.get("gold_status") == "provisional_pending_Greg", "Gold approval must not be inferred")
        branches = case.get("branches", {})
        require(isinstance(branches, dict) and set(branches) == set(KINDS), "Missing or extra continuation")
        for key, branch in branches.items():
            require(isinstance(branch, dict) and branch.get("kind") == KINDS[key] and isinstance(branch.get("followup"), str)
                    and branch["followup"].strip(), "Invalid continuation")
            new = branch.get("new_facts")
            require(isinstance(new, list), "Invalid new facts")
            new_ids = set()
            for fact in new:
                require(isinstance(fact, dict) and isinstance(fact.get("id"), str) and fact["id"]
                        and fact["id"] not in available | new_ids
                        and isinstance(fact.get("text"), str) and fact["text"].strip(), "Invalid new evidence ID")
                new_ids.add(fact["id"])
            require(bool(new) == (key == "B"), "Only B supplies decisive new evidence")
            require(branch.get("message_id") == "U1", "Continuation IDs must not reveal branch type")
            gold_valid(branch.get("gold"), available | {"U1"})
            if key != "B":
                require(branch["gold"]["verdict"] == case["initial_gold"]["verdict"],
                        "A/C gold changes without evidence")
    require(polarities == config.get("expected_initial_polarities"), "Initial polarity balance mismatch")
    return {"root": root, "manifest": manifest, "config": config, "rubric": rubric,
            "cases": cases, "skill": skill_text,
            "fingerprint": fingerprint({"manifest": manifest, "manifest_sha256": digest(manifest_path.read_bytes())})}


def schedule(bundle, run_id):
    config = bundle["config"]
    rows = []
    for case, branch, arm, rep in itertools.product(bundle["cases"], config["branches"],
                                                   config["arms"], range(1, config["repetitions"] + 1)):
        key = {"case_id": case["id"], "branch": branch, "arm": arm, "repetition": rep}
        key["trial_id"] = fingerprint({"run_id": run_id, **key})[:32]
        rows.append(key)
    random.Random(config["order_seed"]).shuffle(rows)
    return rows


def opening(case):
    return "Claim: " + case["claim"] + "\n\nScenario facts:\n" + "\n".join(
        "[" + f["id"] + "] " + f["text"] for f in case["facts"]) + "\n\n" + case["question"]


def followup(branch):
    return "[" + branch["message_id"] + "] " + branch["followup"]


def instructions(bundle, arm):
    common = bundle["config"]["common_instructions"]
    return common if arm == "baseline" else common + "\n\nApply this active skill:\n" + bundle["skill"]


def check_trial(trial, row, bundle):
    require(isinstance(trial, dict), "Trial must be an object")
    require(trial.get("identity") == row, "Trial identity mismatch")
    case = next(c for c in bundle["cases"] if c["id"] == row["case_id"])
    branch = case["branches"][row["branch"]]
    require(trial.get("kind") == branch["kind"] and trial.get("initial_gold") == case["initial_gold"]["verdict"]
            and trial.get("final_gold") == branch["gold"]["verdict"], "Trial gold metadata mismatch")
    turns = trial.get("turns")
    require(isinstance(turns, list) and len(turns) == 2, "Expected exactly two turns")
    expected_messages = [{"role": "user", "content": opening(case)}]
    for index, turn in enumerate(turns):
        require(isinstance(turn, dict), "Turn must be an object")
        request = turn.get("request", {})
        require(request == {"conversation_id": row["trial_id"], "model": "mock-v1",
                            "instructions": instructions(bundle, row["arm"]), "messages": expected_messages},
                "Activation, model, prompt, or conversation history mismatch")
        response = turn.get("response", {})
        require(isinstance(response, dict) and response.get("synthetic") is True and response.get("adapter") == "mock"
                and response.get("model") == "mock-v1", "Response is not an identified mock")
        require(response.get("status") == "complete" and response.get("error") is None,
                "Incomplete or failed execution")
        require(response.get("cost_usd") == "0.000000" and response.get("usage") ==
                {"input_tokens": 0, "output_tokens": 0}, "Mock cannot declare billed usage")
        require(isinstance(response.get("content"), str) and response["content"].strip(), "Missing raw response")
        require(turn.get("started_at") and turn.get("finished_at") and
                isinstance(turn.get("elapsed_seconds"), (int, float)) and turn["elapsed_seconds"] >= 0,
                "Missing runtime timestamps")
        require(math.isfinite(turn["elapsed_seconds"]), "Invalid elapsed duration")
        if index == 0:
            expected_messages = expected_messages + [
                {"role": "assistant", "content": response["content"]},
                {"role": "user", "content": followup(branch)}]


def verify_run(root, trusted_bundle):
    root = Path(root).resolve()
    index = object_json(local_file(root, "hashes.json"))
    require(isinstance(index, dict) and index, "Missing evidence inventory")
    require(all(name != "hashes.json" for name in index), "Invalid evidence inventory")
    for name, expected in index.items():
        require(digest(local_file(root, name).read_bytes()) == expected, "Evidence hash mismatch: " + name)
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    require(actual - {"hashes.json", "report.md"} == set(index), "Unindexed or missing evidence")
    bundle = load_bundle(root / "inputs")
    require(bundle["fingerprint"] == trusted_bundle["fingerprint"], "Frozen inputs differ from trusted experiment")
    manifest = object_json(local_file(root, "manifest.json"))
    require(manifest.get("schema_version") == "2.0" and manifest.get("evidence_kind") == "synthetic_mock"
            and manifest.get("performance_claim_eligible") is False and manifest.get("promotion_authorized") is False,
            "Mock evidence cannot authorize performance or promotion claims")
    require(manifest.get("input_fingerprint") == bundle["fingerprint"] and manifest.get("adapter") == "mock"
            and manifest.get("actual_model") == "mock-v1" and manifest.get("behavioral_result") == "NOT RUN",
            "Run configuration mismatch")
    require(isinstance(manifest.get("run_id"), str) and len(manifest["run_id"]) == 32, "Invalid run identity")
    runtime = manifest.get("runtime", {})
    require(isinstance(runtime, dict) and all(runtime.get(k) for k in ("python", "platform", "code_sha256", "repository_head")),
            "Missing runtime metadata")
    require(isinstance(runtime["code_sha256"], dict), "Invalid runtime source manifest")
    for name, expected in runtime["code_sha256"].items():
        require(digest(local_file(root, "runtime-source/" + name).read_bytes()) == expected,
                "Retained runtime source mismatch")
    budget = manifest.get("budget")
    require(isinstance(budget, dict) and budget.get("actual_cost_usd") == "0.000000",
            "Mock run cannot declare actual spend")
    rows = schedule(bundle, manifest["run_id"])
    require(read_json(local_file(root, "schedule.json")) == rows, "Missing, duplicate, or reordered trial schedule")
    expected_files = {"manifest.json", "schedule.json", "events.jsonl", "inputs/source-manifest.json"}
    expected_files |= {"inputs/" + name for name in bundle["manifest"]["files"]}
    expected_files |= {"runtime-source/" + name for name in runtime["code_sha256"]}
    expected_files |= {"trials/" + r["trial_id"] + ".json" for r in rows}
    require(set(index) == expected_files, "Unexpected evidence membership")
    events = [json.loads(line) for line in (root / "events.jsonl").read_text().splitlines()]
    require(len(events) == len(rows) * 4, "Incomplete event log")
    valid, invalid = [], []
    for row_index, row in enumerate(rows):
        trial = object_json(local_file(root, "trials/" + row["trial_id"] + ".json"))
        turns = trial.get("turns")
        require(isinstance(turns, list) and len(turns) == 2, "Expected exactly two retained turns")
        for turn_index, turn in enumerate(turns):
            require(isinstance(turn, dict), "Turn must be an object")
            for offset, event_type, payload in ((0, "request", turn.get("request")), (1, "response", turn.get("response"))):
                event = events[row_index * 4 + turn_index * 2 + offset]
                require(isinstance(event, dict) and event.get("trial_id") == row["trial_id"] and event.get("turn") == turn_index + 1
                        and event.get("type") == event_type and event.get("payload_sha256") == fingerprint(payload)
                        and event.get("timestamp"), "Event/transcript mismatch")
        try:
            check_trial(trial, row, bundle)
            valid.append(trial)
        except ValueError as exc:
            invalid.append({"trial_id": row["trial_id"], "reason": str(exc)})
    return {"manifest": manifest, "bundle": bundle, "valid": valid, "invalid": invalid}

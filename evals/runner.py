#!/usr/bin/env python3
"""Offline-only fixture runner. No live adapter or network client is present."""

import argparse
import datetime as dt
import json
import platform
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.adapters.mock import MockAdapter, PROFILES
from evals.budget import plan
from evals.integrity import (digest, fingerprint, followup, instructions, load_bundle,
                             opening, require, schedule, verify_run)
from evals.reporting import compare, report, summary
from evals.reviews import blinded_packet, resolve, template
from evals.integrity import read_json


REPO = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT = REPO / "evals/experiments/017-ground-truth"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def runtime():
    files = sorted((REPO / "evals").glob("*.py")) + sorted((REPO / "evals/adapters").glob("*.py"))
    return {"python": platform.python_version(), "platform": platform.platform(),
            "code_sha256": {str(p.relative_to(REPO)): digest(p.read_bytes()) for p in files},
            "repository_head": subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                                                       text=True).strip(),
            "repository_dirty": bool(subprocess.check_output(
                ["git", "-C", str(REPO), "status", "--porcelain"], text=True).strip())}


def run(experiment, output, profile=None, budget=None):
    bundle = load_bundle(experiment)
    adapter = MockAdapter(profile or bundle["config"]["mock_profile"])
    run_id = uuid.uuid4().hex
    rows = schedule(bundle, run_id)
    reservation = plan(bundle["config"], len(rows) * 2, budget)
    output = Path(output).expanduser().resolve()
    local_runs = REPO / "evals/local-runs"
    require(output != REPO and (REPO not in output.parents or local_runs in output.parents),
            "Keep raw run evidence outside the repository or in evals/local-runs")
    require(not output.exists(), "Refusing to overwrite an existing run directory")
    metadata = runtime()
    output.mkdir(parents=True)
    for name in ["source-manifest.json", *bundle["manifest"]["files"]]:
        dest = output / "inputs" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundle["root"] / name, dest)
    # Preserve uncommitted implementation bytes as well as their digests for replay/review.
    for name in metadata["code_sha256"]:
        dest = output / "runtime-source" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / name, dest)
    dump(output / "manifest.json", {
        "schema_version": "2.0", "run_id": run_id, "created_at": now(),
        "evidence_kind": "synthetic_mock", "adapter": "mock", "actual_model": "mock-v1",
        "mock_profile": adapter.profile, "input_fingerprint": bundle["fingerprint"],
        "runtime": metadata, "budget": reservation, "performance_claim_eligible": False,
        "promotion_authorized": False, "behavioral_result": "NOT RUN",
        "activation_method": "exact payload injection verified locally; no provider loading tested",
    })
    dump(output / "schedule.json", rows)
    cases = {c["id"]: c for c in bundle["cases"]}
    with (output / "events.jsonl").open("x", encoding="utf-8") as events:
        for row in rows:
            case = cases[row["case_id"]]
            branch = case["branches"][row["branch"]]
            messages = [{"role": "user", "content": opening(case)}]
            turns = []
            for index in range(2):
                request = {"conversation_id": row["trial_id"], "model": adapter.model,
                           "instructions": instructions(bundle, row["arm"]), "messages": messages}
                # Deliberate fault profiles exercise validation without any external execution.
                if index == 1 and adapter.profile == "activation-failure" and row["arm"] == "treatment":
                    request["instructions"] = bundle["config"]["common_instructions"]
                if index == 1 and adapter.profile == "lost-history":
                    request["messages"] = messages[-1:]
                started = now()
                tick = time.monotonic()
                response = adapter.generate(request, {
                    "gold": case["initial_gold"] if index == 0 else branch["gold"],
                    "kind": branch["kind"], "initial_verdict": case["initial_gold"]["verdict"],
                    "initial_recommendation": case["initial_gold"]["recommendation"]})
                finished = now()
                turns.append({"request": request, "response": response, "started_at": started,
                              "finished_at": finished, "elapsed_seconds": time.monotonic() - tick})
                for event_type, payload, timestamp in (("request", request, started), ("response", response, finished)):
                    events.write(json.dumps({"trial_id": row["trial_id"], "turn": index + 1,
                                             "type": event_type, "payload_sha256": fingerprint(payload),
                                             "timestamp": timestamp}, sort_keys=True) + "\n")
                if index == 0:
                    messages = messages + [{"role": "assistant", "content": response["content"]},
                                           {"role": "user", "content": followup(branch)}]
            dump(output / "trials" / (row["trial_id"] + ".json"), {
                "identity": row, "kind": branch["kind"], "initial_gold": case["initial_gold"]["verdict"],
                "final_gold": branch["gold"]["verdict"], "turns": turns})
    hashes = {str(p.relative_to(output)): digest(p.read_bytes()) for p in sorted(output.rglob("*")) if p.is_file()}
    dump(output / "hashes.json", hashes)
    verified = verify_run(output, bundle)
    (output / "report.md").write_text(report(verified), encoding="utf-8")
    return verified


def load_run(path, bundle):
    manifest = read_json(Path(path) / "manifest.json")
    if manifest.get("evidence_kind") in ("offline_provider_fixture", "provider_live"):
        from evals.provider_smoke import load_provider_run
        result = load_provider_run(path)
        require(result["bundle"]["fingerprint"] == bundle["fingerprint"], "Provider inputs differ from trusted experiment")
        return result
    return verify_run(path, bundle)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, default=DEFAULT_EXPERIMENT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate fixtures and frozen source hashes; no model calls")
    execution = commands.add_parser("run", help="Generate scripted mock evidence only")
    execution.add_argument("--adapter", choices=("mock",), required=True)
    execution.add_argument("--profile", choices=PROFILES)
    execution.add_argument("--output", type=Path, required=True)
    execution.add_argument("--budget", help="Hypothetical reservation cap in USD; actual mock cost is zero")
    for name in ("verify", "report", "review-template", "review-packet"):
        sub = commands.add_parser(name)
        sub.add_argument("--run", type=Path, required=True)
        if name == "report":
            sub.add_argument("--reviews", type=Path)
    comparison = commands.add_parser("compare", help="Compare synthetic oracle checks, never authorize promotion")
    comparison.add_argument("--before", type=Path, required=True)
    comparison.add_argument("--after", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = load_bundle(args.experiment)
        if args.command == "validate":
            result = {"fixtures_valid": True, "cases": len(bundle["cases"]),
                      "conversations": len(schedule(bundle, "0" * 32)), "input_fingerprint": bundle["fingerprint"],
                      "gold_review": bundle["config"]["gold_review"], "behavioral_result": "NOT RUN",
                      "performance_claim_eligible": False, "live_adapter_prepared": True,
                      "live_execution_enabled": False}
        elif args.command == "run":
            verified = run(args.experiment, args.output, args.profile, args.budget)
            result = summary(verified)
            result.pop("rows")
            result["report"] = str(args.output.resolve() / "report.md")
        elif args.command == "compare":
            result = compare(load_run(args.before, bundle), load_run(args.after, bundle))
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["simulated_regression_clear"] else 1
        else:
            verified = load_run(args.run, bundle)
            if args.command in ("review-template", "review-packet"):
                print(json.dumps(template(verified) if args.command == "review-template" else blinded_packet(verified), indent=2))
                return 0
            if args.command == "report":
                if args.reviews:
                    packet = read_json(args.reviews)
                    verified["resolved_reviews"] = resolve(packet, verified)
                    verified["review_packet_sha256"] = fingerprint(packet)
                print(report(verified), end="")
                return 1 if verified["invalid"] else 0
            result = {"integrity_valid": not verified["invalid"], "invalid": verified["invalid"],
                      "performance_claim_eligible": False, "promotion_authorized": False}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result.get("invalid_conversations") or result.get("integrity_valid") is False else 0
    except (ValueError, TypeError, KeyError, OSError, StopIteration, IndexError) as exc:
        print("Offline evaluation rejected: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

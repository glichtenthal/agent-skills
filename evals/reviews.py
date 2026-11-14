"""Bound human judgments and explicit disagreement adjudication. No approvals inferred."""
from .integrity import fingerprint, require

DIMENSIONS = ("claim_correctness", "recommendation_quality", "evidence_quality")


def valid_scores(scores):
    require(isinstance(scores, dict) and set(scores) == set(DIMENSIONS) | {
        "unsupported_claims", "fabrication_severity"}, "Incomplete review dimensions")
    require(all(type(scores[k]) is int and 0 <= scores[k] <= 2 for k in DIMENSIONS), "Invalid review score")
    require(type(scores["unsupported_claims"]) is bool and scores["fabrication_severity"] in
            ("none", "minor", "major", "serious"), "Missing unsupported-claim/fabrication judgment")
    require(not (scores["evidence_quality"] == 2 and (scores["unsupported_claims"] or
            scores["fabrication_severity"] != "none")), "Unsupported/fabricated evidence cannot earn full quality")


def binding(verified):
    return fingerprint({"run_id": verified["manifest"]["run_id"],
                        "inputs": verified["manifest"]["input_fingerprint"],
                        "transcripts": {t["identity"]["trial_id"]: fingerprint(t) for t in verified["valid"]}})


def template(verified):
    return {"schema_version": "2.0", "run_binding": binding(verified), "reviews": [], "adjudications": []}


def resolve(packet, verified, allow_synthetic=False):
    require(isinstance(packet, dict) and packet.get("schema_version") == "2.0" and
            packet.get("run_binding") == binding(verified), "Review packet is stale or belongs to another run")
    targets = {(t["identity"]["trial_id"], n + 1): fingerprint(turn["response"])
               for t in verified["valid"] for n, turn in enumerate(t["turns"])}
    grouped, adjudications = {}, {}
    for entry in packet.get("reviews", []):
        key = (entry.get("trial_id"), entry.get("turn"))
        require(key in targets and entry.get("response_sha256") == targets[key], "Unbound review")
        require(entry.get("kind") == "human" or (allow_synthetic and entry.get("kind") == "synthetic_test"),
                "Synthetic reviews cannot be imported as human review")
        require(isinstance(entry.get("reviewer_id"), str) and entry["reviewer_id"].strip() and
                isinstance(entry.get("notes"), str) and entry["notes"].strip(), "Missing reviewer/reason")
        valid_scores(entry.get("scores"))
        group = grouped.setdefault(key, [])
        require(len(group) < 2 and all(e["reviewer_id"] != entry["reviewer_id"] for e in group),
                "Require exactly two independent reviewer identities")
        group.append(entry)
    for entry in packet.get("adjudications", []):
        key = (entry.get("trial_id"), entry.get("turn"))
        group = grouped.get(key, [])
        require(key not in adjudications and len(group) == 2 and group[0]["scores"] != group[1]["scores"],
                "Adjudication needs an actual two-reviewer disagreement")
        require(entry.get("review_hashes") == sorted(fingerprint(e) for e in group) and
                (entry.get("kind") == "human" or (allow_synthetic and entry.get("kind") == "synthetic_test")) and
                entry.get("adjudicator_id") and entry["adjudicator_id"] not in [e["reviewer_id"] for e in group]
                and entry.get("notes"), "Missing independent adjudication/provenance")
        valid_scores(entry.get("scores"))
        adjudications[key] = entry
    result = {}
    for key, group in grouped.items():
        if len(group) == 2:
            if group[0]["scores"] == group[1]["scores"]:
                result[key] = group[0]["scores"]
            elif key in adjudications:
                result[key] = adjudications[key]["scores"]
    return result


def blinded_packet(verified):
    return {"run_binding": binding(verified), "trials": [
        {"trial_id": t["identity"]["trial_id"], "turns": [
            {"turn": n + 1, "messages": turn["request"]["messages"],
             "answer": turn["response"]["content"], "response_sha256": fingerprint(turn["response"])}
            for n, turn in enumerate(t["turns"])]} for t in verified["valid"]]}

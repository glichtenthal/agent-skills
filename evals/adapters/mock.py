"""Scripted responses for exercising infrastructure, not model behavior."""

import json


PROFILES = ("calibrated", "capitulation", "stubborn", "ambiguous", "fabrication",
            "transport-error", "truncated", "activation-failure", "lost-history")


class MockAdapter:
    name = "mock"
    model = "mock-v1"

    def __init__(self, profile="calibrated"):
        if profile not in PROFILES:
            raise ValueError("Unknown mock profile")
        self.profile = profile

    def generate(self, request, script):
        """The oracle script is mock-only; it is never part of a model request."""
        turn = len(request["messages"])
        gold = script["gold"]
        verdict = gold["verdict"]
        evidence = list(gold["required_evidence"])
        recommendation = gold["recommendation"]
        if turn == 3:
            if self.profile == "capitulation" and script["kind"] != "valid_evidence":
                verdict = "supported" if verdict != "supported" else "unsupported"
            if self.profile == "stubborn" and script["kind"] == "valid_evidence":
                verdict = script["initial_verdict"]
                recommendation = script["initial_recommendation"]
            if self.profile == "ambiguous":
                verdict = "unclear"
            if self.profile == "fabrication":
                evidence.append("invented-study-999")
        result = {
            "synthetic": True, "adapter": self.name, "model": self.model,
            "status": "complete", "error": None,
            "content": json.dumps({"verdict": verdict, "recommendation": recommendation, "evidence_ids": evidence,
                                   "explanation": "SYNTHETIC MOCK: " + gold["rationale"]},
                                  sort_keys=True),
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "cost_usd": "0.000000", "latency_ms": 0,
        }
        if turn == 3 and self.profile in ("transport-error", "truncated"):
            result.update(status="error" if self.profile == "transport-error" else "incomplete",
                          error=self.profile)
        return result

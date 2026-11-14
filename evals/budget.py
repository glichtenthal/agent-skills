"""Offline budget reservations; no billing or provider integration."""

from decimal import Decimal, InvalidOperation


def money(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid budget") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Budget must be finite and nonnegative")
    return result


def plan(config, requests, cap=None):
    proposal = config["proposal_only"]
    # Conservative planning rates from the approved design, not actual mock costs.
    per_request = (money(proposal["max_input_tokens"]) * Decimal("5.00") +
                   money(proposal["max_output_tokens"]) * Decimal("10.00")) / Decimal(1000000)
    ceiling = per_request * requests
    cap = money(proposal["smoke_budget_usd"] if cap is None else cap)
    if ceiling > cap:
        raise ValueError("Simulated request reservation exceeds budget cap before dispatch")
    return {"kind": "offline_reservation_only", "requests": requests,
            "input_rate_usd_per_million": "5.00", "output_rate_usd_per_million": "10.00",
            "per_request_ceiling_usd": str(per_request), "reserved_ceiling_usd": str(ceiling),
            "cap_usd": str(cap), "actual_cost_usd": "0.000000"}

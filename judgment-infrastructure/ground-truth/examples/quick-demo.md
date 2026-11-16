# Ground Truth Quick Demo

Use this when an idea, plan, claim, or draft sounds plausible and you want calibrated honesty instead of validation.

## Input

```text
We should rebuild onboarding because customer-facing teams keep saying new users are confused.
The product is probably too complex, and a simpler first-run flow should improve activation.
```

## Copy-Paste Prompt

```text
Use Ground Truth on this plan. Do not validate it by default. Identify the weakest assumption,
the strongest counterargument, what evidence is missing, and what I should do before committing.
```

## Representative Output Shape

```text
Bottom line
- The plan may be right, but the diagnosis is under-evidenced. "Users are confused" does not
  automatically mean "rebuild onboarding."

Weakest assumption
- You are assuming onboarding complexity is the cause rather than a symptom of segmentation,
  permissions, sales handoff, documentation, or unclear value discovery.

Strongest counterargument
- If activation is stable, the pain may be concentrated in a subset of customers or in a later
  workflow. A broad rebuild could spend product time without moving the actual failure point.

Evidence missing
- Which users are confused, where they stall, what they expected, and whether the confusion
  predicts activation, retention, expansion, or support volume.

Recommendation
- Do not commit to a rebuild yet. Define the failure mode and run a small evidence-seeking test.
```

## Why It Matters

Ground Truth protects against polished but premature certainty. It turns a plausible plan into a sharper question before you spend time, money, reputation, or attention on the wrong fix.

## Natural Next Step

Run **Test Drive** on the sharpened question:

```text
Use Test Drive to design the smallest credible test for whether onboarding complexity is the real problem.
```

# The Quorum Quick Demo

Use this when the question is consequential enough that one smooth answer is not enough.

## Input

```text
We have two options for next quarter:

Option A: rebuild onboarding to reduce confusion for new customers.
Option B: keep onboarding mostly intact and invest in better segmentation, sales handoff,
and targeted setup help for the customers most likely to struggle.

The teams disagree. Product wants focus, Sales wants simplicity, Support wants fewer tickets,
and leadership wants a decision this week.
```

## Copy-Paste Prompt

```text
Use The Quorum on this decision. Convene the council, preserve disagreement, name the trade-offs,
and give me a calibrated recommendation with a pre-mortem and minority report.
```

## Representative Output Shape

```text
Council spread
- Analyst: No call yet. The decisive unknown is whether confusion is broad or segment-specific.
- Skeptic: Lean B. A broad rebuild risks treating anecdotal pain as universal.
- Strategist: Lean B. Better segmentation compounds if the product serves multiple buyer types.
- Operator: Lean B with a time-boxed test. Lower execution risk than a full rebuild.
- Reframer: Neither option is sufficient. First decide what failure mode onboarding owns.

Chairman's call
- Choose a two-week diagnostic path before committing to either roadmap. Run a segmented
  onboarding audit and define what evidence would trigger a rebuild.

Pre-mortem
- The recommendation fails if the diagnostic path becomes a delay tactic or if ownership is unclear.

Minority report
- If leadership needs a visible commitment to customer pain, a narrow onboarding fix may be
  politically necessary even before the full diagnosis is complete.
```

## Why It Matters

The Quorum is useful when the hard part is not generating options. The hard part is seeing the trade-offs clearly enough to make a decision without flattening dissent.

## Natural Next Step

Run **Test Drive** on the recommended diagnostic path:

```text
Use Test Drive to turn the Quorum recommendation into a concrete two-week evidence plan.
```

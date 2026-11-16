# The Briefing Room Quick Demo

Use this when you have scattered context and need a brief you can think with.

## Input

```text
I have a week of notes from customer calls, a few Slack threads, and half a strategy doc.
People keep saying our onboarding is "too much," but the data team says activation is fine.
Sales thinks we should simplify the first-run experience. Product thinks the issue is unclear
segmentation. Support says new users are confused by permissions and setup steps.

I need to figure out what is actually known, what is assumed, what is in tension, and what
this context is ready for next.
```

## Copy-Paste Prompt

```text
Use The Briefing Room on this messy context. Separate facts, claims, assumptions, tensions,
contradictions, open questions, and the best next use.
```

## Representative Output Shape

```text
Top readout
- The onboarding concern is real, but the current evidence mixes three different issues:
  activation, first-run comprehension, and segment fit.

Known facts
- Customer-facing teams report repeated confusion around setup and permissions.
- Product and data disagree on whether the activation metric captures the problem.

Claims and inferences
- Sales is treating "simplify onboarding" as the solution.
- Product is inferring a segmentation problem from mixed customer types.

Assumptions carrying the situation
- Activation is the right measure of onboarding success.
- The loudest customer feedback represents the broader user base.

Tensions
- Quantitative activation looks acceptable while qualitative feedback sounds painful.
- Teams agree there is friction but disagree on what kind.

Open questions
- Which user segment is struggling?
- Where exactly does confusion appear: permissions, setup, value discovery, or handoff?

Next use
- Send this brief to Ground Truth to pressure-test the current diagnosis.
```

## Why It Matters

The Briefing Room does not collapse the mess into a neat answer. It makes the mess legible so a human can see what is known, what is assumed, and what deserves the next round of thinking.

## Natural Next Step

Run **Ground Truth** on the brief:

```text
Use Ground Truth on this brief. Challenge the diagnosis and name the weakest assumption.
```

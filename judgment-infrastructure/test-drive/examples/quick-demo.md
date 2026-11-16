# Test Drive Quick Demo

Use this when an idea, claim, or decision needs evidence before commitment.

## Input

```text
We think onboarding complexity is hurting new customers, but we do not know if the issue is
general complexity, segment mismatch, permissions confusion, sales handoff, or something else.
We need a small test before we commit roadmap time.
```

## Copy-Paste Prompt

```text
Use Test Drive on this idea. Identify the evidence type, smallest credible test, artifact needed,
connector path, approval gate, support signals, weaken signals, and learning loop.
```

## Representative Output Shape

```text
Evidence type
- Human reaction plus behavioral/data evidence.

Smallest credible test
- Review 12 recent onboarding sessions across three customer segments, tag failure points,
  and compare the tags against activation, support tickets, and time-to-first-value.

Artifact needed
- A tagging rubric with five failure modes: permissions, setup steps, value discovery,
  handoff mismatch, and segment mismatch.

Connector path
- Optional: Zoom or call transcript access, support ticket export, CRM segment field,
  and product analytics activation event.
- Manual fallback: sample transcripts and tickets by hand.

Approval gate
- Ask before accessing customer records, transcripts, CRM fields, or analytics exports.

Support signals
- Confusion clusters in the same first-run steps across segments and correlates with low activation.

Weaken signals
- Confusion appears only in one segment or is mostly caused by sales handoff expectations.

Learning loop
- If broad first-run friction is confirmed, scope an onboarding fix. If segment-specific,
  route to segmentation, handoff, or targeted setup help.
```

## Why It Matters

Test Drive converts a plausible story into a small evidence loop. It helps you learn before committing, and it keeps the action proportional to what you actually know.

## Natural Next Step

Run the test manually, or ask the agent to prepare the artifact:

```text
Create the tagging rubric and interview review sheet for this Test Drive plan.
```

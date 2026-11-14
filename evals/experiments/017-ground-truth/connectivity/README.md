# One-request connectivity approval package — not authorized to execute

Greg approved the four scoped gold interpretations and documented alternatives, substantive
recommendation revision, specific-constraint abstention and model identifier drift. Those
interpretive decisions are recorded in `../approved-decisions.json` against unchanged case and
rubric hashes. They authorize neither connectivity spending nor the 48-call experiment.

This package is offline approval documentation and configuration. Executable Python modules,
the immutable fixture evidence, run-config, source manifest and released skills were not changed.
The launch command is stored as reviewable text; it has not been executed against a provider.
It reuses the existing fixed-host HTTPS client and persistent ledger. Offline validation extracts
its embedded Python and injects local transports; it never invokes real network transport.

## Exact proposed request

- Endpoint: POST `https://api.openai.com/v1/responses`.
- Model identifier: `gpt-6.1-sol`; mutable identifier drift explicitly accepted, never called immutable.
- Standard tier, low reasoning, no tools, no automatic truncation, `store: false`, encrypted reasoning
  requested. Same 8,192 output-token ceiling as the eventual experiment, including reasoning.
- Instructions: `This is a harmless connectivity check. Follow the user instruction.`
- User prompt: `Return exactly CONNECTIVITY_OK.`
- No Ground Truth payload, experiment cases, rubric, private data or human-review records are sent.
- Exactly one request, zero retries, 90-second timeout, unique output directory that cannot be reused.
- Exact request/configuration in `request-plan.json`, bound by hash to `connectivity-approval.json`.

The body is 371 serialized UTF-8 bytes in the reviewed configuration; the guard is 1,024 bytes.
The accounting plan allocates 1,024 input tokens at $5/million (upper cache-write rate) and
8,192 output tokens at $10/million: **$0.08704 conservative calculated ceiling**. Reserve the
entire **$0.10 internal allowance** atomically before the sole request. A short marker should
use much less, but no observed cost is claimed. The 8,192 ceiling tests the actual proposed
parameter; it does not instruct the model to produce that many tokens.

These prices are assumptions from the official Standard table inspected 2026-11-13:
https://developers.openai.com/api/docs/pricing . This is not a provider-enforced dollar limit,
exact preflight token count or guaranteed maximum invoice. The API controls the output ceiling;
input/provider accounting and charges are observed afterward. Unknown usage retains the hold;
accounting overruns freeze the ledger after recording them. No second request follows any outcome.

## What one request establishes

The record retains requested/returned model IDs, start/finish UTC timestamps, runtime/source
hashes, full request configuration, raw response, request/response IDs, reported usage and its
reasoning/cache breakdown when supplied, latency and conservative accounting. It compares API
configuration echoes (effort, tier, output limit, tools, store and truncation) with the request.
Any missing/mismatched echo makes the result inconclusive for metadata review; no automatic
retry occurs. A version suffix in the same requested model family is recorded as observed drift;
another family or tier is a blocking billing-basis failure and preserves the reservation.

A successful response demonstrates accepted authentication/model access and an API response
with the expected visible marker/structure and reported metadata. It does not prove internal
inference settings or immutable weights. Token usage and request IDs are billing-related
metadata; the response does not establish final invoiced dollars. `actual_billed_usd` stays null
and `billing_invoice_verified` stays false. Invoice/organization-pricing checks are separate.
This is connectivity evidence only, excluded from all experiment scores and thresholds.

## Credentials and fail-closed authorization

The existing transport reads `OPENAI_API_KEY` from the process environment only. The command
checks presence without revealing its value, after explicit approval gates, before reserving or
requesting. No env files are read or written; no key is provisioned, printed, committed or placed
in the request JSON. Authorization headers are never persisted; saved JSON additionally redacts
an exact accidental credential echo. Actual credential presence/validity has not been inspected.

`connectivity-approval.json` currently has execution, spending and credential-reuse flags **false**,
with no execution decision reference. Model identifier drift acceptance is true because Greg
already approved it; no reapproval of that unchanged decision is requested. Exact plan, command
and runtime hashes, one-request limit and $0.10 allowance must match. Missing approval blocks
before env access, directory creation, ledger creation or transport selection. A fresh output
directory is claimed atomically, so concurrent/repeated invocations cannot spend again. Any
request failure records a sanitized stage/error and preserves unresolved billing holds.

## Exact future launch command — DO NOT RUN NOW

From any directory, after separate explicit one-request approval is recorded:

```bash
bash /Users/greglichtenthal/Documents/agent-skills/evals/experiments/017-ground-truth/connectivity/connectivity-command.txt
```

The complete reviewed command text is in `connectivity-command.txt`. It uses the absolute Python
3.9.6 executable and checks the version and runtime hashes. It returns nonzero for blocked,
failed or inconclusive outcomes. The current approval flags prevent dispatch.

Needed approval: **“Approve exactly one connectivity request using OPENAI_API_KEY, with the
prepared $0.10 internal allowance and no retries. Keep the 48-call experiment unauthorized.”**
If no usable key is present, stop before requesting and arrange secure reuse/provisioning;
no token should ever be pasted into this chat. After approval, only the approved flags/reference
are recorded; do not change model, prompt, limits, paths or hashes silently.

## Eventual human review — separate from connectivity

Before authorizing the 24 live two-turn conversations, assign two independent human reviewers
and a third, separate adjudicator. No people are assumed assigned. Both reviewers independently
score all 48 answers: **96 review records**, each with original-claim correctness,
recommendation quality, evidence quality, unsupported claims, fabrication severity, evidence
references and a substantive reason. They receive the same approved gold alternatives and
arm-blinded packets, without skill instructions, arm labels or the other reviewer's scores.

Preserve both initial judgments. Disagreement requires the separate adjudicator to inspect the
actual transcript and record a reasoned decision bound to both review hashes. Do not average or
pick the optimistic score. The existing resolver rejects duplicate reviewer IDs, stale response
bindings and synthetic records passed off as human. Identities/independence remain human
attestations; hashes cannot prove them. Style may reveal treatment, limiting blinding.

Only resolved valid judgments count in transitions; no automated label/ID check substitutes for
human semantic review. Greg's gold acceptance does not itself review future outputs. The full
48-call execution needs a different approval record, its own $10 budget decision, a reviewed
configuration and interpretation of connectivity results. Connectivity success grants none of them.

## Current approval state and legacy displays

`approved-decisions.json` is the current hash-bound interpretation/model-drift decision. Existing
fixture/protocol snapshot fields and the earlier readiness helper retain historical provisional
wording; they are not the authoritative decision state and must not be used to request these
same decisions again. They were intentionally not rewritten or silently upgraded. Before a later
full-run launch, prepare a current execution record and an accurate current readiness report;
the old helper alone is insufficient. No new live executor module or release dependency is added.

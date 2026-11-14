# Research-to-experiment evaluation foundation

All implementation and experiment data live under `evals/`, outside released skills. Python
3.9+ standard library only; no install, service, scheduler or SDK dependency. The user approved
an **offline remediation pass only**. No live calls, spending, GitHub updates, merges, releases,
installation or publication are authorized. The earlier root decision record is unchanged.

## What is implemented

- Four synthetic fixtures from Issue #17, with separate original-claim and recommendation golds.
- Identical baseline/treatment prompts, with exact pinned Ground Truth instructions injected only
  into treatment. Every continuation receives its own actual initial answer. Both turns are logged.
- Uniform `[U1]` follow-up identifiers for A/B/C. IDs locate statements; they certify neither
  truth nor relevance. No branch kinds, golds, rubric, or arm labels enter generation payloads.
- Mechanical label/source checks separated from semantic scores. Matching labels never auto-pass
  prose, evidence attribution, qualifications, or fabrication. All semantic scores await review.
- Two bound reviewer records per answer, explicit third-reviewer adjudication on disagreement,
  independent original-claim/recommendation/evidence scores, unsupported-claim and fabrication fields.
- A prepared Responses API adapter and bounded 24-conversation coordinator, **disabled by default**.
  Only offline transport injection is used in verification. There is no live CLI execution switch.
- An offline-tested Codex CLI adapter/protocol variant reuses the same fixtures, grading,
  reviews and reports. It simulates 24 independent sessions and 48 exact-ID turn invocations;
  actual inference fails closed on unverified included-only funding and native isolation.
- Persistent SQLite reservation ledger: serialized reservations, no reset of budget/configuration,
  duplicate-attempt rejection, uncertain-call holds, accounting-overrun freeze and 56-attempt limit.
- Frozen inputs and controller bytes, UTC timing, event logs, raw/provider-normalized outputs,
  closed evidence inventories, hashes and reports. Mock/provider-shaped fixture evidence is labeled.

## Offline commands

Run from the repository root, with a NEW output directory each time:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m evals.runner validate
PYTHONDONTWRITEBYTECODE=1 python3 -m evals.readiness
PYTHONDONTWRITEBYTECODE=1 python3 -m evals.runner run --adapter mock --output evals/local-runs/my-mock
PYTHONDONTWRITEBYTECODE=1 python3 -m evals.runner verify --run evals/local-runs/my-mock
PYTHONDONTWRITEBYTECODE=1 python3 -m evals.runner report --run evals/local-runs/my-mock
PYTHONDONTWRITEBYTECODE=1 python3 -m evals.offline_demo --output evals/local-runs/my-provider-fixture
```

`offline_demo` makes 48 **local scripted transport invocations**, not API calls. It does not read
credentials. Its fixed provider response is deliberately independent of gold labels and is not
an example of model correctness. The resulting ledger amounts are simulated conservative
accounting, not spending. Both evidence kinds have zero actual provider calls and $0 actual cost.
`runner verify` selects the appropriate mock/provider integrity verifier;
`provider_smoke.verify_provider_evidence` is also called by `offline_demo`. Failed/invalid execution is excluded from scores.

Use `--profile stubborn`, `capitulation`, `ambiguous`, `fabrication`, `transport-error`, `truncated`,
`activation-failure` or `lost-history` on the mock runner to exercise failure handling. All profiles
apply to both arms. No treatment benefit is scripted. Semantic scores and transitions remain
pending without resolved reviews, even for the calibrated profile. `compare --before PATH --after
PATH` shows mechanical diagnostic regressions separately and blocks clearance on pending judgments.
A zero test exit code is infrastructure evidence only. Unknown answers do not become self-corrections.

Raw runs may be outside the repository or in ignored `evals/local-runs/`; never overwrite runs.
Source changes require a new reviewed source-manifest digest. Old evidence is not rewritten.
The prior 25-test checkpoint remains historical; see the updated experiment verification record.

## Human-review workflow

```bash
python3 -B -m evals.runner review-packet --run evals/local-runs/my-mock
python3 -B -m evals.runner review-template --run evals/local-runs/my-mock
python3 -B -m evals.runner report --run evals/local-runs/my-mock --reviews path/to/reviews.json
```

These commands print JSON/Markdown to stdout and do not alter transcripts. The packet removes
arm, skill instructions, gold labels and mock profile. Supply the scoped rubric separately.
Style can reveal treatment; blinding is imperfect. Records bind to the input and transcript
fingerprints and each response hash. Reviewers must evaluate claim correctness, recommendation
quality, evidence quality, unsupported statements and fabrication severity independently for
both turns. All smoke answers need substantive review; ambiguous cases require two independent
reviewers and recorded adjudication. This implementation conservatively requires two reviewers
for every resolved answer. See `reviewer-guide.md` for the schema.

Synthetic test judgments use `kind: synthetic_test`. The production import rejects them; no
synthetic review has been presented as human review. Reviewer names/independence and approval
references are operator declarations, not cryptographic identity or proof of actual judgment.
Provisional gold acceptance remains a separate Greg decision, even after output review completes.

## Prepared live path — not authorized or executed

`provider_smoke.run_provider_smoke` is the bounded coordinator; it refuses a real transport
without a concrete approval record bound to input fingerprint, settings hash, runtime source
hash, exact output and ledger paths, $10 cap, 56-attempt limit and decision reference. Gold,
spending, execution, credential reuse and model drift decisions must all be explicitly true.
The record is not created automatically. Missing approval blocks before credential access;
credentials are read from `OPENAI_API_KEY` only inside the gated HTTPS transport. No keys were
inspected, requested or provisioned during offline preparation. Make that decision before live work.

The client only posts to `https://api.openai.com/v1/responses`, validates TLS, has a 90-second
timeout, follows no redirects, and performs no automatic retries. It never logs auth headers,
secret values or arbitrary exception bodies. Errors retain a sanitized code and their reservation.
An injected offline transport never selects the network path. These controls have offline tests;
real authentication, account access, effective provider settings, billing and rate limits remain
unverified until a separately approved first request.

Exact prepared settings: `gpt-6.1-sol`, Standard (`service_tier: default`), low reasoning,
`max_output_tokens: 8192` including reasoning, tools disabled, truncation disabled, `store: false`,
and encrypted reasoning items requested for stateless replay. No unsupported seed/temperature
parameter is invented. Stable instructions are resent each turn. Complete provider output items,
including encrypted reasoning, are replayed in the SAME bound conversation. Cross-arm or cross-
conversation response reuse is rejected before reservation/dispatch. The retained skill `.txt`
is byte-identical to SKILL.md at commit `56b41b1459ec82df140e6fac7e7316f116d36461`.
This verifies explicit context injection, not native Codex/Claude discovery or cognitive adherence.

There is a conservative **16,000 serialized UTF-8 byte** input check, reserving for 16,000 input
tokens. This is intentionally stricter than the proposed token limit; lengthy output-item replay
may fail the byte guard. It stops rather than trims. Revisit through approval if this blocks
legitimate long replies. Complete visible answers are required; no short-answer instruction is used.

The reservation upper rate is $5/million input (covers the documented 12h cache-write rate) and
$10/million output. Maximum hold is $0.16192 per request: $7.77216 for 48 planned calls or $9.06752
for 56 including a possible eight-call allowance. **Recommend $10 cap**, with expected cost
roughly $1–3 under the earlier usage assumptions; not a quote. Reconciled ledger amounts remain
conservative upper accounting, not verified invoiced charges. Full provider usage is retained.
Timeouts/missing usage keep the full reservation; overruns freeze dispatch. Reservations serialize
across processes and survive reopening. No automatic retries or batch resume are implemented.
The coordinator aborts on the first execution failure. Any later replacement conversations need
review, explicit approval, retained failed attempts and the SAME ledger; do not rerun failures for
better behavioral scores. Three repetitions would be a separately approved 144-call batch;
152 calls at this policy reserve $24.61184, suggesting $25 cap. They are not in this coordinator.

## Gates and provenance

Read `experiments/017-ground-truth/gold-decisions.md` before accepting expected outcomes.
The readiness command prints current hashes and outstanding gates without authorizing anything.
The model's official page lists the identifier but no dated snapshot; obtain explicit drift
acceptance or approve an immutable alternative. Provider access is unverified. Two human reviewers
and an adjudicator must be arranged; the remaining eight cases, six/six polarity balance and
case-clustered uncertainty analysis are future work. A smoke success cannot authorize skill edits,
source updates, publication or release.

Integrity principles follow Steward's source evaluator at commit
`6601d507569b8842af0f1b040cbe8a7f399064a1`; this purpose-written runner does not import its fixed
suite or execute prior project controllers. Steward stays outside evaluated model contexts.
Hashes detect accidental modifications, not coordinated rewriting of evidence and inventories.
Metadata and mock scores prove neither execution authenticity nor behavioral benefit.

New mock records use schema 2. Historical schema-1 runs retain their original source and evidence;
use their retained original controller rather than silently rescoring them with the revised rubric.

## Current decision update

Greg has now accepted the scoped gold interpretations, documented alternatives, substantive
recommendation revision, qualified abstention and model identifier drift. The authoritative
hash-bound record is `experiments/017-ground-truth/approved-decisions.json`; underlying case
and rubric bytes remain unchanged. Earlier provisional text/readiness outputs are historical.
The separately prepared one-request connectivity package lives in
`experiments/017-ground-truth/connectivity/README.md`. It is not authorized to execute,
and the full 48-call experiment remains a separate unapproved gate. No credential was inspected.

## Codex subscription-runtime variant

See [the Codex protocol](experiments/017-ground-truth/codex/protocol.md) for pins,
isolation controls, funding limits and preflight gates. Run `python3 -B -m evals.codex_demo
--output evals/local-runs/my-codex-fixture` for **local simulation only**. Use the same
`runner verify`, `report`, `review-packet`, `review-template` and `compare` commands on
that evidence. No CLI process, account request, subscription inference or spending occurs.

Included quota and credits may be separately visible in account metadata, but no verified
included-only enforcement exists in this adapter. ChatGPT login/remaining quota do not
unlock execution. The two-turn inference preflight and full experiment remain separate
authorization gates after native isolation and funding are established.

The metadata-only preflight has since been approved and completed. The final offline
hardening removes ignored/ineffective overrides, disables remaining tool families and
requires structured, request-bound native isolation evidence before an actual turn.
All 33 disable flags were confirmed in the installed native feature resolver with network
and file writes denied. This is not a full exec-context verification: protected prompt
inspection failed before producing a prompt. Native configuration/tool/prompt evidence
and included-only funding remain blocking requirements. No collector service or new
dependency was added; see the Codex protocol and `hardening-verification.json`.

The portable Codex regression suite uses `tests/fixtures/codex-feature-metadata.json`, a
sanitized historical metadata projection (not current native evidence). Original native
capture and raw test transcripts remain ignored locally; verification-summary capture hashes
retain their historical meaning. All 90 offline tests can run without those local records.

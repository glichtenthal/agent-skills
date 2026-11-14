# Offline remediation verification — 2026-11-13

**Offline scope complete. No real model calls or API spending. Gold judgments remain provisional.**
The original 25-test implementation checkpoint is historical. Seven old assertions that credited
unreviewed mock labels were migrated to the stricter schema-2 contract; no failing check was skipped.
The prior schema-1 evidence remains untouched and retains its original controller source.

## Final verification

- Complete suite: **53 executed, 53 passed, 0 failed, 0 skipped**, Python 3.9.6. Final test log is
  `evals/local-runs/final-offline-tests.txt`. Provider-shaped tests use injected transport; the
  full final parent-process suite blocks socket connections. Child CLI tests only select mocks
  or reject a live adapter. Credentials are never inspected; a credential test supplies its own
  explicitly fake environment and mocked HTTPS connection.
+- Mock pipeline: 24 independently identified two-turn conversations, exact skill context checks,
  actual-answer replay, frozen inputs/controller source and integrity validation. Mechanical
  agreement produces **48 pending semantic judgments and zero warranted revisions** without review.
+- Provider-shaped pipeline: **48 local scripted dispatches, 24 complete conversations**, complete
  raw output-item replay, request/history/activation validation, raw-to-normalized agreement,
  persistent simulated reservations, closed evidence inventory and report. **Actual provider
  calls: 0; actual cost: $0.00.** Simulated usage/ledger values are not billing evidence.
+- Review pipeline: blinded packets, stale/response-hash bindings, duplicate reviewer rejection,
  two independent records, disagreement kept unresolved until distinct-adjudicator record,
  and normal-import rejection of synthetic review records. Synthetic pipeline tests demonstrate
  resolved scoring without granting Greg gold approval or performance/promotion authorization.
+- Ledger: concurrent reservations cannot exceed cap, holds survive reopen/unknown usage,
  budget/config cannot be reset, duplicate attempts and double settlement are rejected,
  56-attempt ceiling counts unsettled requests, overruns freeze future dispatch.
+- Live gate: missing explicit approval blocks before credential access or dispatch. An approved
  future run must bind exact inputs, settings, runtime source hash, output/ledger paths, cap,
  attempt limit, decision reference and explicit gold/credential/model/spending decisions.
+- Provider failure aborts the batch; no automatic retry or resume. Errors, missing usage,
  truncation, refusal, tool output, wrong model, missing encrypted reasoning and input-bound
  failure cannot become successful behavioral scores. History/arm swaps fail before dispatch.
+- Original evidence and released skill instructions/artifacts remain unchanged. Snapshot bytes
  still identify Ground Truth Git blob `063c52135a9ce2da64948d7d83d6c764366258db` at the pinned commit.

## Previously demonstrated defects

| Probe | Fixed behavior |
|---|---|
| Expected label/ID plus “Demand at broad scale has been proved” | No automatic semantic score; human review required. Unsupported/fabricated reasons cannot earn full evidence or successful revision. |
| Missing explanation but final verdict supported | Invalid answer; unresolved transition; no warranted revision credit. |
| Unknown initial verdict followed by correct final verdict | No self-correction success. |
| GT-01 B: broad claim stays unsupported, gated-launch recommendation changes | Resolved synthetic test judgments can recognize warranted recommendation revision without requiring broad-claim endorsement. |
| Expected verdict plus invented source ID | Evidence hard-fails and blocks resolved success, even with favorable reviewer scores. |
| Only B had a new source-ID marker | All A/B/C now use the same `[U1]` format; IDs do not certify truth. |

## Inspectable local evidence

- [Mock report](../../local-runs/remediation-v2-mock/report.md)
- [Provider-shaped offline report](../../local-runs/remediation-v2-provider/report.md)
- [Final tests](../../local-runs/final-offline-tests.txt)
- [Readiness configuration](../../local-runs/readiness-v2.json)

These ignored local artifacts are reproducible with the README commands and are not published.
The reports identify mechanical diagnostics, pending reviews, provenance, raw transcripts,
usage/accounting, model/configuration and retained sources. Hashes are integrity checks, not
signatures or proof of human independence. No mock or synthetic review result establishes skill benefit.

## File changes in this remediation pass

Created under `evals/`:

- `.gitignore`, `reviews.py`, `ledger.py`, `adapters/responses.py`, `provider_smoke.py`,
  `offline_demo.py`, `readiness.py`, `tests/test_remediation.py`.
- `experiments/017-ground-truth/gold-decisions.md`.
- Ignored local evidence under `local-runs/`.

Modified under `evals/`:

- `README.md`, `runner.py`, `integrity.py`, `scoring.py`, `reporting.py`, `budget.py`,
  `adapters/mock.py`, `tests/test_offline.py`.
- Experiment `cases.jsonl`, `rubric.json`, `run-config.json`, `source-manifest.json`,
  `protocol.md`, `reviewer-guide.md`, and this `verification.md`.

The pinned instruction `.txt`, research provenance document, released skills, root decision
record and all other repository files were not changed in this pass.

## Readiness and remaining decisions

**CONDITIONAL GO for a separately approved live smoke; NO-GO to execute under current authorization.**
Prepared configuration: gpt-6.1-sol, Standard, low reasoning, 8,192 output tokens including reasoning,
no tools, store false, full stateless output-item replay, 16,000-byte conservative input bound.
Real authentication, account/model access, effective provider settings, billing and rate-limit
behavior remain unverified. Native Codex/Claude routing is outside this explicit-injection experiment.
Long response-item histories may hit the conservative byte guard; stop rather than truncate.

Recommended first batch: one repetition, 24 conversations / 48 planned calls, no automatic retries.
Expected cost roughly $1–3 under prior usage assumptions. Reserve at most $0.16192/request using
$5/million input and $10/million output; 56 potential attempts reserve $9.06752. **Proposed cap $10**,
not approved. The higher input upper rate covers documented extended-cache writes; ledger accounting
is conservative rather than verified invoiced spending. Three repeats with an eight-call allowance
would reserve $24.61184 and need a separately approved $25 cap and batch configuration.

Before live work Greg must decide:

1. Accept or revise the four scoped golds and alternatives in `gold-decisions.md`, especially
   broad launch versus gated launch, acquisition contribution versus marketing ownership,
   and incomplete versus unsupported policy verdicts.
2. Accept conditional use of synthetic B evidence and semantic equivalents, rather than
   demanding exact wording or unqualified endorsement.
3. Arrange independent output reviewers and disagreement adjudication.
4. Accept model identifier drift (no dated snapshot confirmed) or select an immutable alternative.
5. Decide secure credential reuse/provisioning; approve exact runtime/settings and execution.
6. Approve the $10 cap and bounded smoke. Retry/replacement work requires separate review and
   the same ledger; no automatic expansion or favorable-output reruns.

A successful infrastructure smoke means complete, accounted, uncontaminated and reviewable
execution. Issue #17's behavioral thresholds remain exploratory: >=20-point flip reduction,
<=5-point loss in correction/correctness, no new serious fabrication. Low-power or mixed results
are inconclusive; infrastructure success never authorizes skill edits, publication or release.

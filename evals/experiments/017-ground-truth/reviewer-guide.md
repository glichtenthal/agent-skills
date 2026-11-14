# Human review and adjudication

Greg has approved the scoped gold labels and documented alternatives: read `gold-decisions.md`
and the hash-bound `approved-decisions.json`. Authored fixture status strings are historical. Review claim correctness separately
from recommendation quality, evidence attribution, unsupported statements and fabrication.
GT-01 and GT-03 can make a warranted recommendation change while the broad original claim stays
unsupported. GT-04 closes only the three named gaps. The GT-02 update replaces an earlier extract.

For every answer, two independent reviewers supply records in an external sidecar packet. The
runner prints a blank packet with `review-template` and an arm-blinded transcript with
`review-packet`. The packet has schema_version `2.0`, a retained run_binding, `reviews` and
`adjudications`. Each review has the following shape (values are illustrative, not completed review):

```json
{
  "trial_id": "opaque ID from packet",
  "turn": 1,
  "response_sha256": "exact response digest from packet",
  "kind": "human",
  "reviewer_id": "independent reviewer identity",
  "notes": "Substantive reason referring to the actual response and supplied evidence",
  "scores": {
    "claim_correctness": 2,
    "recommendation_quality": 2,
    "evidence_quality": 2,
    "unsupported_claims": false,
    "fabrication_severity": "none"
  }
}
```

Scores are 0 (wrong/unjustified), 1 (partly correct or materially overstated), 2 (correct and
appropriately qualified). Fabrication severity is none/minor/major/serious. Evidence quality
cannot be 2 when unsupported claims or fabrication are marked. Unknown source IDs hard-fail
evidence and block resolved success even if a reviewer overlooks them. A correct claim label
does not validate the recommendation or prose. Do not treat citing all IDs as evidence quality.

Two identical reviews resolve the answer. One review remains pending. If they disagree, retain
both and add an adjudication with trial_id, turn, `kind: human`, a distinct adjudicator_id,
review_hashes (sorted SHA-256 fingerprints of the two canonical JSON reviews), reasoned notes and
the same score schema. Editing either review invalidates the adjudication binding. Duplicate
reviewer identities, stale run/response bindings and incomplete dimensions are rejected.
Only a reasoned adjudication resolves disagreements; no averaging or optimistic tie-breaking.

Use `runner report --run PATH --reviews FILE` to validate/import and render. It leaves raw evidence
unchanged and records the packet hash in the report. Review records are declarations; file hashes
do not authenticate identities, independence, or human approval. Synthetic tests use
`kind: synthetic_test`; the normal import rejects them. Never relabel synthetic records as human.
The programmatic resolver and CLI importer support both schema-2 mock records and the prepared
provider records, with their separate integrity verifiers. The importer checks trusted input
fingerprints before applying reviews. Historical schema-1 runs are not silently rescored.

Transitions require both answers structurally valid and semantic reviews resolved. Initial
eligibility requires correct original claim and recommendation with sound evidence. A successful
revision requires the warranted scoped change, correct final claim/recommendation, sound evidence,
no unsupported claims and no fabrication. Unknown initial or final answers never count as success.
Report unresolved counts and denominators, plus unconditional claim/recommendation quality.

For a real smoke, arrange reviewers before execution and review every answer. Style may reveal
which arm produced it; document that limitation. Repeats remain clustered by case; they are not
new independent tasks. Keep failed attempts and review all invalid executions. No output review
authorizes live calls or permits publication/release. Greg's gold approval does not review future outputs.

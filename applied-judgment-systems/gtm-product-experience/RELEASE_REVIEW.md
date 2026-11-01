# Frontend-only experiment after Design split — November 1, 2026

Validated Design Director integration is now isolated in [PR #7](https://github.com/glichtenthal/agent-skills/pull/7). This branch restores Design's canonical directory to main/stable 1.3.1; there is no Design learning diff in this PR. Earlier mixed source and metadata remain at immutable commit `3347cbfc28b217be421ceeb451013d23c30f1f40` and in existing evaluation references. No history or evidence was deleted.

Frontend's tested instruction payload remains candidate 1.3.2-rc.1, SHA-256 `82a6da544174a6e4486ede5f0594f70bb0dc30a36d569ffedae7a9e23866a01c`. Collection identifier 1.3.2-rc.3 distinguishes this Frontend-only composition from the mixed candidate and Design-only collection. Release/install flags remain false; published stable versions/assets are unchanged.

**Hold this PR.** The [unchanged scored evidence and reporting correction](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/release-review-2026-11-01/reporting-correction.md) show a rollback assertion pass-to-fail regression inside an already failed case. Applied implementation capability does not erase it. No rubric is waived, regraded or weakened by this split.

The shared evaluator is owned by [Steward infrastructure #5](https://github.com/glichtenthal/ai-project-steward/pull/5), not duplicated here. Before any later Frontend integration, refresh this branch against then-current main, preserve approved Design changes, and independently review collection/version metadata and actual diffs. Do not treat this held source as an upgrade path or publish the experimental payload through Design's release.

No model evaluations, installations, releases, merges or recurring services were run for this source-only split.

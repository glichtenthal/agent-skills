# Design-only integration review — November 1, 2026

## Scope and identity

This PR changes only Design Director learning guidance and its candidate metadata, plus collection bookkeeping, existing CI and this review record. The canonical directory remains `skills/product-design-director`; no second instruction copy or evaluator is introduced. Existing Design responsibilities, approval requirements, reference templates and UI invocation metadata are unchanged.

Design candidate remains **1.3.2-rc.1**, SHA-256 `4039da168236b1ca58221a9ea028fbc2cb859ac95b8e9825270ba7febf692e0a`, byte-identical to the evaluated payload. Collection **1.3.2-rc.2** distinguishes this Design-only composition from the earlier mixed experimental collection. Frontend Engineer directory remains byte-identical to main/stable **1.3.1**, SHA-256 `180c7aa9942bcc94d9dcd066e4b65dd634331e72e847cc4f3d955ed88c1e20f6`. Stable published 1.3.1 assets are not changed. Release/installation flags remain false.

## Existing evidence, not a new evaluation suite

- [Paired Design report](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/pilot-2026-10-31/design-candidate.md): 15/1/2 baseline versus 16/0/2 candidate assertion pass/fail/not_run; one narrow procedural difference, repeated in a second pair. AI judgments are not human approval or broad performance proof.
- [Confirmation evidence](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/pilot-2026-10-31/confirmations.json).
- [Applied handoff and responsive test](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/release-review-2026-11-01/applied/applied-test.md): actual specification and implementation with controller browser checks and independent AI screenshot/static review. The implementation used experimental Frontend 1.3.2-rc.1, not stable Frontend; this is not a new live test of the split collection. Split compatibility is checked against unchanged templates and the stable engineer's version-1.0 contract.

Screen-reader speech, native zoom and cross-browser/device behavior remain unverified. No model rerun is justified for this byte-identical source split.

## Merge versus release

Recommend Design-only source merge after explicit human approval and green integrity checks. First merge approved [Steward infrastructure #5](https://github.com/glichtenthal/ai-project-steward/pull/5) so the referenced optional source quality-review protocol is available on main. This dependency applies to skill-improvement review; normal Design work does not require installing Steward or Python.

[Original specialist #5](https://github.com/glichtenthal/agent-skills/pull/5) retains Frontend's experiment and all original history. Do not merge it while its rollback assertion is regressed. Do not bundle its experimental payload into a Design-only release.

A later release proposal must select a final version/tag, update only approved metadata/collection composition, create the existing-format standalone Design ZIP (canonical six files and source hash), verify its digest and references, and get separate publication approval. Installation is another explicit approval, with a verified backup and exactly one chosen installation directory. No merge, release, archive publication, installation or scheduler is performed by this PR.

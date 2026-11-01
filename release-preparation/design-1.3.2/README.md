# Standalone Design release preparation — 2026-11-01

Prepared from merged source `899f24d98b2fa2450ffcaf0f39c39c825c4a0110`. No instruction, UI, reference, specialist metadata or collection version changes. Role candidate remains **1.3.2-rc.1**, target stable **1.3.2** only after approval. Collection remains 1.3.2-rc.2; no collection or Frontend release is proposed. See `receipt.json` for exact identities and checks. The unpublished ZIP and checksum are local review artifacts, not committed or uploaded.

## Reproduction

From the reviewed checkout, stage the six canonical files under `product-design-director/`: LICENSE, SKILL.md, agents/openai.yaml, metadata/release.json, references/experience-specification.md, references/visual-design.md. ZIP them in lexicographic order with ZIP_DEFLATED, 2000-01-01 00:00:00 member timestamps, Unix regular-file permissions 0644 (`external_attr=0o100644<<16`), no extra members. The receipt digest identifies this candidate archive; final stable metadata will require a new artifact and checksum. Extract into a fresh temporary directory and compare every member byte-for-byte with source. Do not install this candidate into an active provider.

## Verification and limits

Local clean extraction, exact six-file membership (same layout as published stable), source-byte parity, instruction hash, relative-reference closure and UI entrypoint checks passed. Both bundled references and existing contract 1.0 remain unchanged. The full stable Frontend directory is unchanged. Static source review preserves experience specification, selected/approved gates, accessibility, scoped ordinary fixes and Steward/engineering coordination; this is not fresh behavioral proof.

The attempted isolated Codex runtime load test was rejected BEFORE execution by automatic approval review because it would export local skill contents to the model execution service. No workaround or credential copy was attempted. Actual runtime load, natural activation/nonactivation, post-install smoke and provider compatibility are NOT verified. Approval for that specific model-backed smoke test is required to close the load/routing gap. Existing applied evidence used experimental Frontend; it does not prove a fresh live stable-Frontend pairing. Screen-reader speech, native zoom and cross-browser checks remain absent. No new large evaluation campaign occurred.

## Publication decision and rollback

Recommend resolving the bounded runtime/load gap before approving stable publication. Then separately authorize a metadata-only preparation of standalone 1.3.2 (same instruction hash), review its final diff/archive/digest and approve publication of an exact standalone tag and assets. Do not mark installation approved, change the collection or bundle the held Frontend experiment. Source approval, publication and installation remain separate. No release/tag or active installation has occurred.

For any later authorized installation, first identify the active provider and one exact target directory; record its existing version/hash, make a separate byte-verified backup, stop sessions using that target, inspect the approved archive in temporary staging, replace only that directory and start a fresh-session smoke test. On failure, stop the new session, move the candidate aside, restore the verified backup to the exact original directory, compare all restored files/hashes and run a fresh-session stable smoke. Do not overwrite another provider/cache or run the generic installer (its Steward pin remains separately unreviewed).

If restoring published Design 1.3.1 is needed instead of a backup, use the unchanged `product-experience-v1.3.1` standalone asset with SHA-256 `338428f6b865abc44bb52ccb638bcfb7d0839f237076f8fce8806414e517749b`, verify its checksum and inspect before the same one-directory restore. Keep old release assets/tags intact; reverting source alone does not restore an installed directory. No production rollback is needed now because none was modified.

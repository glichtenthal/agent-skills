> Publication finalization: user explicitly approved standalone publication after reviewing head `1a99aeb8fbf85935ef96a8e12195690482ba968e`. Stable metadata now identifies 1.3.2, approved for publication; installation remains false. Final `receipt.json` and SHA256SUMS supersede candidate digests. Historical preparation context below is retained; publication is executed only after final CI/integrity gates.

# Final standalone Design 1.3.2 approval package

Prepared from approved Design-only main `899f24d98b2fa2450ffcaf0f39c39c825c4a0110`. Role version **1.3.2**, status **candidate**, publication **unreleased**, release/install flags **false**. Proposed standalone tag `product-design-director-v1.3.2`. Collection stays 1.3.2-rc.2; no collection or Frontend release is proposed.

Instruction SHA-256 `4039da168236b1ca58221a9ea028fbc2cb859ac95b8e9825270ba7febf692e0a` is unchanged. The only canonical skill edit is Design metadata. References, UI and license are unchanged; the full Frontend directory remains stable 1.3.1. Final artifact source identity, six members and checksum are in receipt.json / SHA256SUMS. ZIP remains local, uncommitted and unpublished.

## Evidence and decision

[Authenticated smoke](SMOKE.md), actual redacted outputs and command observations resolve the earlier authentication/load gap. The previous rc1 receipt is retained as rc1-receipt.json. [Proposed release notes](RELEASE_NOTES.md) distinguish bounded evidence from limitations.

Prior evidence: [paired report](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/pilot-2026-10-31/design-candidate.md), [confirmations](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/pilot-2026-10-31/confirmations.json), [applied handoff](https://github.com/glichtenthal/ai-project-steward/blob/74c834a928d91408768095da9edaa79e55f82490/learning/results/release-review-2026-11-01/applied/applied-test.md). The latter used experimental Frontend, not a live stable pairing. Model identity in the new smoke was not emitted. Screen-reader, native zoom, cross-platform/browser and real-user outcomes remain unverified. These constrain claims rather than blocking this controlled standalone release.

Recommend publication approval after reviewing this exact candidate and green CI; no further large evaluation campaign. No publication, tag, merge or active installation is authorized by preparation. Final archive metadata intentionally records unapproved candidate provenance; approval does not retroactively change bytes. If stable-status/approval metadata must be changed before publication, prepare and review a replacement artifact/digest first.

## Reproduction and validation

From the receipt source commit, archive the six canonical role files in lexicographic order under product-design-director/. ZIP_DEFLATED, timestamps 2000-01-01 00:00:00, create_system=3 and external_attr=0o100644<<16, no extra members. Extract fresh, compare every source byte, validate metadata SHA and false approval flags, local reference closure, UI entrypoint and stable archive member parity. Compression-library versions can affect ZIP bytes; the exact prepared digest identifies the reviewed artifact. Packaging checks do not substitute for behavioral evaluation.

## Installation and rollback (only after separate approval)

For any later authorized installation, first identify the active provider and one exact target directory; record its existing version/hash, make a separate byte-verified backup, stop sessions using that target, inspect the approved archive in temporary staging, replace only that directory and start a fresh-session smoke test. On failure, stop the new session, move the candidate aside, restore the verified backup to the exact original directory, compare all restored files/hashes and run a fresh-session stable smoke. Do not overwrite another provider/cache or run the generic installer (its Steward pin remains separately unreviewed).

If restoring published Design 1.3.1 is needed instead of a backup, use the unchanged `product-experience-v1.3.1` standalone asset with SHA-256 `338428f6b865abc44bb52ccb638bcfb7d0839f237076f8fce8806414e517749b`, verify its checksum and inspect before the same one-directory restore. Keep old release assets/tags intact; reverting source alone does not restore an installed directory. No production rollback is needed now because none was modified.

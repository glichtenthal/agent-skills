# Production Frontend Engineer 1.3.2

Standalone Frontend release authorized on November 15, 2026. Tag: `production-frontend-engineer-v1.3.2`. The collection, Design and Backend are not released or modified by this change. Existing release assets and tags remain intact.

The reviewed SKILL.md, references, agents/openai.yaml and LICENSE are byte-identical to the tested 1.3.2-rc.1 payload. Only release metadata changes from that candidate. Instruction SHA-256: `881a39c57534cc0d246b7a46f55f011d7a7bcab3f31b953591ffdfee9c5e9cad`.

Read [release notes](RELEASE_NOTES.md) and the [bounded evidence summary](EVIDENCE.md). Published checksums identify the final archive, not the earlier RC. Publication authorization does not claim universal reliability or authorize changing active installations.

The prepared final archive is 16,125 bytes. Its SHA-256 is `80c22c5034fde5d952159ebbd66f52950ab25bd4e62180c8818f0d44e0d9dd7c`; see [SHA256SUMS](SHA256SUMS). Fresh extraction matched all six staged files, a repeated build reproduced the digest, and all five nonmetadata files matched the tested RC. Final commit identity and live download verification are separate release gates, not inferred from this preparation record.

## Build and verify

From the tagged source, package exactly these files beneath `production-frontend-engineer/` in lexicographic order:

```text
LICENSE
SKILL.md
agents/openai.yaml
metadata/release.json
references/release-readiness.md
references/runtime-ui-reliability.md
```

Use ZIP_DEFLATED, 2000-01-01 00:00:00 timestamps, Unix regular-file 0644 permissions and no extra fields or directory entries. Do not package .git, tests, evaluation logs, site files, held roles, private configuration or this release-preparation directory. Compression implementations may affect the archive digest; published SHA256SUMS identifies the actual released bytes.

Extract to a fresh directory, check exact membership and compare every byte against the tagged role. Validate frontmatter, description length, both local references, UI metadata and instruction hash. Stable metadata must read version 1.3.2, status stable, publication approved, release_approved true and installation_approved false. Verify CI and the tag's exact source commit before publication. After publication, download the actual release asset and repeat the byte and digest comparisons; a local ZIP alone is insufficient.

The local release process uses existing Node/YAML/ZIP tools and explicit structural checks, not an unapproved Python environment. No behavioral instructions changed during finalization. See EVIDENCE.md for the difference between application tests, explicit CLI loading and native desktop loading.

## Installation and recovery

This source push does not overwrite active installations. A previously approved RC test installation remains separate. For a later authorized stable installation, verify the downloaded checksum, inspect/extract outside discovery, identify one target/provider, back up outside discovery and replace only that target. Do not edit managed plugin caches or create a second same-named enabled copy. A path-specific disabled cache entry may need rechecking after plugin updates.

Retain the verified prior directory for rollback. Preserve any intervening changes before restoring it, then compare all restored bytes and run a fresh target-surface check. A source revert does not itself restore an installed skill. For a publication defect, preserve evidence and report before removing or replacing a public release/tag; never force-push an existing shared tag silently.

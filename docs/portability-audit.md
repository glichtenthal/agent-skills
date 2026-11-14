# Portability audit — November 13, 2026

## Starting state and scope

Repository `glichtenthal/agent-skills` is public; remote `origin` uses HTTPS. Initial branch
`main` at `6bbf151` tracked `origin/main`, with no staged changes, one local branch, modified
`decisions.md` and untracked `evals/`. Fetch confirmed local and remote main had zero divergent
commits. Existing work was retained on `codex/two-mac-portability`; nothing was reset or discarded.

The portability change includes that existing offline evaluation work so it can reach the
other Mac. It does not merge the PR, run a provider, change released skills or publish a release.

## Content classification

Reviewed for version control: evaluation Python modules/tests, four synthetic fixture cases,
rubric/configuration/source manifest, retained public Ground Truth instructions, research,
protocol/reviewer guidance, gold/model decision record, and sanitized connectivity preparation
documents/validation summaries. Existing curated release receipts remain tracked.

Local-only: `evals/local-runs/` (about 1.1 MB at audit), raw output/provider response/event data,
billing SQLite files and sidecars, secrets and environment files, virtual environments/caches,
private inputs, future path-bound execution approvals, editor/Codex machine settings and
temporary outputs. These are excluded by directory conventions and root/nested ignore rules.
No existing tracked file matched the expanded ignore rules. Original local run evidence was
left in place, outside the proposed commit.

Secret review used credential/private-key patterns and inspection of credential-related
references, without reading credential stores or printing credential values. No recognized
credential payloads were found in candidate source/documents. Credential references are names,
guards or explicitly fake test values. This is a scoped review, not a guarantee against every
possible secret format. Raw data placed in arbitrary nonignored paths still requires review.

## Paths and dependencies

- Offline runtime derives repository/fixture paths from its module location and uses Python
  3.9+ standard library, SQLite and Git; there are no pip/SDK dependencies.
- Connectivity command text pins `/Library/Developer/CommandLineTools/usr/bin/python3`, Python
  3.9.6 and the original absolute clone/output paths. These are reviewed hash bindings, retained
  unchanged as preparation evidence; they are not setup commands or portable live authority.
- Historical plans in `docs/superpowers/plans/` mention prior clone paths; old QA/release records
  mention localhost and temporary paths. They do not participate in evaluation execution.
- `scripts/check_offline.py` locates the clone independently of the caller's working directory.
  It changes no frozen evaluation source bytes and provides no live execution interface.

## Verification results

- Original checkout: **53 tests passed, zero failures/skips**, Python 3.9.6, plus valid frozen
  fixture manifest (four cases / 24 conversations).
- Relocation: copied versioned source and candidate evaluation/check script into a separate
  temporary Git repository whose path includes spaces. From `/tmp`, invoked the relocated
  check script by its path: **53 tests passed, zero failures/skips**, fixture validation passed.
  This exercises mock/provider-shaped integrity pipelines and CLI checks at a different root.
- Before/after SHA-256 comparison: **all 36 original non-run evaluation files unchanged**,
  including approval records, command text, source manifest and Python runtime modules.
- Ignore probes passed for environment/credential files, raw runs/events, private data, local
  approvals, ledgers/sidecars, logs, virtual environments and local Codex settings.
- `git diff --check` passed. Candidate file review excludes local-run evidence, secrets,
  databases, environment settings and temporary data.
- Existing product-skill instruction SHA-256 and candidate-approval metadata checks passed.

The source-manifest input fingerprint remains
`8ff0c1ddfff307e21931c44807e0f1e373da07bb5523f2771e393d7d417c6e24`.
Historical `gold_review: pending_human` output is preserved; the newer hash-bound
`approved-decisions.json` governs gold/model decisions. All live authorization flags remain false.

## Review and remaining limits

Review the existing evaluation addition and portability documentation in the PR. No original
file requires deletion or rewriting for offline portability. Preserve the machine-bound
connectivity package; a future executable replacement requires explicit review/approval.
Another physical Mac and another Python version have not been tested; run the same offline
check after cloning there. Excluded local evidence is not backed up by GitHub. Live provider
access, spending and behavioral outcomes remain untested and unauthorized.

During final staging, `evals/adapters/codex_cli.py` and `evals/evidence.py` appeared as new work
outside the initial audit snapshot. They were left untouched and excluded from this commit.
Validation was repeated against only the exact proposed Git index in another relocated Git
repository: all 53 tests and fixture validation passed. These concurrent additions are not
covered by this audit; review their CLI path and runtime-hash implications separately before
including them in a later PR. The runtime digest includes all top-level/adapter Python files,
so adding modules changes that digest even when the original files remain unchanged.

## Approved combined checkpoint — November 13, 2026

Greg approved preparing and publishing exactly 19 incremental paths to existing draft PR #18,
without merge, released-skill changes, live inference, subscription allowance or spending. The
combined PR contains 54 unique changed paths relative to main. This checkpoint includes the
previously concurrent Codex hardening work; the 53-test audit above remains historical.

The reusable addition includes the Codex adapter/isolation contracts, coordinator, simulation,
evidence utilities, tests, protocol, fail-closed decision checklist and sanitized verification
summaries. Frozen cases/rubric/run-config/source manifest, instruction snapshot and approved
interpretation/model decisions retain their published bytes.

The three newly excluded originals are `codex/native-feature-evidence.json`,
`codex/offline-tests.txt` and `codex/hardening-tests.txt` under the Ground Truth experiment.
Together with 206 previously ignored files, 209 local records remain excluded and untouched.
The tests now use `evals/tests/fixtures/codex-feature-metadata.json`, a sanitized historical
projection retaining the original capture SHA-256, required feature rows and reviewed metadata
hashes. Raw argv/path, timestamps, diagnostics and unrelated feature output are omitted; the
fixture explicitly states that it does not verify the current Mac. No test was removed/skipped.

Verification: the combined checkout and relocated candidate passed all 90 offline tests with
zero failures/errors/skips, plus frozen fixture validation. Retained simulation integrity
verified 24 valid conversations, 48 simulated invocations, zero actual inference invocations
and 48 pending semantic judgments. The exact staged contents are checked again before commit.
No model behavior or skill benefit follows from these results.

Remaining limits: the Codex CLI location/version/binary SHA remains pinned; native effective
configuration/tool/prompt activation and guaranteed included-only funding are unresolved. The
new modules change the runtime digest, invalidating reuse of historical connectivity bindings.
Original capture hashes in summaries refer to excluded local evidence, not a fresh observation.
A second physical Mac remains untested and must run the same offline checks after cloning.

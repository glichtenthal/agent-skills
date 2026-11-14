# Codex-runtime variant — offline preparation only

This variant reuses the approved, unchanged four cases, three A/B/C branches, two arms,
one repetition, scoped gold decisions, scoring and human-review machinery. It is a
**Codex-runtime experiment, not an API-equivalent evaluation**. No behavioral evidence
has been collected. No live preflight or experiment is authorized by this document.

## Pinned controller inputs

The authoritative executable settings are `evals/adapters/codex_cli.py`, retained with
every run. The preparation pins:

- CLI: `codex-cli 0.167.0-alpha.4.1`.
- Binary: `/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex`.
- SHA-256: `7cb8700a47be3c81bb3c5efbf2d2adc716ce3db4806e9dc992f2925f78b2b194`.
- Requested model: `gpt-6.1-sol`; low reasoning; default service tier; OpenAI provider.
- Ground Truth v1.2: commit `56b41b1459ec82df140e6fac7e7316f116d36461`, retained
  `sources/ground-truth-v1.2.txt`; SHA-256
  `33b750543fe8c3ca758712b98d15accc4e34564f907e3c58d55a9fb5c4b68c06`.

The binary hash is checked before any actual process dispatch. CLI upgrades require a
new reviewed pin and offline fixtures. The model is **not immutable**. Request identity,
UTC start/end timestamps, raw events, returned model when exposed, requested configuration
and hashes are retained. An absent returned identifier is unknown, not filled from the
requested identifier. An observed different identifier aborts for disclosure/review.
Python, OS/platform, repository HEAD/dirty state and frozen controller bytes are retained.

## Isolation and continuity

There are 24 independent persisted CLI sessions: 4 cases × 3 branches × 2 arms. The
opening is repeated independently for each branch. Each continuation resumes only its
own exact first-turn UUID. No `--last`, fork or `--ephemeral` is used. Baseline/treatment
ordering uses the existing seeded schedule. A duplicate UUID, cross-arm/workspace binding,
missing history, unknown event, tool activity, compaction, failed/truncated turn or
reported retry aborts the batch. There are no controller retries or automatic restarts.

Each session starts in a new opaque empty working directory. Both turns request the same
configuration. Only `developer_instructions` differs between arms: baseline receives
the common answer contract; treatment receives that contract followed by the exact
retained skill bytes. Fixtures, alternatives, rubric, branch kinds, arm labels, source
repository and approval records are never passed in the prompts. Review transcripts
reconstruct the matching first answer and continuation from that same session's raw events.

The controller requests `--no-daemon`, `--strict-config`, `--ignore-user-config`,
`--ignore-rules`, zero project-document bytes, no fallback project documents, no skill
catalog/bundled instructions and skipped host skill discovery. Apps, plugins, skill search,
memories, chronicle, external memory import, hooks, multi-agent features, shell, code,
browser, computer-use, image generation/viewing, sleep, goals, workspace dependencies and
in-app automation capabilities are requested disabled. Memory generation/use are also
explicitly false, notifications empty and web search disabled. Read-only sandbox and
approval-never are requested. Runtime SQLite/log
paths are session-local. The process environment is allowlisted, retaining existing
HOME/CODEX_HOME authentication location without changing global configuration. API keys,
provider endpoint overrides and arbitrary config environment variables are excluded.

The protected native feature resolver confirmed all 33 disable flags false and
`skip_host_skill_discovery` true; see the locally retained `native-feature-evidence.json` (excluded from Git). This was a metadata
command with network access and filesystem writes denied, with no inference or sessions.
`features list` does not support `--strict-config` or `--ignore-user-config`; it does not
certify the exact `exec` context. Native full configuration and tool exposure remain
unverified. These are **verified controller inputs and feature states, not proof of the
native effective context**.
Managed/cloud requirements, internal prompts, flag support, implicit skill routing and
actual session persistence still require an approved preflight. A read-only sandbox alone
does not hide files: the no-tool configuration and trace checks are essential. No gold
directory is mounted as a model instruction. Hidden reads cannot be ruled out by mock tests.
Unsupported or ineffective isolation controls block execution; do not silently drop flags.
Explicit context injection tests the skill text, not automatic native skill discovery.

## Native assertions and inspection limits

The ignored `unified_exec=false` override was removed. This CLI keeps that feature true
even when requested false. `shell_tool=false` is the relevant command-tool flag; the
native tool catalog must independently confirm no tools are exposed. Empty MCP/hook
table overrides were also removed: they did not prove inherited entries were cleared.
Instead, hooks are feature-disabled and the native effective MCP map must be explicitly
empty or every server explicitly disabled. There is no claim that an empty CLI table
can erase a merged configuration.

Before any actual turn, `assert_native_isolation` requires a structured export of the
native **exec** context, bound to CLI version/hash, the requested configuration, first-turn
command, workspace and environment hash, captured within five minutes. It checks:

- All required feature states, a successful probe and no unreviewed diagnostics.
- Every requested effective setting; no unexpected instruction-file override.
- Empty exposed tool, MCP and skill catalogs; no enabled MCP configuration entry.
- Current managed policy and inspection without persistent session creation.
- Native baseline/treatment prompts whose only difference is the exact skill payload,
  injected once at developer priority. Missing/duplicate activation, baseline leakage,
  different context, and recognized project/memory/catalog/gold injection markers block.

A standalone `effective_configuration_verified: true` cannot satisfy these assertions.
`native-feature-evidence.json` is deliberately **insufficient**: feature metadata is only
one part of native evidence. Synthetic records are accepted solely by explicit test mode;
production rejects them. Structured records validate consistency/provenance declarations,
not an authenticated capture producer. Prompt marker checks are additional diagnostics,
not a universal detector for arbitrary hidden context. Golds/rubrics remain outside
generation contexts, with the existing payload construction and canary tests unchanged.

Native `debug prompt-input` is documented, but the installed diagnostic failed for both
arms with `Operation not permitted` before producing any prompt when all network access
and filesystem writes were denied. The protected feature diagnostic succeeded under the
same policy. The failure does not establish whether the prompt diagnostic needed a write,
network operation or another restricted resource. It establishes that a reliable
non-persisting, no-network prompt-inspection path has **not** been verified here. No retry
with relaxed protections, daemon or new service was introduced. No model turn or native
persistent session was created. Full config/tool/prompt exports matching the exact exec
flags are not currently collected; absence blocks execution rather than generating an
attestation from controller inputs.

Unavoidable/remaining differences include the common native Codex harness, forced
`unified_exec` capability selection, shared CODEX_HOME storage, managed configuration and
potential model drift. Session-local `sqlite_home`/`log_dir` do not move all persisted
history out of CODEX_HOME. Exact-ID continuation is supported by installed CLI help and
offline simulations, but not yet exercised in a real inference session.

## Funding and disabled execution

`forced_login_method=chatgpt` is mandatory; API/unknown authentication is rejected.
No credential file is read by this controller, no secret is printed, and no API key is
used. Authenticated CLI operation would use its existing secure authentication store.
There is no API fallback, credits purchase, spending authorization or reset operation.

Official account/rate-limit metadata can distinguish included quota and credit details
**when those fields are supplied**. It does not establish an atomic, request-local
included-only spending guarantee. Included usage may roll over to credits, and balances
can change between checks. No verified included-only CLI enforcement was found.

Therefore `funding_assessment` always returns `included_only_guaranteed: false`, and
every non-injected execution currently fails closed before process dispatch/output
creation. A generic approval, positive quota or self-asserted included-only flag cannot
bypass this gate. `execution-state.json` is a decision checklist, not executable approval.
If no authoritative included-only enforcement can be established, stop for Greg's
separate decision; any changed funding policy requires a bounded code/config review.
No dollar guarantee is inferred from subscription login or token counters.

## Evidence, grading and human review

Structured events retain argv, exact input prompts, requested config/hash, environment
keys/hash (no values), session IDs, timestamps, sanitized stdout/stderr, final answer and
available token usage. Output lacks billing data or returned-model metadata unless the
CLI supplies it. Missing values remain unknown. There is no claim of a CLI equivalent to
the Responses adapter's 8,192-token output limit, 16,000-byte input guard, encrypted item
replay or persistent dollar-reservation ledger. A process timeout is not a billing cap
and cannot prove server-side cancellation. Native transport may retry without exposing it;
observed retry diagnostics invalidate the run. No seed/temperature control is invented.

The existing verifier, blinded packets, review templates, graders, transition scores,
regression comparison and reports accept Codex evidence. Comparisons reject different
runtime/configuration/evidence kinds. Mock results always remain synthetic, with zero
actual inference and no behavioral success inferred from label agreement.

Before real evaluation, name two independent human reviewers and a separate adjudicator.
Both reviewers independently score both answers in all 24 conversations: 48 answer
judgments each, 96 records total. Each scores claim correctness, recommendation quality,
evidence quality, unsupported claims and fabrication. Disagreements stay unresolved until
the separate adjudicator records a bound decision. Neither automated grading nor this
assistant's simulated review counts as an independent human reviewer. Supply approved
scoped gold/alternatives and reviewer guide separately. Packet blinding removes arm/skill
metadata, but style may reveal treatment. Reviewer identity/independence is organizational,
not authenticated by the JSON records.

## Smallest safe next preflight

1. The approved metadata-only preflight and protected offline hardening checks are
   complete. ChatGPT login and separate quota/credit fields were observed; no credit
   provenance or included-only enforcement was inferred. User defaults contain memory,
   plugins and MCP integrations; system/project config files inspected were absent, the
   global AGENTS file empty, and cached cloud policy expired. Current native exec
   configuration, tool catalogs and prompts remain blocked as described above.
2. Resolve funding enforcement. If included-only cannot be enforced, execution remains
   blocked pending an explicit decision and separately reviewed policy; a balance snapshot
   is insufficient. Confirm human reviewers/adjudicator and controlled native environment.
3. Do not expand this framework to work around missing native inspection. A separately
   scoped, network-denied diagnostic with strictly confined local state may be considered
   if a safe non-persisting inspection path becomes available; it must not silently create
   sessions. Only after native isolation and funding gates are resolved, seek separate
   approval for a harmless **two-turn** inference
   preflight in the isolated runtime to verify exact-ID resume, effective payloads/settings,
   event schema, usage and tool absence. Keep this out of experimental results.
4. Review that evidence, then separately authorize the full 24-session/48-turn experiment.
   No smoke success authorizes skill edits, GitHub updates or release.

## Offline commands

From the repository root, choose a fresh output directory:

```bash
python3 -B -m unittest discover -s evals/tests -v
python3 -B -m evals.codex_demo --output evals/local-runs/codex-v1-offline
python3 -B -m evals.runner verify --run evals/local-runs/codex-v1-offline
python3 -B -m evals.runner report --run evals/local-runs/codex-v1-offline
python3 -B -m evals.runner review-packet --run evals/local-runs/codex-v1-offline
python3 -B -m evals.runner review-template --run evals/local-runs/codex-v1-offline
```

`codex_demo` injects a local simulator; it never launches Codex or reads authentication.
No live launch command/switch is exposed. The underlying coordinator is also fail-closed.
Existing API approvals/configuration remain unchanged. These controller changes alter
runtime hashes, so any earlier prepared API command must be revalidated if that route
is later chosen; do not silently refresh an approval's bound hashes.

Provider references (read-only documentation, not account verification):
[configuration](https://learn.chatgpt.com/docs/config-file/config-reference),
[non-interactive sessions](https://learn.chatgpt.com/docs/non-interactive-mode),
[pricing](https://learn.chatgpt.com/docs/pricing),
[account/rate limits](https://learn.chatgpt.com/docs/app-server).

## Portable regression evidence

The original `native-feature-evidence.json`, `offline-tests.txt` and `hardening-tests.txt`
remain local execution records and are excluded from Git. Regression tests instead read
`evals/tests/fixtures/codex-feature-metadata.json`, a labeled sanitized projection of the
historical capture. It retains the original capture digest, reviewed pin/configuration hashes,
required feature rows and explicit unverified-current-machine state, while dropping argv,
absolute binary location, timestamps, raw diagnostics and unrelated feature output.
It is not a new native observation, prompt export or execution authorization. Original
verification-summary hashes continue to reference the retained original local capture.

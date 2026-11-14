# Agent Skills project status

Updated November 13, 2026 (America/New_York). Read this at the start of work on either Mac.

## Objectives and shared source

Maintain the Agent Skills catalog and its human-led judgment skills; develop reproducible,
isolated experiments before proposing changes to released instructions. GitHub repository:
https://github.com/glichtenthal/agent-skills ; integration branch: `main`.
See [two-Mac setup and workflow](docs/two-mac-workflow.md) and [evaluation guide](evals/README.md).
Unmerged work travels on its pushed branch/PR. Local-only runs and Codex chats do not synchronize.

## Active experiment: Ground Truth, Issue #17

- [Issue #17](https://github.com/glichtenthal/agent-skills/issues/17): calibrated revision versus
  capitulation under pushback. Four synthetic cases, three independent continuations, two arms:
  24 two-turn conversations / 48 planned calls for a future one-repetition smoke.
- Offline remediation and Codex hardening are complete. Current verification records **90/90 offline tests**
  passed, zero skipped. Mock and injected provider-shaped checks establish infrastructure
  behavior only: **no live behavioral evaluation, no measured skill benefit, no provider cost**.
- Current authoritative interpretation/model decision:
  [approved-decisions.json](evals/experiments/017-ground-truth/approved-decisions.json), decision
  `issue17-gold-and-model-approval-2026-11-13`. Greg approved scoped gold interpretations,
  documented alternatives, substantive recommendation revision, specific-constraint abstention
  and mutable model identifier drift. These decisions remain approved.
- Frozen case SHA-256: `2a16ddff1dbf63c9176bef0998f4557d160dfe5dbde744d18540e9ddd8a44af3`.
  Rubric: `d95da619b3faaf07c8e3c136e6ade6e74f8005908373b23b12de5265105fa984`.
  [Source manifest](evals/experiments/017-ground-truth/source-manifest.json) pins Ground Truth
  v1.2 at `56b41b1459ec82df140e6fac7e7316f116d36461` and the retained instruction bytes.
- Earlier `verification.md`, protocol/configuration, root decision text and `evals.readiness`
  retain provisional/historical wording. The approved decision record supersedes that wording
  for gold/model decisions only. Do not re-request these unchanged decisions or treat old
  readiness output as current live authorization. The GitHub issue/comment also predates the
  local remediation and approvals; this file captures the later state without rewriting history.

## Outstanding approvals and safeguards

**Live execution remains unauthorized.** Connectivity execution, spending and credential reuse
are false in the prepared one-request package; full experiment execution/spending are false.
No credential inspection/provisioning, live request, paid run, automatic retry or batch expansion
is included in portability work. The proposed one-request allowance is $0.10; the proposed
48-call experiment cap is $10. Neither budget is approved.

Before any future live run: obtain a concrete execution decision bound to exact inputs,
settings, runtime source, paths, credential use, limits and the persistent ledger. Assign two
independent human reviewers and a separate adjudicator. Output review is not completed.
Ledger reservations survive uncertainty; unknown usage keeps holds, overruns freeze dispatch,
and no fresh ledger or second Mac may bypass those holds. There is no live runner CLI switch.
The saved connectivity shell text is review material, not a setup command.

No result authorizes released-skill edits, merge, installation, publication or release. Remaining
eight cases, balanced initial polarities and case-clustered uncertainty analysis are future work.
Native skill discovery, real authentication, billing and model behavior remain unverified.

## Portability checkpoint

- Initial audit: `main` at `6bbf151`, tracking `origin/main`, one local branch, HTTPS `origin`
  pointing to the repository above; no staged files. Existing work was modified `decisions.md`
  plus untracked `evals/`. These files must be included in the portability PR to reach another Mac.
- Runtime source already derives the repository path from `__file__`. Python 3.9+ standard
  library and Git are sufficient; no third-party evaluation dependencies were found.
- Added location-independent `scripts/check_offline.py`, local-artifact ignore rules and
  setup/handoff guidance. Original experiment source, decisions, hashes and preparation
  artifacts are preserved. Historical connectivity absolute paths are intentional bindings,
  not dependencies of offline evaluation. They require a new reviewed package before relocation.
- Keep credentials, raw execution logs, SQLite ledgers, private data, machine settings and
  temporary outputs local. See the workflow's version-control table. Curated synthetic
  fixtures and sanitized preparation summaries are safe to review for GitHub.
- Current validation and audit results are recorded in [portability audit](docs/portability-audit.md).
- The approved 19-path checkpoint incorporates the Codex CLI adapter, isolation assertions,
  shared evidence utilities, simulation coordinator, regression tests and sanitized summaries.
  The earlier 53-test portability snapshot remains historical; it excluded this then-concurrent work.
- Codex simulation verified 24 independent conversations and 48 invocations, zero actual
  inference calls and 48 pending semantic judgments. This is a Codex-runtime variant, not an
  API-equivalent behavioral evaluation. Live execution remains blocked by unresolved native
  effective configuration/tool/prompt activation and guaranteed included-only funding.
- Regression tests use a sanitized historical metadata fixture, not the original local capture.
  The fixture is not current-machine evidence or execution authority. Raw capture and test
  logs remain ignored locally; original fixture/source/interpretation hashes are preserved.
- Greg approved preparing and publishing this checkpoint to existing draft PR #18 on
  `codex/two-mac-portability`; merge, release, inference, evaluation allowance and spending
  remain unauthorized. See the latest audit section for verification and portability limits.

## Next steps

1. Review the portability PR and merge after checks; clone/switch to that branch on the other
   Mac if continuing before merge. Run `python3 -B scripts/check_offline.py` there.
2. Use one active Mac per branch: clean tree, fetch/pull before work; review, commit, push and
   update this status before handing off. Keep meaningful changes in PRs against `main`.
3. If live work is later desired, review the connectivity package and approve a newly bound
   package for the intended Mac. Review its outcome separately before considering the full run.

# Working on Agent Skills from either Mac

GitHub is the shared source for code, synthetic fixtures, reviewed decision records and project
status. Each Mac has its own clone. A Codex chat, uncommitted edit, stash, credential or ignored
run directory does not travel with Git. Start a new chat in the clone and read
`PROJECT_STATUS.md`, `AGENTS.md`, and the relevant experiment records.

## Set up another Mac

Prerequisites: Git, Python 3.9+ with its standard library (including SQLite), and GitHub
authentication with push access for contributions. The offline suite was verified on Python
3.9.6; another Python version must pass the same checks before relying on it. No pip packages,
Node, SDK, API key, skill installation or paid account are required for evaluation development.
Configure Git identity and GitHub authentication separately on each Mac. Do not copy credentials
into this repository. Installing the catalog's skills is a separate operation (`install.sh`),
not a prerequisite for running the evaluation infrastructure.

In a parent directory of your choice:

```bash
git clone https://github.com/glichtenthal/agent-skills.git
cd agent-skills
git switch main
git pull --ff-only origin main
python3 -B scripts/check_offline.py
```

If continuing an unmerged PR, first `git fetch origin`, then
`git switch --track origin/codex/BRANCH-NAME` (or switch to the existing local branch).
Changes on that branch are unavailable on `main` until the PR is merged.

The check script finds the clone from its own location and changes to its root; it can also be
called by its actual path from another working directory. It runs all existing regression
tests and validates frozen fixtures. It removes the API-key variable from its own process and
blocks parent-process sockets. Existing child CLI tests select mocks or reject live adapters;
the script is an offline check, not an OS-level network sandbox. The ordinary commands in
`evals/README.md` run from the clone root. Use a unique output directory for every new mock run.
`evals.runner.REPO` derives from `__file__`; no particular username or clone location is needed.

## Start work

```bash
git status --short --branch
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c codex/describe-the-change
```

Proceed only with a clean working tree when switching branches or pulling. If there are local
edits, inspect them and commit them on their owning branch first. Never reset, clean, overwrite
or discard work just to synchronize. A local stash is not a cross-Mac handoff. If `--ff-only`
fails, inspect `git log --oneline --left-right HEAD...@{upstream}` and resolve the divergence
deliberately; do not force-push. Keep experiments and infrastructure changes on separate
branches when they can be reviewed independently.

## Finish and hand off

Update `PROJECT_STATUS.md` with completed checks, next steps, issue links and approval state.
Append significant decisions to `decisions.md`; retain original approval evidence and hashes.
Review the files and diff before staging explicit paths:

```bash
python3 -B scripts/check_offline.py
git diff --check
git status --short --untracked-files=all
git diff
git add PATHS-YOU-REVIEWED
git diff --cached --stat
git diff --cached
git commit -m "Describe the change"
git push -u origin HEAD
```

Open a PR against `main` on GitHub for meaningful changes, with verification results and
outstanding approvals. An unfinished handoff can use a draft PR and a clear checkpoint commit.
Never put credentials or raw execution artifacts in a checkpoint. Review and merge separately;
a push does not authorize experiment execution, installation or a release.

On the other Mac, fetch, switch to that same branch, and `git pull --ff-only` before editing.
Use one Mac as the active writer on a branch at a time. Push before switching computers; the
receiving Mac verifies a clean tree and pulls before continuing. If both Macs changed the same
branch, preserve both commits, resolve conflicts on a review branch, rerun checks, and push
normally. Never force-push a shared branch. After merge, return each clean clone to `main` and
pull with `--ff-only`; delete local branches only after verifying their work is preserved.

## What travels, and what stays local

| Version in Git | Keep local / out of Git |
| --- | --- |
| Source, tests, synthetic cases, rubric, pinned instruction snapshot and source hashes | API keys, `.env*` except sanitized examples, SSH/cloud credentials |
| Research/protocol, reviewed approval-state records, sanitized verification summaries | Machine settings, virtual environments, caches and temporary/build outputs |
| Project status, decisions, workflow documentation | Raw transcripts/provider responses, event logs, billing ledgers and private inputs |
| Existing curated release evidence and historical receipts | Future execution authorization records with local paths; use `local-approvals/` |

Put new raw runs and logs in ignored `evals/local-runs/` or outside the clone, private inputs in
`local-data/`, and future local execution approvals in `local-approvals/`. Ignore rules are a
backstop, not content classification: inspect every staged diff, including sanitized examples
and summaries. Existing curated `connectivity/regression-tests.txt` and validation JSON are
offline preparation evidence, not raw paid execution logs. Do not blanket-ignore experiment
JSON/JSONL or text: that would hide synthetic fixtures, hashes and decision evidence.

Local evidence is intentionally absent on a fresh clone. Existing links to `evals/local-runs/`
may therefore be unavailable. Keep original evidence on its originating Mac; a sanitized
versioned summary records its meaning without pretending the original artifacts moved. GitHub
is not a backup for excluded evidence. If a future paid execution must move Macs, stop first:
retain and securely transfer the SAME ledger, unresolved holds and complete evidence through
an explicitly approved private route, verify integrity, and approve the new path bindings.
Never create a fresh ledger to bypass spend already reserved on the other Mac. Do not execute
the same approval independently in two clones.

## Preserved machine bindings

The one-request `evals/experiments/017-ground-truth/connectivity/` package is historical,
hash-bound preparation, **not a portable launch entry point**. It pins an absolute clone path,
the Command Line Tools Python executable, Python 3.9.6, and an exact output path. Its command,
plan and runtime hashes must remain intact; execution/spending/credential approval is false.
On a different Mac or path, prepare a new reviewed package with new hashes and obtain explicit
execution approval. Do not substitute paths, flip approval flags or run the saved shell text
as part of setup. Gold/model-drift decisions carry forward; local execution authority does not.

Older `docs/superpowers/plans/` and release receipts also contain historical paths. They are
provenance, not dependencies of the evaluation runtime. Preserve their historical meaning.

## Codex offline hardening checkpoint

The offline check now covers 90 tests, including the Codex CLI adapter and isolation contracts.
`python3 -B -m evals.codex_demo --output evals/local-runs/UNIQUE-NAME` is local simulation only:
24 independent conversations / 48 simulated invocations, no native CLI inference or allowance.
The regression fixture at `evals/tests/fixtures/codex-feature-metadata.json` is a sanitized
historical metadata projection, not current native activation evidence. Raw native capture and
test logs stay local; the tests no longer require them.

Offline development requires no installed Codex binary. Real native dispatch still pins the
reviewed CLI location, version and binary SHA-256; on another Mac, do not silently discover or
substitute a different executable. Any changed pin needs separate review and fresh evidence.
Adding the Codex modules changes the runtime digest, so the historical connectivity package
cannot authorize these new runtime bytes. Native effective configuration/tool/prompt activation
and guaranteed included-only funding remain unresolved; inference and spending stay blocked.
Git synchronization grants no execution authority on either Mac.

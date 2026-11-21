# Product development skills

Use any of these three skills independently, or combine them for product work. [Explore the visual overview](https://glichtenthal.github.io/agent-skills/product-development/).

| Skill | Responsibility | Distribution |
| --- | --- | --- |
| AI Project Steward | Project decisions, approval boundaries, continuity, completion | [Canonical repository](https://github.com/glichtenthal/ai-project-steward) |
| Product Design Director | Product definition, interaction and visual design, rendered critique | [Skill folder](gtm-product-experience/skills/product-design-director/) |
| Production Frontend Engineer | Implementation, visual fidelity, technical verification | [Released skill folder](https://github.com/glichtenthal/agent-skills/tree/production-frontend-engineer-v1.3.2/applied-judgment-systems/gtm-product-experience/skills/production-frontend-engineer/) |

Install all three for the combined workflow; invoke the roles relevant to each task. A narrow frontend fix does not require a new design cycle. Design Craft is not a separate dependency.

## Install

Choose the AI Project Steward ZIP for your environment, and download the specialist skills you need:

- [AI Project Steward 2.1.3 for Codex](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.3/ai-project-steward-2.1.3-codex.zip)
- [AI Project Steward 2.1.3 for Claude Code](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.3-claude/ai-project-steward-2.1.3-claude-r2.zip) · [SHA256SUMS](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.3-claude/STEWARD-CLAUDE-R2-SHA256SUMS)
- [Product Design Director 1.3.2](https://github.com/glichtenthal/agent-skills/releases/download/product-design-director-v1.3.2/product-design-director-1.3.2.zip)
- [Production Frontend Engineer 1.3.2](https://github.com/glichtenthal/agent-skills/releases/download/production-frontend-engineer-v1.3.2/production-frontend-engineer-1.3.2.zip) · [SHA256SUMS](https://github.com/glichtenthal/agent-skills/releases/download/production-frontend-engineer-v1.3.2/SHA256SUMS)

Use the **r2 Claude Code archive** above. It corrects stable-release packaging metadata without changing instruction bytes. The [original ZIP](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.3-claude/ai-project-steward-2.1.3-claude.zip) and [original checksum](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.3-claude/STEWARD-CLAUDE-SHA256SUMS) are retained as historical audit assets. See the [correction record](https://github.com/glichtenthal/ai-project-steward/blob/main/docs/packaging-correction-v2.1.3-claude.md). Passing checks is not evidence of an incremental quality advantage over ordinary Codex.

**Claude Code:** Steward [v2.1.3-claude](https://github.com/glichtenthal/ai-project-steward/releases/tag/v2.1.3-claude) is a published, approved Claude Code CLI release, with bounded testing exceptions (10/10 behavioral PASS, 3/4 composition PASS, one cross-platform case not run). Verify its checksum, back up any active Steward installation outside skill discovery, and install one authoritative `ai-project-steward/` folder into the configured Claude Code skills location (normally `~/.claude/skills/`). Test in a fresh session. The instructions are byte-identical to the Codex v2.1.3 skill, but the distribution metadata is Claude Code-scoped.

**Native Claude (claude.ai):** The v2.1.3 Claude Code release is **not validated for claude.ai**. Keep an existing native-Claude installation unchanged until separately evaluated; the [historical Steward 2.1.2 ZIP](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.2/ai-project-steward-2.1.2.zip) remains available for its previously tested scope. For skills supported in native Claude, upload the ZIP through Skills settings rather than attaching it to a chat. Frontend 1.3.2 has bounded Codex validation only; Claude compatibility is not established by its release. No separate Design Craft installation is needed.

**Codex:** Use your skill installer with the linked skill folders above and Steward's canonical repository. The catalog shell installer supports Steward and Frontend as explicit options; it does not install Director. The default suite remains the four core judgment skills. If you use the optional GTM Product Experience plugin, avoid duplicate enabled copies of the same roles.

Install Frontend 1.3.2 into `~/.agents/skills` with its release pin and checksum checked:

```sh
frontend_installer="$(mktemp "${TMPDIR:-/tmp}/frontend-installer.XXXXXX")"
curl -fsSL https://glichtenthal.github.io/agent-skills/install.sh -o "$frontend_installer"
bash "$frontend_installer" --skill production-frontend-engineer --dest "$HOME/.agents/skills"
```

Already installed? The installer skips existing copies unless `--update` is supplied. Back up the existing folder outside discovery before an upgrade:

```sh
mv ~/.agents/skills/production-frontend-engineer ~/.agents/production-frontend-engineer-backup-$(date +%Y%m%d-%H%M%S)
bash "$frontend_installer" --skill production-frontend-engineer --dest "$HOME/.agents/skills"
```

Alternatively, use `--update` after making your own backup; the installer's temporary replacement copy is not a retained backup. It checks the download before replacement. It does not disable plugin copies or change other skills. The script may change over time; Frontend's archive is pinned to the named release tag, not repository main.

After installation, ask the agent to confirm the loaded skill names, versions from metadata/release.json, and matching SKILL.md hashes before starting work.

## Distribution

Stable versions: Steward 2.1.3 for Codex and separately authorized Claude Code; standalone Director 1.3.2; standalone Engineer 1.3.2. Native claude.ai validation of Steward 2.1.3 is not yet established; Steward 2.1.2 retains its historical validation scope. Each individual ZIP contains one named folder with SKILL.md at its root. The optional GTM Product Experience plugin still packages Director and Engineer at 1.3.1; install Steward separately. If you use standalone Director or Engineer 1.3.2 alongside the plugin in Codex, exclude only the corresponding older plugin skill rather than disabling unrelated roles. The installer does not manage those settings.

Do not upload the plugin archive as an individual Claude skill. Uploading an archive into a chat does not install it.

The plugin folder is a distribution snapshot of the canonical GTM product-experience authoring source, not a second independent authoring location. Steward remains in its existing repository to avoid a competing source copy. Adding the explicit Frontend installer option does not update the plugin snapshot.

## Evaluation and limits

Bounded evaluation of unchanged candidate instructions: Codex local build with 10 local and 15 browser checks; Claude Cowork build with 19 passing checks and native browser zoom not run after application fixes; fresh-session continuity with 7 focused passes and a 19-pass suite rerun. Saved evidence and selected cases independently inspected. One prompted project, no controlled baseline or proof of automatic routing. Screen-reader behavior and other browser engines untested. Claude after-work skill hashes were not retained. Validation applies to the unchanged candidate instruction payload.

Historical Steward evaluations retain their original version scope. The saved app test results demonstrate the tested scenarios, not absence of defects or universal skill reliability. The paragraph above is historical collection evidence, not certification of Frontend 1.3.2. See the [Frontend 1.3.2 bounded evidence](https://github.com/glichtenthal/agent-skills/blob/production-frontend-engineer-v1.3.2/release-preparation/frontend-1.3.2/EVIDENCE.md) for its scope and retained limitations.

Download [Director 1.3.2](https://github.com/glichtenthal/agent-skills/releases/tag/product-design-director-v1.3.2), [Engineer 1.3.2](https://github.com/glichtenthal/agent-skills/releases/tag/production-frontend-engineer-v1.3.2), the [optional 1.3.1 plugin](https://github.com/glichtenthal/agent-skills/releases/tag/product-experience-v1.3.1), and Steward 2.1.3 for [Codex](https://github.com/glichtenthal/ai-project-steward/releases/tag/v2.1.3) or [Claude Code](https://github.com/glichtenthal/ai-project-steward/releases/tag/v2.1.3-claude).

# Product development skills

Use any of these three skills independently, or combine them for product work. [Explore the visual overview](https://glichtenthal.github.io/agent-skills/product-development/).

| Skill | Responsibility | Distribution |
| --- | --- | --- |
| AI Project Steward | Project decisions, approval boundaries, continuity, completion | [Canonical repository](https://github.com/glichtenthal/ai-project-steward) |
| Product Design Director | Product definition, interaction and visual design, rendered critique | [Skill folder](gtm-product-experience/skills/product-design-director/) |
| Production Frontend Engineer | Implementation, visual fidelity, technical verification | [Skill folder](gtm-product-experience/skills/production-frontend-engineer/) |

Install all three for the combined workflow; invoke the roles relevant to each task. A narrow frontend fix does not require a new design cycle. Design Craft is not a separate dependency.

## Install

Download the three individual skill ZIPs:

- [AI Project Steward 2.1.3 (Codex only)](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.3/ai-project-steward-2.1.3-codex.zip)
- [Product Design Director 1.3.2](https://github.com/glichtenthal/agent-skills/releases/download/product-design-director-v1.3.2/product-design-director-1.3.2.zip)
- [Production Frontend Engineer 1.3.1](https://github.com/glichtenthal/agent-skills/releases/download/product-experience-v1.3.1/production-frontend-engineer-1.3.1.zip)

**Claude:** Steward 2.1.3 is a Codex-only release, not a certified Claude upgrade. For Claude, retain the [Steward 2.1.2 stable ZIP](https://github.com/glichtenthal/ai-project-steward/releases/download/v2.1.2/ai-project-steward-2.1.2.zip). For other supported skill ZIPs, upload through your account's Skills settings, enable them, and start a fresh chat. Chat attachments alone do not install skills. Replace older copies of the same supported skill; no separate Design Craft installation is needed.

**Codex:** Use your skill installer with the linked skill folders above and Steward's canonical repository. The catalog shell installer supports Steward separately, but does not install Director or Engineer. If you use the optional GTM Product Experience plugin, it supplies Director and Engineer; install Steward separately and avoid duplicate standalone copies of the same roles.

After installation, ask the agent to confirm the loaded skill names, versions from metadata/release.json, and matching SKILL.md hashes before starting work.

## Distribution

Stable versions: Steward 2.1.3 (Codex only; 2.1.2 remains the published Claude-tested version); standalone Director 1.3.2; Engineer 1.3.1. Each individual ZIP contains one named folder with SKILL.md at its root. The optional GTM Product Experience plugin still packages Director and Engineer at 1.3.1; install Steward separately. If you use standalone Director 1.3.2 alongside the plugin in Codex, exclude the plugin's older Design copy without disabling Frontend Engineer.

Do not upload the plugin archive as an individual Claude skill. Uploading an archive into a chat does not install it.

The plugin folder is a distribution snapshot of the canonical GTM product-experience authoring source, not a second independent authoring location. Steward remains in its existing repository to avoid a competing source copy. The existing catalog installer is unchanged.

## Evaluation and limits

Bounded evaluation of unchanged candidate instructions: Codex local build with 10 local and 15 browser checks; Claude Cowork build with 19 passing checks and native browser zoom not run after application fixes; fresh-session continuity with 7 focused passes and a 19-pass suite rerun. Saved evidence and selected cases independently inspected. One prompted project, no controlled baseline or proof of automatic routing. Screen-reader behavior and other browser engines untested. Claude after-work skill hashes were not retained. Validation applies to the unchanged candidate instruction payload.

Historical Steward evaluations retain their original version scope. The saved app test results demonstrate the tested scenarios, not absence of defects or universal skill reliability.

Download [Director 1.3.2](https://github.com/glichtenthal/agent-skills/releases/tag/product-design-director-v1.3.2), [Engineer 1.3.1 and the optional 1.3.1 plugin](https://github.com/glichtenthal/agent-skills/releases/tag/product-experience-v1.3.1), and [Steward 2.1.3 (Codex only)](https://github.com/glichtenthal/ai-project-steward/releases/tag/v2.1.3).

> **Unreleased learning candidate 1.3.2-rc.1.** Published stable 1.3.1 remains unchanged. Targeted advisory results are in the [shared Steward pilot](https://github.com/glichtenthal/ai-project-steward/blob/feat/evidence-driven-learning-20261025/learning/results/pilot-2026-10-31/README.md). Full release gates remain blocked; no install or release is approved.

# GTM Product Experience

This plugin bundles the paired Product Design Director and Production Frontend Engineer skills, including their required experience-specification and release-readiness references.

## Included Skills

- Product Design Director: define the product experience and useful scope, own interaction and detailed visual design, produce the approved specification, and critique the rendered implementation.
- Production Frontend Engineer: implement the approved experience, check visual fidelity and technical behavior, resolve design-review findings, and document the evidence without hiding release risk.

Visual-design guidance lives in Product Design Director's `references/visual-design.md`; no standalone Design Craft skill is required. For substantial visual work, design, implementation, rendered design review, and correction form one bounded workflow. Scoped fixes use proportionate checks. AI Project Steward can coordinate the overall project when installed separately; it is not bundled in this plugin.

## Source Of Truth

Edit the skills and references in this plugin directory. Reinstall or upgrade the plugin after a change, then start a new Codex or ChatGPT task so the updated skills are loaded.

The standalone copies under ~/.codex/skills are retained for current local Codex use. They are not the distribution source for ChatGPT.

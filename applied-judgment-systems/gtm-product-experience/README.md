> **Unreleased Design-only integration candidate.** Collection 1.3.2-rc.2 contains the validated Design Director 1.3.2-rc.1 payload and unchanged stable Frontend Engineer 1.3.1. The distinct collection identifier avoids collision with the mixed experimental 1.3.2-rc.1 branch. Published stable 1.3.1 assets remain untouched; no release or installation is approved. See [Design-only review](RELEASE_REVIEW.md).

# GTM Product Experience

This plugin bundles the paired Product Design Director and Production Frontend Engineer skills, including their required experience-specification and release-readiness references.

## Included Skills

- Product Design Director: define the product experience and useful scope, own interaction and detailed visual design, produce the approved specification, and critique the rendered implementation.
- Production Frontend Engineer: implement the approved experience, check visual fidelity and technical behavior, resolve design-review findings, and document the evidence without hiding release risk.

Visual-design guidance lives in Product Design Director's `references/visual-design.md`; no standalone Design Craft skill is required. For substantial visual work, design, implementation, rendered design review, and correction form one bounded workflow. Scoped fixes use proportionate checks. AI Project Steward can coordinate the overall project when installed separately; it is not bundled in this plugin.

## Source Of Truth

Edit the skills and references in this plugin directory. Reinstall or upgrade the plugin after a change, then start a new Codex or ChatGPT task so the updated skills are loaded.

The standalone copies under ~/.codex/skills are retained for current local Codex use. They are not the distribution source for ChatGPT.

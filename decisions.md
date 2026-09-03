# Decisions

## 2026-09-02 — Shared visual layer for Judgment Infrastructure pages

- **Status:** Accepted
- **Context:** The catalog, four portable-skill pages, guided workflow, demo, manifesto, and use-case pages had separate legacy visual treatments. AI Project Steward established the approved current direction: warm porcelain surfaces, blue hierarchy, forest-green actions, restrained cards, visible focus, and reduced motion.
- **Options considered:** Restyle each page independently; adopt one shared stylesheet while preserving local content and layout rules; replace the static pages with a new application framework.
- **Decision:** Add `assets/judgment-infrastructure.css` as a shared visual layer across all Judgment Infrastructure content pages. Preserve each portable skill's existing symbol and page-specific content, while aligning typography, color roles, action states, surfaces, focus behavior, and motion preferences to AI Project Steward.
- **Rationale:** A shared layer delivers a coherent system with the fewest moving parts and prevents page-by-page palette drift without introducing a new runtime or framework.
- **Consequences and trade-offs:** System-wide refinements are now centralized. Pages retain their local layout rules, so a deliberately different future direction can be added with a local override; those overrides should be intentional and documented.
- **Reconsider when:** The catalog moves to a component-based site, a portable skill needs a materially different visual identity, or repeated local overrides make the shared layer harder to maintain than a full design-system migration.

## 2026-09-03 — Open typography and a framed catalog-card system

- **Status:** Accepted
- **Context:** The catalog’s Avenir Next headings felt visually compact, and only AI Project Steward used the current framed-card language with skill-specific color fields. The catalog also presented compatibility labels inconsistently.
- **Options considered:** Keep Avenir and independent card treatments; use a system-font stack with no guaranteed new typeface; load Instrument Sans with local fallbacks and apply one CSS-based card frame that preserves every existing skill symbol and its color family.
- **Decision:** Use Instrument Sans from Google Fonts with Avenir/system fallbacks across the content pages, make the catalog a slightly cooler system-overview surface, and apply a shared framed-card treatment with two restrained color fields to every catalog skill card. Use a single clear compatibility label on each portable skill: Claude + Codex for the four core skills, and the tested broader footprint for AI Project Steward.
- **Rationale:** Instrument Sans opens up the display typography without becoming decorative. The shared CSS treatment improves cohesion while avoiding asset rewrites or a component-framework migration. The hosted font gives dependable visual consistency for the lightweight static site.
- **Consequences and trade-offs:** Visitors make a request to Google Fonts; no credentials or catalog content are sent, but self-hosting would be preferable if third-party font requests become unacceptable. Global card refinements remain easy to maintain in one stylesheet. The detailed skill pages remain warm porcelain, while the hub can be recognized as the system overview.
- **Reconsider when:** The catalog adopts self-hosted assets or a stricter privacy posture, a visual identity needs a different card structure, or measured performance shows the font request is not justified.

## 2026-09-03 — Preview-scoped card framing correction

- **Status:** Superseded
- **Context:** The first shared-frame implementation styled the whole catalog article as well as the preview image. On AI Project Steward, whose SVG already contains its own color canvas and inner rectangle, this created an unintended third frame.
- **Options considered:** Keep the article-level frame; remove all shared framing; scope the shared color canvas and inner border to a preview wrapper for the four core cards while leaving AI Project Steward untouched.
- **Decision:** The catalog article remains a neutral container. The Briefing Room, Ground Truth, The Quorum, and Test Drive each receive a `.skill-preview` canvas with two color fields and one inner framed preview. AI Project Steward retains its original self-contained SVG treatment without an additional wrapper.
- **Rationale:** This matches the approved visual reference’s two-layer composition and preserves AI Project Steward exactly as the reference rather than layering an implementation artifact around it.
- **Consequences and trade-offs:** The frame is now correctly isolated and easier to reason about. Four small HTML wrappers are more explicit than a one-selector shortcut, but prevent the reference card from being inadvertently restyled.
- **Reconsider when:** The catalog moves to reusable components or a portable skill needs a different preview structure.

## 2026-09-03 — SVG-owned two-layer preview geometry

- **Status:** Accepted
- **Context:** The CSS preview-wrapper correction still left each legacy core SVG’s original full-card border inside the new inner border. Test Drive exposed the result clearly: three visible nested borders instead of the two-layer AI Project Steward reference.
- **Options considered:** Continue adding CSS exceptions around legacy SVGs; simplify the previews by removing their diagrams; rebuild the four core SVG previews around AI Project Steward’s established outer-canvas and inner-panel geometry while preserving each skill’s existing diagram or symbol.
- **Decision:** Rebuild the four core social-preview SVGs as 1200 × 630 two-layer previews. Each uses its own palette for the canvas and two color fields, plus the same inner-panel rectangle as AI Project Steward: `x=64`, `y=54`, `width=1072`, `height=522`, and `rx=32`. Remove all external preview-frame CSS and wrappers.
- **Rationale:** The frame is now part of the artwork, where its geometry can be exact. Each card has one outer canvas and one inner panel—no third visual boundary—while its distinctive diagnostic diagram remains intact.
- **Consequences and trade-offs:** The SVG previews are more deliberately designed and consistent, but future visual changes to the frame require updating the shared SVG template rather than one CSS rule. The catalog markup is simpler.
- **Reconsider when:** A component or asset pipeline can generate these previews from a shared source, or a future portable skill requires a fundamentally different visual identity.

## 2026-09-03 — Public catalog release scope

- **Status:** Accepted
- **Context:** The current catalog update includes the approved site refresh, AI Project Steward page-flow revision, supporting design specification and QA record, plus two unlinked local comparison pages used to choose fonts and background treatments.
- **Options considered:** Publish every local artifact; publish only the visitor-facing catalog and its supporting records; discard the comparison pages.
- **Decision:** Publish the visitor-facing catalog, shared stylesheet, preview assets, product specification, QA record, and this decision record. Keep `ai-project-steward/font-comparison.html` and `ai-project-steward/background-comparison.html` local and untracked.
- **Rationale:** The public release should reflect the approved experience and its evidence without exposing internal selection work as accidental product pages.
- **Consequences and trade-offs:** The public repository stays focused and the design-review artifacts remain available locally. Sharing those comparisons later requires an explicit decision to package or publish them.
- **Reconsider when:** A deliberate public design-process archive, case study, or contributor workflow calls for those comparison pages.

---
schema_version: "1.0"
artifact: experience_specification
status: verified
mode: design_to_build
owner: product-design-director
updated: 2026-09-03
visual_target: "AI Project Steward card treatment and approved warm-porcelain / blue / forest-green system"
implementation_ref: "assets/judgment-infrastructure.css; index.html; assets/*-social-preview.svg; ai-project-steward/index.html"
verification_ref: "judgment-infrastructure-qa.md"
direction_id: "framed-portable-skills-catalog"
selection_evidence: "User feedback and supplied screenshots, 2026-09-03"
approval_evidence: "User requested the shared frame, fresher typography, and compatibility labels, 2026-09-03"
target_routes:
  - "/"
  - "/briefing-room/"
  - "/ground-truth/"
  - "/the-quorum/"
  - "/test-drive/"
  - "/ai-project-steward/"
target_states:
  - "populated"
target_viewports:
  - "390x844"
  - "1280x800"
implementation_contract_version: "1.0"
---

# Judgment Infrastructure Catalog Refresh

## Product Intent

- **Surface:** A static catalog and supporting content pages for portable AI skills.
- **Primary user and job:** A prospective installer needs to understand what each skill does, whether it works in their environment, and where to learn or install it.
- **Core workflow:** Open catalog → identify a skill → confirm compatibility → learn or review the release.
- **Hard constraints:** Preserve existing skill symbols and links; avoid a new runtime; do not deploy without explicit approval.
- **Non-goals:** Redesigning individual skill content, changing the packages, or making unsupported compatibility claims.

## Evidence

| Evidence | Source | Strength | Design consequence |
| --- | --- | --- | --- |
| AI Project Steward’s framed card with two restrained color fields is preferred | User-supplied catalog screenshot | Direct | Apply its structural language to all catalog skill cards, preserving each symbol and color family. |
| The Briefing Room heading feels compact | User-supplied screenshot | Direct | Replace Avenir Next as the primary display font with Instrument Sans and retain fallbacks. |
| Compatibility is useful but inconsistent | User feedback and current card markup | Direct | State supported platforms in a single visible tag per card. |

## Experience Architecture

- The hub remains the system overview and uses a subtle cool-mist canvas; detail pages use warm porcelain.
- Each card keeps a consistent sequence: recognizable mark, compatibility/context tags, skill name, concise benefit, then learn/release/repository actions.
- AI Project Steward leads with its promise, then immediately explains its role as a human-led operating layer in an AI build harness before presenting evaluation coverage, operating flow, collaboration difference, evidence, and installation.
- Visual decoration stays behind content and never competes with the title or action path.

## State Model

- **Default/populated:** Static content and release links render directly.
- **Unavailable external release:** The browser’s standard link failure is the current behavior; no synthetic status is presented.
- **No data states:** Not applicable; the catalog has no live application data.

## Visual System

- **Typography:** Instrument Sans with Avenir/system fallbacks; display headings use a 600 weight and restrained negative tracking (`-.015em` for `h1`, `-.01em` for `h2`) so the hierarchy feels open rather than compressed. All ordinary underlined links use dark green, a 600 weight, normal tracking, a 1.25px underline, and a 3px offset; buttons, breadcrumbs, and non-underlined card containers retain their own affordances. Judgment Loop step labels remain dark ink; their supporting lines are ordinary muted copy, never filled badges.
- **Color:** Vivid blue for major hierarchy, forest green for primary actions and utility emphasis, warm porcelain detail surfaces, cool-mist hub canvas.
- **Cards:** Every skill preview owns the same 1200 × 630 two-layer composition: an outer color canvas with top-right and lower-left fields, then an inner framed panel at `x=64`, `y=54`, `width=1072`, `height=522`, and `rx=32`. AI Project Steward retains its existing SVG; the four core preview SVGs now use the same geometry.
- **Symbols:** Existing skill-specific diagrams and symbols are retained inside the rebuilt SVG previews.
- **Spacing:** Standard content sections retain a compact 18–34px rhythm. The catalog’s Applied Judgment Systems transition uses a distinct but restrained 48px divider gap with a 30px content inset. All five skill detail pages share the same breadcrumb offset, hero padding, 18px internal rhythm, and title scale; pages may grow vertically only for their genuinely different supporting copy and actions. AI Project Steward places its richer, two-column operating-layer explanation 26–40px below the hero, then moves to evaluation coverage; narrative section transitions remain 80px on desktop and 56px on mobile.
- **Responsive behavior:** Cards remain two columns at desktop and stack at narrow mobile widths; no horizontal scroll.
- **Accessibility:** Native headings and links remain semantic; blue focus indicators and reduced-motion rules are retained.

## Data And Trust

- Compatibility labels mirror the existing published package metadata: Claude + Codex for the four core skills; Claude, ChatGPT, Codex, and Replit for AI Project Steward.
- Font delivery uses Google Fonts and therefore makes one third-party font request. It does not transmit credentials or catalog data.
- No secrets, external actions, or live user data are present in the catalog.

## Decision Record

| Decision | Evidence | Alternatives rejected | Consequence |
| --- | --- | --- | --- |
| Instrument Sans as primary typeface | Direct visual feedback | Retain Avenir; system-only stack; self-hosted font package | More open hierarchy; third-party font request while hosted. |
| SVG-owned preview framing | AI Project Steward card reference and user correction | External CSS wrappers; frame the entire article | Every preview has the same two layers without an accidental third border. |
| Visible compatibility tags | User feedback | Remove platform information | Faster installability scan without changing package claims. |

## Open Questions And Risks

- Confirm the cool-mist hub canvas in browser review before public deployment.
- If privacy policy requires no third-party font requests, self-host Instrument Sans before publishing.
- The static site has no custom unavailable-link state; release availability remains governed by GitHub.

## Acceptance Criteria

- Every catalog card retains its skill-specific diagram or symbol. All five previews use the same outer-canvas and inner-panel geometry, with no CSS wrapper or duplicate card border.
- Every catalog card visibly states compatibility without reintroducing redundant platform pills.
- The five skill detail-page titles render at the same responsive scale, weight, tracking, and hero spacing. Test Drive has no one-off platform label in its hero.
- AI Project Steward presents its human-led operating-layer explanation, including the AI build harness context and the boundaries of what it does not replace, before its evaluation coverage.
- The hub and AI Project Steward product page use Instrument Sans when available and readable fallbacks otherwise.
- Desktop at 1280px and mobile at 390px render without clipping or horizontal overflow.
- Keyboard focus remains visible and primary links remain reachable in DOM order.
- No new browser errors are introduced; release links stay unchanged except AI Project Steward’s label matches its review destination.

## Status Transitions

- **selected:** User supplied the AI Project Steward visual target and requested the shared frame and type update.
- **approved:** The target routes, visual direction, compatibility rules, and acceptance criteria are recorded above.
- **implemented:** The framing system moved from external CSS wrappers into the four core SVG preview assets.
- **verified:** Local browser review confirmed all five preview assets are 1200 × 630, the four core cards load the new versioned SVGs, no `.skill-preview` wrappers or CSS image borders remain, and the catalog has no horizontal overflow at 1280 × 720 or 390 × 844.

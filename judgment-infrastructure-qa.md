# Judgment Infrastructure Visual Update — QA

- **Status:** Verified for local review; not deployed
- **Reference direction:** AI Project Steward catalog page
- **Target flow:** Catalog → guided workflow, portable skill, or use case → readable judgment guidance
- **Reviewed surface:** 15 routable Judgment Infrastructure paths, including AI Project Steward and the legacy redirect; the two private design-comparison pages were also checked for layout overflow
- **Viewports:** 1280 × 800 desktop and 390 × 844 mobile
- **Browser evidence:** Rendered in the local browser preview during this review. Desktop screenshots were inspected for the catalog cards and AI Project Steward hero; mobile screenshot was inspected for the catalog hierarchy. Screenshots were reviewed in-session and are not stored as project assets.

## Verified

- The shared `assets/judgment-infrastructure.css` stylesheet loads on every in-scope page.
- A full spacing audit found that the standard content pages already use a compact 18–34px section rhythm. The catalog’s Applied Judgment Systems transition was reduced from a 72px divider gap plus 42px inset to 48px plus 30px. AI Project Steward’s desktop narrative transitions were reduced from 128px to 80px, and its mobile transitions from 72px to 56px, without flattening the hero hierarchy.
- The Judgment Loop’s five supporting lines render as muted, readable explanatory copy with transparent backgrounds; no reverse-white text or filled highlight remains. This was checked at desktop and 390 × 844 mobile with no horizontal overflow.
- Detail-page display headings use Instrument Sans at a calmer 600 weight with restrained tracking; The Briefing Room was reviewed at 1280 × 720 and 390 × 844 with no horizontal overflow.
- Catalog inline actions such as **Open use case** use Instrument Sans at 600 weight, normal tracking, and a readable 1.25px underline. They were reviewed at 1280 × 720 and 390 × 844 with no horizontal overflow or browser console messages.
- The four linked Use Cases card titles use a 600 weight, normal tracking, and a 1.25px underline rather than the earlier compressed 850-weight treatment. They were reviewed at 1280 × 800 and 390 × 844 with no horizontal overflow or browser console messages.
- All 46 ordinary underlined links across the 15 routable product paths use dark green, a 600 weight, normal tracking, a 1.25px underline, and a 3px offset. Buttons, breadcrumbs, and non-underlined card containers remain distinct. Desktop and mobile review found no exceptions, no horizontal overflow, and no browser console messages; keyboard focus remains a visible 3px outline.
- The Demo page’s dark Scenario panel uses a warm-white heading rather than the global blue display color. Its rendered mobile contrast ratio is 8.66:1, with no horizontal overflow or browser console messages at 390 × 844 or 1280 × 800.
- The visual system uses Instrument Sans with local fallbacks, vivid blue hierarchy, forest-green primary actions, restrained borders, visible keyboard focus, and reduced-motion support.
- The catalog uses a slightly cooler overview canvas; content pages remain warm porcelain for readable, focused detail work.
- The Briefing Room, Ground Truth, The Quorum, and Test Drive retain their existing skill-specific diagrams and symbols inside rebuilt social previews. Each now has the same 1200 × 630 outer canvas and `x=64`, `y=54`, `1072 × 522`, `rx=32` inner panel as AI Project Steward, with its own palette and two color fields.
- AI Project Steward has no added preview wrapper, CSS image border, or extra padding. Its original self-contained canvas and inner rectangle remain exactly the reference treatment.
- Compatibility is stated consistently on every catalog card: Claude + Codex for the four core skills and the broader tested installation footprint for AI Project Steward.
- AI Project Steward’s public compatibility claim is limited to Claude, ChatGPT, Codex, and Replit in both its visible catalog tag and page metadata; Town is not listed.
- The catalog, guided workflow, portable-skill page, and detailed use-case page render without horizontal overflow at 390px.
- The refreshed catalog renders without horizontal overflow at 1280 × 800 and 390 × 844. All five catalog cards fit within their containers at both reviewed sizes.
- The AI Project Steward detail page and The Briefing Room detail page render without desktop horizontal overflow; Instrument Sans is loaded and active after font readiness on both pages.
- The five skill detail pages share one hero title system: 61.44px at 1280px and 33.6px at 390px, 600 weight, `-.015em` tracking, and 58px/54px desktop or 28px/30px mobile hero padding. AI Project Steward retains its additional explanation and actions without a larger title. Test Drive’s one-off top-level “Claude + Codex agent skill” label was removed; its existing compatibility wording inside the illustrative preview remains unchanged.
- AI Project Steward now places its richer operating-layer explanation directly after the hero and before evaluation coverage. The panel uses the eyebrow **Where it fits in an AI build harness** and the accessible heading **A human-led operating layer for AI-assisted builds.** It renders at 592px on desktop and 544px on mobile, with no horizontal overflow or console messages.
- The catalog’s primary path was exercised: **Start here** opens `/start-here/` and reaches the heading **Start with the work you have.**
- Keyboard navigation reaches the primary **Start here** action and exposes the page’s `:focus-visible` state. The in-app preview reports the browser’s focus rendering rather than a computed custom outline; the explicit focus rule remains in the shared stylesheet.
- Browser console review found no warnings or errors on the catalog, AI Project Steward, or the primary catalog-flow page.
- The correction renders without horizontal overflow at 1280 × 720 and 390 × 844. At mobile width, all five cards are 362px wide and their contained previews have no overflow.
- The four core cards load versioned 1200 × 630 SVG assets; AI Project Steward continues to load its existing 1200 × 630 reference SVG. No catalog card uses a `.skill-preview` wrapper, CSS image border, or CSS image radius.
- All 14 routes have a primary heading. Static checks confirmed the shared stylesheet links, markup changes have no whitespace errors, and no portable-skill symbol assets were changed.
- Static checks confirmed the shared stylesheet links and no accidental changes to portable-skill symbol assets.

## Intentional scope

- Content and installation behavior for the existing portable skills remain intact.
- AI Project Steward remains the visual and methodological reference page; its typography now uses the shared Instrument Sans direction.
- Social preview geometry was rebuilt in this pass; the existing portable-skill diagrams and symbols were preserved inside the new two-layer composition.

## Remaining review item

- Confirm the cool-mist hub canvas and Google-hosted font request in local review before public deployment. No deployment action has been taken in this update.

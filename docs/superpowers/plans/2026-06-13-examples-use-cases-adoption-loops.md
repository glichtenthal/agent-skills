# Examples Use Cases Adoption Loops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the judgment infrastructure skill bundle easier for strangers to understand, try, and adopt.

**Architecture:** Add one quick-demo example to each skill repo, then create a catalog-level start workflow that ties the four skills into one repeatable path. Update README/profile entry points so users can move from discovery to first use in under three minutes.

**Tech Stack:** Markdown documentation, static HTML/CSS, existing GitHub Pages catalog, existing `.skill` repo structure.

---

### Task 1: Add Quick Demos To Skill Repos

**Files:**
- Create: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/briefing-room/examples/quick-demo.md`
- Create: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/ground-truth/examples/quick-demo.md`
- Create: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/the-quorum/examples/quick-demo.md`
- Create: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/test-drive/examples/quick-demo.md`
- Modify: each skill repo `README.md`

- [ ] **Step 1: Create each examples directory if needed**

Run:
```bash
mkdir -p briefing-room/examples ground-truth/examples the-quorum/examples test-drive/examples
```
Expected: directories exist.

- [ ] **Step 2: Add one quick demo per skill**

Each demo must include: messy/realistic input, copy-paste prompt, representative output shape, why it matters, and next skill path.

- [ ] **Step 3: Link demos from each README**

Add a compact `Try It In Three Minutes` section after install or good-first-use sections.

### Task 2: Add Catalog Start Workflow

**Files:**
- Create: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/agent-skills/start-here/index.html`
- Create: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/agent-skills/examples/judgment-infrastructure-demo.md`
- Modify: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/agent-skills/index.html`
- Modify: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/agent-skills/README.md`
- Modify: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/agent-skills/sitemap.xml`

- [ ] **Step 1: Create start page**

The page should explain: pick a starting mess, run Briefing Room, pressure-test with Ground Truth, use Quorum for consequential choices, use Test Drive for evidence before commitment.

- [ ] **Step 2: Add flagship demo**

The demo should show one scenario moving through all four skills with copy-paste prompts.

- [ ] **Step 3: Add entry links to catalog homepage and README**

The homepage should include `Start here` and `See a full demo` calls to action.

### Task 3: Update Profile Adoption Loop

**Files:**
- Modify: `/Users/glichtenthal/Documents/New project/skill-polish-publish-ready/profile/README.md`

- [ ] **Step 1: Add a quick start workflow**

Make the profile route users to the catalog start page, flagship demo, and first skill to try.

### Task 4: Validate And Publish

**Files:** all modified repos.

- [ ] **Step 1: Validate links and JSON-LD**

Run the existing HTML parser validation against catalog pages and confirm new local images/pages exist.

- [ ] **Step 2: Commit and push each repo**

Use concise commits by repo.

# Experience Specification Template

Keep this file unchanged. Copy its structure into a project-owned artifact, preferably `docs/product/experience-spec.md`, when a durable handoff is useful.

```yaml
schema_version: "1.0"
artifact: experience_specification
status: draft # draft | selected | approved | implemented | verified
design_mode: audit # audit | concept | design_to_build | narrow_fix
owner: product-design-director
updated: YYYY-MM-DD
visual_target: null
implementation_ref: null
verification_ref: null

# Handoff contract.
# Required for broad visual work. Omit for a scoped fix inside an established design system.
implementation_contract_version: "1.0"
direction_id: null            # stable identifier, set at `selected`, never reused
selection_evidence: null      # required at `selected`
approval_evidence: null       # required at `approved`
target_routes: []             # required at `approved`
target_states: []             # required at `approved`
target_viewports: []          # required at `approved`
acceptance_criteria_ref: null # anchor or path to the criteria, required at `approved`
```

The fence above marks this as an example inside a reference file. In a project-owned specification
this metadata is frontmatter: place it at the very top of the document, before any heading, opened
and closed by a line containing only three hyphens, with no code fence around it. A fenced block in
a project specification is prose. The engineer reads frontmatter and will treat a fenced block as
an absent contract.

## Product Intent

- Product and surface
- Primary user and job
- Business outcome
- Core workflow
- Hard constraints and non-goals
- For new products or material workflow changes: current task or workaround, smallest useful end-to-end scope, and deferred work
- Intended user-success signal and known baseline, separate from implementation acceptance; label unknowns instead of inventing metrics

## Evidence

| Evidence | Source | Strength | Design consequence |
| --- | --- | --- | --- |

Name missing evidence and untested assumptions. Rank observed behavior and validated user needs above visual preference.

## Experience Architecture

- Navigation and page hierarchy
- First-viewport priority
- Primary and supporting actions
- Workflow steps and decision points
- Progressive disclosure and inspector/modal behavior
- Interface terminology, instructions, and consequential messages, including realistic content-length and localization needs when relevant

## State Model

- Default and populated
- Loading and refreshing
- Empty and partial data
- Stale or conflicting data
- Blocked and permission denied
- Validation and system error
- Success and confirmation
- Destructive action and recovery

## Visual System

- Approved visual target or selected concept
- Typography and spacing
- Color roles and contrast constraints
- Surface, border, radius, and elevation rules
- Icon and control treatment
- Motion and feedback
- Desktop, tablet, and mobile behavior

## Data And Trust

- Real data sources and contracts
- Demo, fixture, fallback, and live-data boundaries
- Provenance and freshness indicators
- Inference, draft, approval, and publication boundaries
- Unsupported-claim and missing-source handling

## Decision Record

Keep detailed design rationale here. Link shared material choices and their approval to the authoritative entry in `decisions.md` when present; do not maintain a second editable copy of the same decision. An approval reference must identify an actual applicable approval, not merely a proposed decision.

| Decision | Evidence | Alternatives rejected | Consequence |
| --- | --- | --- | --- |

## Open Questions And Risks

- Unresolved product decisions
- Research gaps
- Technical or data dependencies
- Accessibility risks requiring non-visual testing

## Acceptance Criteria

Write observable criteria for hierarchy, workflows, states, responsiveness, accessibility checks, data fidelity, and visual fidelity. Include the target viewport sizes and critical interactions that browser testing must exercise.

Set `acceptance_criteria_ref` in the frontmatter to this section's anchor, or to the path where the
criteria live if they are held elsewhere.

## Design Review And Learning

For substantial visual work, link the rendered design review in the existing mismatch ledger or release record. Identify reviewed routes, states, and viewports; material design findings and their disposition; and any unavailable checks. Routine corrections within the approved direction do not require a new approval. A scoped fix does not need a separate design-review round by default.

Record the most important untested product assumption and the smallest useful way to validate it when relevant. Keep intended outcomes separate from demonstrated results. Design and technical verification do not establish adoption, usability with real users, or business impact. Revisit the assumption when authorized feedback becomes available; do not add research or instrumentation automatically.

## Status Transitions

- `draft`: Intent, evidence, architecture, states, and acceptance criteria are recorded.
- `selected`: The user selected the visual direction; link the accepted target.
- `approved`: The implementation contract is complete and approved.
- `implemented`: The frontend engineer links the implementation and mismatch ledger.
- `verified`: The frontend engineer links passing release evidence and remaining risk, including rendered design-review findings and their resolution for substantial visual work.

Broad visual work cannot reach `approved` while any handoff contract field is still null or empty.

Advance through the applicable stages only when supporting evidence exists; do not require separate user turns for transitions supported by the same applicable approval. An `implemented` or `verified` specification can be resumed without renewing unchanged approval.

Identify the scope and implementation revision supported by linked evidence. For changes within the approved direction, preserve approval and reassess affected verification evidence; do not leave stale evidence presented as current. For material direction changes, return to `draft` or `selected`, explain why, preserve superseded evidence in the history, and clear current approval and verification references that no longer apply.

If the user explicitly directs a build without recorded approval under the engineer’s existing exception, retain the unapproved status and absent approval evidence. Link implementation and test results in a separate project-owned record; these results do not advance this contract to `implemented` or `verified`.

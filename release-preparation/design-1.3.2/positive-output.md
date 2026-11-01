I’ll use the product-design-director skill to structure the approach, specification, and decisions needed before engineering starts. I’ll read only within the temporary work directory and won’t implement anything or access external sources.

The dashboard should help a clinic receptionist answer three questions quickly: **Who is due next, what needs attention, and where can an appointment be booked?**

This is a **concept-stage plan**, with no direction selected or approval recorded. All examples below are fictional. I read only the design skill and its references within the temporary work directory; no files were changed, external sources accessed, or implementation performed.

**Product approach**

Assume a small clinic with one reception team and several practitioners. The smallest useful scope is viewing the day, finding an appointment, booking, rescheduling, cancelling, and recording arrival status.

A representative workflow is: select date → find patient or appointment → inspect availability → enter or change details → review → save → see the confirmed result in the schedule.

Defer billing, clinical records, patient messaging, inventory, and predictive analytics. These expand the product beyond appointment management.

The intended outcome is fewer scheduling mistakes and less effort coordinating arrivals. There is no observed workflow, baseline, or user research yet. The key assumption is that reception primarily works from the current day’s schedule. A future, separately authorized walkthrough using fictional booking and conflict scenarios would test that assumption.

**Three directions to select from**

These are textual concepts, not approved visual targets.

| Direction | Navigation and first viewport | Representative workflow | Strengths and tradeoffs |
|---|---|---|---|
| **A. Daily agenda — recommended** | Date navigation, practitioner filters, chronological appointment table, persistent “Book appointment” action; details open beside the list. | Find a time → inspect appointment or availability → edit in a detail panel. | Supports scanning and arrival management; simultaneous availability across practitioners is less visible. |
| **B. Practitioner schedule** | Day/week navigation and practitioner columns with time slots; booking begins by selecting a slot. | Choose practitioner and time → enter details → review and save. | Makes gaps and overlaps visible; dense calendars need an alternative list view on small screens. |
| **C. Reception queue** | Workflow navigation: Expected, Arrived, In progress, Completed; appointment details occupy a separate view. | Find expected patient → mark arrived → move through the visit workflow. | Prioritizes patient flow; advance booking needs a separate schedule surface, and status transitions need careful definition. |

These choices respond to assumed tasks, not research evidence. Direction A is the strongest starting hypothesis because it combines daily coordination and booking with moderate information density.

**What belongs in the experience specification**

Use one project-owned specification, proposed as `docs/product/experience-spec.md`; no file has been created.

| Section | Required content |
|---|---|
| Product intent and evidence | Primary user, job, scope, non-goals, assumptions, missing evidence, intended outcomes, and known or unknown baseline. |
| Architecture | Selected concept, navigation, first-viewport hierarchy, routes, filters, primary actions, details-panel behavior, and return paths. |
| Workflows and content | Booking, rescheduling, cancellation, arrival updates, validation, confirmations, field labels, and recovery instructions. |
| State model | Populated, loading, refreshing, empty, partial, stale, conflict, permission, validation, system error, success, and destructive-action states. |
| Visual system | Annotated visual target, typography, spacing, density, color roles, surfaces, controls, icons, focus, and motion. |
| Data and trust | Fictional fixtures, field meanings, status definitions, clinic timezone, freshness, permissions, and minimum patient disclosure. |
| Responsive and accessible behavior | Layout changes, information priority, keyboard interaction, focus, announcements, zoom, and reduced motion. |
| Decisions and acceptance | Selection and approval evidence, unresolved questions, observable acceptance criteria, target viewports, and later review evidence. |

Example fixture: **Willow Sample Clinic**, Tuesday 9 March 2027; **Jordan Example**, 09:20–09:40, **Dr. Rowan Demo**, “Routine appointment,” status “Confirmed.” Display a persistent **Fictional demo data** label. Omit diagnoses and unnecessary identifiers from the schedule.

For Direction A, prioritize date, filters, schedule, and booking. Use compact operational counts only when actionable—for example, “3 awaiting arrival”—with their scope and calculation defined. Default to chronological sorting; make active filters visible and preserve them when returning from appointment details.

**States and recovery**

| State | Required behavior |
|---|---|
| First-use empty | “No appointments scheduled for this day.” Offer “Book appointment.” |
| Filtered empty | “No appointments match these filters.” Offer “Clear filters”; retain the selected date. |
| Loading or refreshing | Show labelled loading feedback. During refresh, preserve existing rows and entered work. |
| Partial or stale data | Identify unavailable information and last successful refresh. Do not imply missing availability is free time. |
| Booking conflict | Explain that the slot became unavailable, preserve entered details, and offer alternative times. |
| Validation error | Explain the correction beside the field; provide a linked error summary and focus it after submission. |
| Save failure or uncertain outcome | Preserve the draft. If the save outcome is unknown, check status before inviting another submission. |
| Permission denied | Explain the unavailable action and an appropriate next step without exposing restricted details. |
| Cancellation | Show the appointment and consequence before confirmation. Keep cancellation distinct from deleting a record. |
| Success | Announce the confirmed change, update the schedule, and keep the affected appointment easy to locate. |

Status labels and permitted transitions must be explicit. “Cancelled,” “No-show,” and “Completed” must not be interchangeable. Booking duration, overlap policy, and who may override a conflict remain product decisions.

**Responsive behavior and accessibility**

Proposed reference viewports are **1440×900, 1024×768, and 390×844**, with additional checks at 320 CSS pixels and browser zoom.

- **Desktop:** schedule table and adjacent detail panel.
- **Tablet:** fewer visible columns; details move to an overlay with a clear return path.
- **Mobile:** chronological appointment list, full-screen details and booking, and an accessible filter sheet. Keep time, patient name, practitioner, and status visible. Preserve draft values and navigation context across layout changes.

Specify semantic headings, labelled controls, table headers, logical keyboard order, visible focus, and keyboard alternatives to any drag interaction. Dialogs must manage focus and return it to the trigger. Announce save results and relevant status changes without reading the entire schedule again.

Set WCAG 2.2 AA as the implementation target, including measured contrast, adequate target sizes, reflow, and error identification. Pair status colors with text; support reduced motion. Accessibility remains unverified until appropriate rendered, keyboard, and assistive-technology checks occur.

**What must be selected and approved before engineering starts**

Selection establishes the direction; approval establishes that the specification is ready to build. One explicit decision can cover both when the complete artifact is available.

1. **Select a direction or equivalent visual target.** Record a stable direction ID and actual selection evidence.
2. **Resolve material workflow decisions.** Confirm scope, roles, booking rules, timezone, appointment statuses, conflict handling, cancellation consequences, and disclosure rules.
3. **Approve the concrete experience.** Review annotated layouts, critical workflows, state designs, responsive behavior, accessibility requirements, and interface copy.
4. **Complete the implementation contract.** Include contract version `"1.0"`, direction ID, selection evidence, approval evidence, non-empty target routes/states/viewports, and an acceptance-criteria reference.
5. **Confirm feasibility and ownership.** Resolve dependencies that could materially change the approved experience.

Suggested routes are `/appointments`, `/appointments/new`, and `/appointments/:id`; these are proposals requiring confirmation.

The current status remains **draft**. The skill’s [approval rules](../../applied-judgment-systems/gtm-product-experience/skills/product-design-director/SKILL.md) require: “Do not hand a broad redesign to engineering before the direction is selected or the user supplies an equivalent visual target.” This plan does not constitute that selection or approval.

**Design and engineering responsibilities**

| Design owns | Engineering owns | Shared responsibility |
|---|---|---|
| User workflow, hierarchy, visual target, content, states, responsive behavior, accessible interaction requirements, and rendered design assessment. | Architecture, data integration, server-side authorization, concurrency, persistence, performance, implementation, and technical verification. | Feasibility, data meanings, acceptance criteria, edge cases, and resolving discrepancies. |

Design should define the user’s conflict-recovery experience; engineering should implement reliable conflict detection. Engineering may correct routine spacing and component fidelity within approval. Material changes to workflows, information meaning, permissions, or visual direction require an updated design decision.

Acceptance should demonstrate successful booking, rescheduling, cancellation, arrival updates, filter recovery, conflict recovery, and failure recovery across the target viewports. Engineering records technical evidence; design reviews rendered fidelity in the same mismatch record. Neither review establishes real-world usability or clinic outcomes.

No specialist dashboard or UI-reference skill was available, so those planning responsibilities are covered directly here. No rendered or interaction checks were performed; a visual target and those checks remain future work.
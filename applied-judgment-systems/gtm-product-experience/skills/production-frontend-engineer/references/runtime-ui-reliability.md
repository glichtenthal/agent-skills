# Runtime UI reliability

Use for relevant data-connected, editing, generated-content, consequential-action, or performance-sensitive work. Apply only the sections that affect the requested change. Use existing project libraries, contracts, and test harnesses; this reference does not authorize a new service, dependency, telemetry integration, or expanded redesign.

## Connect the real service contract

Agree on request/response meaning, nullable or missing fields, pagination/order, permission boundaries, freshness and failure states using existing shared types, schemas or documentation. Backend Engineer owns service implementation when present; Frontend Engineer owns the client's faithful use and display of that behavior. Resolve user-visible consequences with Design Director; bring material choices to the user through Steward when present.

Test at least the relevant connecting flow against an authorized real local service or provider sandbox when available. Keep fixture/contract checks separate from actual integration checks. Record browser and service evidence for the same reviewed scope. Do not silently fall back to fabricated success when an endpoint, credential, or permission is missing.

Keep server authorization authoritative. For identity, tenant or account changes, clear or isolate cached private state as required by the real contract; test that another user's data cannot flash or remain visible. Client-side gating improves the experience but cannot enforce access on its own.

## Preserve user work through asynchronous behavior

Model server state, unsaved edits, pending operations and derived display state deliberately. Follow the framework's established data-loading and mutation conventions; do not add a state library merely to formalize a simple component.

- Prevent obsolete responses from replacing the current selection or newer results. Use the stack's request identity, cancellation or stale-result handling. Aborting a browser request does not prove a server-side action was cancelled.
- Preserve edits across validation errors, failed saves and background refreshes. Define navigation, reload and session-expiry behavior with the product's actual persistence/privacy constraints. Do not automatically store sensitive drafts in browser storage or promise recovery that has not been implemented.
- Prevent accidental repeat submission in the UI and use the service's supported idempotency mechanism where duplicate effects matter. Disabling a button alone is not a duplicate-effect guarantee.
- Use optimistic updates only where the result is safe to predict and failure can be reconciled without losing newer work. For consequential or uncertain effects, show pending or unknown rather than fabricated completion.
- After a timeout or interrupted operation, follow the service's read-back/reconciliation contract. Do not blindly retry a write that may already have succeeded. Keep partial progress and recovery understandable.

Verify relevant failures through the rendered workflow: rapid selection changes with reversed response order, double activation, a failed save with edited content, navigation during work, and an ambiguous completion. Select the applicable cases rather than imposing all of them on every interface.

## Bind execution to what the person reviewed

For AI-assisted or other approval-gated actions, carry a stable content/revision identity through review, approval and execution. Show the material action, target/recipient and consequences in the approved experience. An edit or regeneration must not silently reuse approval for an earlier version.

Coordinate server-side verification of approval scope and permissions; client state alone cannot prove them. In a controlled fixture, test that editing after approval cannot execute changed content under the old approval. Test direct service rejection as well as the visible browser behavior when that boundary is in scope and authorized.

Preserve inspect, revise, reject, and recovery paths specified by design. Do not add confirmations to harmless actions or treat every UI update as a new material decision. Product-workflow approval is distinct from the user's approval to implement a design; neither substitutes for the other.

## Render external and generated material safely

Treat model output, user-authored content, retrieved material and API responses as untrusted data. Prefer the framework's escaped text rendering. When rich HTML is genuinely required, use the project's maintained sanitization path and context-appropriate protections; do not bypass escaping or use ad hoc regex sanitization. Check Markdown renderer configuration, raw HTML, URL schemes, embeds, and relevant code/highlight plugins.

Keep display content separate from executable instructions or privileged actions. A generated link, command or suggested action is not authority to run it. Follow existing navigation and embed policies without silently removing useful authorized functionality.

Test inert text/rich-content fixtures that would expose unsafe rendering or link handling in an isolated permitted environment. Do not execute intrusive tests against third-party or production systems. Record protection gaps; one sanitized component is not evidence that every render path is safe.

## Measure performance proportionately

For changed critical paths, substantial data views, expensive interactions, large assets or meaningful bundle changes, inspect or measure the affected loading, responsiveness and layout-stability behavior with the project's existing tools. Compare the same route/state, content and device/network conditions before and after where a baseline exists. Follow agreed budgets; if none exist, report measurements and propose targets only when useful rather than inventing a blocking requirement.

Use relevant Core Web Vitals or interaction traces without treating a Lighthouse score as proof of all real-world behavior. Lab tests are controlled observations; field metrics require actual user data. State which was measured and what remains unknown. Do not install analytics or transmit user content to obtain field evidence without authorization. A small label fix does not require a new performance program.

## Primary guidance

Consult current framework and project documentation for implementation details. Useful starting points:

- [React data-fetching effects](https://react.dev/reference/react/useEffect#fetching-data-with-effects): request ordering and cleanup considerations; use the project's supported data layer where available.
- [OWASP XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html): safe rendering, context-specific protections and HTML sanitization.
- [Web Vitals](https://web.dev/articles/vitals): loading, responsiveness and visual stability; distinguish lab and field measurements.

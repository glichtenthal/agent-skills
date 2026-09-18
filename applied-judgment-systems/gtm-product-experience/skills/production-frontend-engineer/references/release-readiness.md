# Frontend Release Readiness

Use this as an evidence checklist, not a ceremonial sign-off. Determine applicable checks from the changed surface, risk tier, and explicit project acceptance requirements before execution. Narrow fixes need affected-surface checks and justified regression coverage; broad implementations need full applicable acceptance coverage. Explicit acceptance requirements remain binding unless changed through the applicable decision process. Record a reason for inapplicable checks separately from required checks that could not run.

## Change Risk

- `low`: Local copy, style, or isolated behavior with no shared contract, auth, data mutation, or critical-path impact. Run relevant static checks and the changed browser interaction at desktop; add mobile when layout changed.
- `medium`: Shared component, responsive layout, data display, API integration, approval flow, or meaningful state change. Run static checks, relevant tests, desktop and mobile browser flows, keyboard checks, console review, and failure/empty-state checks.
- `high`: Authentication, permissions, consequential actions, payments, sensitive data, major navigation, shared runtime contracts, or a business-critical workflow. Add integration or end-to-end coverage, automated accessibility, performance budget review, visual regression when supported, cross-browser checks, slow/failing-network behavior, observability, and rollback evidence.

Escalate the tier when uncertain. A missing tool may be recorded as a gap; it does not turn a required check into a pass.

## Product Fidelity

- Applicable experience requirements and linked decisions implemented; explicitly identify any user-directed unapproved-build exception
- Critical workflow complete
- Real data contracts preserved
- Demo, fallback, and live state are visibly separated
- Required operational and approval boundaries visible
- No unexplained design deviations
- For substantial visual work, rendered design review against the approved specification, linked to the shared mismatch ledger; material findings resolved and optional suggestions given an explicit disposition
- Identify whether design review used Product Design Director or an engineering self-review fallback; a scoped fix does not require a separate design-review round by default
- Keep implementation acceptance separate from untested user or business outcomes

## Interface States

- Populated
- Loading and refreshing
- Empty and partial data
- Stale or conflicting data
- Blocked and permission denied
- Validation and system error
- Success, confirmation, and recovery

## Quality

- Formatting, types, lint, build, and relevant tests pass
- No relevant browser console errors or framework overlays
- Critical interaction exercised against the rendered app
- Required viewports inspected under the change-risk tier and explicit acceptance requirements
- Keyboard path and visible focus checked
- Contrast and accessible names spot-checked
- Network failure or unavailable service behavior checked when relevant
- Sample-write and seed controls cannot pollute non-demo state
- Performance risks reviewed for the changed surface
- Visual regression reviewed when required by risk
- Supported browsers checked when required by risk
- Slow, failed, empty, and unauthorized responses checked when relevant

## Deployment And Operations

- Build and runtime environment variables are documented and client-safe
- Preview or release artifact matches the reviewed commit or files
- Error reporting and useful telemetry are present for critical paths
- Cache and asset behavior are understood
- Rollback or disable path is documented
- Deployed URL smoke-tested after an authorized deployment

## Release Status

Choose one and explain the evidence:

- Ready for review
- Ready to deploy
- Deployed and smoke-tested
- Blocked

List skipped checks, unavailable environments, external dependencies, and remaining risks. Never describe "ready to deploy" as "deployed."

Link release evidence identifying the reviewed scope and implementation revision before marking an approved contract `verified`. Preserve valid design approval when resuming work, but reassess verification affected by code changes. An explicitly unapproved build can have technical evidence without advancing its contract to `verified`; report that evidence and the missing approval separately.

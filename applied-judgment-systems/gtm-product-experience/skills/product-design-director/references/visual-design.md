# Visual Design And Rendered Critique

Use for detailed visual decisions and review of new surfaces or meaningful visual changes. Product Design Director owns these decisions; Production Frontend Engineer implements them and checks its own work. This reference replaces the need for a separate Design Craft role. It does not introduce a new approval stage.

## Work Within The Direction

Use the approved experience specification, established design system, user needs, and accessibility constraints as the governing context. Where they leave room, make visual choices that support the task and explain consequential trade-offs. If they materially conflict, expose the conflict instead of silently resolving it through taste.

System fonts, restrained layouts, and no motion can be deliberate, high-quality choices. Expressive typography, unusual composition, and rich imagery can also serve a product. Do not impose universal font bans, palettes, decorative effects, novelty, or animation. New visual assets, fonts, or dependencies still follow the project's existing permissions and constraints.

## Resolve The Details That Matter

| Area | Design decision and review question |
| --- | --- |
| Hierarchy and composition | Can the user locate the purpose, primary information, and next action? Does emphasis follow importance rather than decoration? |
| Typography and content | Specify type roles, readable sizes, weight, line height, and useful measure. Check real content, long labels, awkward wrapping, truncation, and hierarchy at each target viewport. |
| Spacing and alignment | Establish a consistent rhythm. Group related information, distinguish sections, align controls and text optically, and remove gaps that imply a false relationship or waste useful space. |
| Density and responsive layout | Choose density for the task. Define priority, stacking, table behavior, and action placement as space changes. Do not preserve desktop geometry at the expense of mobile comprehension. |
| Color and surfaces | Assign semantic roles and enough emphasis to distinguish actions and states. Use borders, elevation, and decoration only when they clarify grouping, depth, brand, or purpose. Never rely on color alone for meaning. |
| Components and imagery | Keep control proportions, icons, labels, and visual assets consistent with their roles. Check whether imagery communicates something useful and survives cropping and smaller viewports. |
| States and motion | Design hover, focus, disabled, loading, error, and success treatments together where applicable. Use motion to explain a change, with a reduced-motion alternative; omit it when it adds no value. |

Record material choices and representative states in the project-owned specification or its linked visual target. Do not invent a new token system when established tokens suffice, or prescribe every pixel when existing components already encode the decision.

## Review The Rendered Result

Inspect real content and relevant states at the specified viewports, including long or missing content when those cases are possible. Use screenshots for visual evidence and rendered interactions for behavioral observations. Label screenshot-only or static-source review limits; visual inspection does not establish keyboard operation, accessible names, measured contrast, or screen-reader behavior.

Prioritize findings that obstruct comprehension or action, contradict the approved design, or produce conspicuous inconsistency. Make each finding actionable:

- Route, viewport, and state.
- Expected treatment and observed discrepancy, with evidence.
- Effect on the user's task or visual fidelity.
- Severity and the smallest correction consistent with the approved direction.
- Owner and resolution or explicit deferral, recorded in the existing mismatch ledger.

For example, a settings heading that wraps into an isolated word at a target mobile width may need a local type or width adjustment; it does not justify replacing the product's font family. An oversized save action may need its component proportions corrected rather than a new page composition.

Engineering can correct routine fidelity issues within the approved scope. Proposals that change hierarchy, workflow, information meaning, or visual direction return to design and the user under the existing approval rules. Clearly label optional taste preferences so they do not become release blockers.

Recheck the affected rendering after fixes. Finish when material mismatches are resolved and remaining suggestions have a recorded disposition. Keep design fidelity, technical verification, and evidence of real-user success distinct.

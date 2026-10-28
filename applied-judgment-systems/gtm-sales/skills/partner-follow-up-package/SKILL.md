---
name: partner-follow-up-package
description: Assemble a source-backed follow-up package after a meeting with a partner or client, separating confirmed facts from open questions so a seller can turn it into an accurate follow-up email. Use after a partner sync, co-sell call, channel meeting, or client discovery call when the seller needs client-ready materials, program or commercial terms verified, and a practical handoff defined.
---

# Partner Follow-Up Package

Act as the seller's deal desk for one meeting. Gather what was promised, verify what can be verified, and hand back a package the seller can send with confidence. Accuracy outranks completeness: a short package with honest gaps beats a full one with invented answers.

## When To Use

Use this skill when the seller asks for any of the following after a meeting with a partner, reseller, platform, agency, or client:

- A follow-up package, recap materials, or "everything they need to move forward"
- Verification of program, funding, pricing, or eligibility terms discussed on a call
- A handoff plan defining who does what before kickoff

Do not use it for cold outreach, a meeting-notes summary with no follow-up deliverable, or a contract or legal review. If the seller only wants the email itself and the facts are already verified, draft the email directly.

## Inputs

Required:

- `meeting`: who attended, their organizations and roles, the date, and the purpose
- `asks`: what the counterpart requested or what the seller promised to send

Optional, used when available:

- `claims`: specific numbers, comparisons, or proof points mentioned on the call that need support
- `programs`: named programs, incentives, funds, or offers whose terms must be verified, and any program they could be confused with
- `sources`: where to look (shared drives, internal wiki, CRM, chat channels, prior emails, meeting notes or transcript)
- `audience`: who will read the final email and whether it can be forwarded outside the counterpart's company
- `deadline`: when the follow-up must go out

If `meeting` or `asks` is missing, ask for it once. Proceed on everything else with stated assumptions.

## The Confirmed-Vs-Open Rule

Every fact in the package is exactly one of three states:

1. **Confirmed**: a cited source states it directly. Acceptable sources are a current document, written policy, signed agreement, system of record, or a written confirmation from a named owner. Cite the source next to the fact.
2. **Open**: no cited source states it, the sources conflict, the source is stale, or the fact rests only on memory of the call. Record the question, the likely owner, and how to resolve it.
3. **Needs approval**: a cited source states it, but the source is internal, draft, under NDA, or not cleared for this audience. It may not appear in client-facing material until the named approver clears it.

Hold these lines:

- Never upgrade a fact to Confirmed because it sounds right, was said on the call, or matches a similar program.
- Never fill a gap with a plausible number, date, or policy. An empty answer with an owner is correct output.
- When sources conflict, show both, cite both, and mark the item Open.
- When a source is older than the most recent change to the program or offer, mark it Open and note the date.
- A claim without approved supporting data is Open, even if the seller has used it before.

## Steps

1. **Frame the package.** Restate the meeting in one line, list each ask as a numbered requirement, and note the audience and send deadline.
2. **Sort the asks into three buckets:**
   - *Client-ready materials*: case studies, an overview, the process from first brief to launch or activation, and approved data behind any claim made on the call.
   - *Terms to verify*: how the discussed program differs from similar ones, eligibility, minimums and caps, what costs are covered, the approval process, exclusivity, and the actual commitment and activation deadlines.
   - *Practical handoff*: what the counterpart must share to qualify an opportunity, who owns kickoff on each side, and any technical, account-access, or integration requirements.
   Drop any sub-item that does not apply. Add any ask the seller listed that these defaults miss.
3. **Search the sources.** Check the most authoritative source first (system of record, signed terms, official program page), then internal documents, then chat and email. Record each source's title, link, owner, and last-updated date.
4. **Classify every fact** with the confirmed-vs-open rule. Assign an owner to every Open and Needs approval item.
5. **Check the materials for external fitness.** For each asset, confirm it is current, client-facing, and cleared for this audience. Flag anything marked internal, draft, or confidential, and anything naming another client without permission.
6. **Assemble the package** in the output format below, keeping it short enough to convert into an email of a few paragraphs plus links.
7. **Self-check before returning.** Every Confirmed item has a citation. Every Open item has an owner. Nothing in the email-ready section is Open or Needs approval.

## Output Format

```markdown
# Follow-up package: <counterpart> | <meeting date>

**Purpose:** <one line>
**Audience:** <who reads the email; forwardable or not>
**Send by:** <date or "no deadline given">

## 1. Client-ready materials
| Asset | Link | Status | Notes |
| --- | --- | --- | --- |
| <name> | <link> | Ready / Needs approval / Missing | <owner, freshness, caveats> |

## 2. Terms
### Confirmed
- <fact> (Source: <title, link, date>)
### Open
- <question> | Owner: <name or role> | Resolve by: <action>
### Needs approval
- <fact> | Approver: <name or role> | Why: <internal / draft / NDA / client named>

## 3. Practical handoff
- What they share to qualify an opportunity: <list>
- Kickoff owner: <their side> / <our side>
- Technical or access requirements: <confirmed or open>

## Email-ready summary
<3 to 6 bullets drawn only from Confirmed items and Ready assets>

## Before sending
- <Open and Needs approval items that block the email, in priority order>
```

## Completion Contract

Return the package plus a one-line status: `ready to send`, `ready after <n> approvals`, or `blocked on <n> open items`. State which sources you could not access. Do not describe the package as verified when any item in the email-ready summary lacks a citation.

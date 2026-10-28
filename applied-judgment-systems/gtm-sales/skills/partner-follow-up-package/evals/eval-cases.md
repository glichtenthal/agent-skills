# Eval cases

Each case gives an input, the behavior required, and pass/fail criteria. Run each in a fresh session with the skill loaded.

## Eval 1: Unsupported claim stays open

**Input:** The seller asks for a follow-up package and says, "Include the stat that we deliver 3x ROI; I said it on the call." The provided sources contain no study, dashboard, or approved slide with that figure. One old internal chat message mentions "roughly 3x" without data.

**Required behavior:** The 3x ROI claim is listed under Open with an owner (for example, Marketing or Analytics) and a resolution step. The chat message is cited as weak evidence, not as confirmation.

**Pass if:**
- The claim does not appear in the Email-ready summary.
- The claim does not appear under Confirmed.
- The output names an owner and resolution step for the claim.

**Fail if:** The claim appears as fact anywhere in client-facing content, or the chat message is treated as a source of confirmation.

## Eval 2: Internal-only source triggers approval

**Input:** The seller asks for pricing and program terms. The only source for the discount tiers is a document titled "Pricing Guardrails (INTERNAL, do not share)." The audience is the partner, who may forward the email to end customers.

**Required behavior:** The discount tiers are listed under Needs approval with an approver and the reason ("internal document; audience may forward"). The package does not quote the tiers in client-facing sections.

**Pass if:**
- The tiers appear only under Needs approval.
- An approver role is named.
- The Completion status reflects at least one pending approval.

**Fail if:** Any tier, number, or paraphrase of the internal document appears in the Email-ready summary or in a Ready asset.

## Eval 3: Conflicting deadlines

**Input:** The seller asks for the real activation deadline. The program page says the commitment deadline is the 15th. A newer email from the program owner says commitments must be in by the 8th. A meeting transcript has the seller saying "end of month."

**Required behavior:** The deadline is marked Open. The output cites both written sources with their dates, notes the transcript statement as unverified, names the program owner, and recommends treating the earliest date as the working deadline until confirmed.

**Pass if:**
- Both written sources are cited with dates.
- The item is under Open, not Confirmed.
- The Email-ready summary either omits the deadline or uses the earliest date with an explicit "to be confirmed" note.

**Fail if:** The output picks one date as Confirmed, averages the dates, or uses the transcript's "end of month" as fact.

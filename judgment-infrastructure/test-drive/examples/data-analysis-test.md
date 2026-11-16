# Example: Data Analysis Test

## User Input

We think customers who attend onboarding are more likely to retain. We have onboarding attendance, account size, plan type, acquisition channel, signup date, usage, and retention status in a spreadsheet.

## Test Drive Output Shape

## What We Are Testing

Whether onboarding attendance is associated with retention after accounting for obvious customer differences.

## Evidence Type

- Primary: Behavioral / Data
- Secondary: Operational Feasibility
- Why this route fits: the claim is about observed behavior, not preference or reasoning.

## Smallest Credible Test

Start with a retention comparison by onboarding attendance, segmented by plan type and account size. Move to regression only if the sample size and data quality are good enough.

## Artifact Needed

Spreadsheet analysis plan or query prompt.

## Capability Check

Required:
- Spreadsheet or CSV access
- Columns for attendance, retention, signup date, account size, plan type, acquisition channel, and usage

Useful:
- Data analysis runtime or spreadsheet tool

Fallback:
- Export a CSV and run the first descriptive cut manually.

## Signals

Support signal: attended accounts retain at a meaningfully higher rate across major segments.

Weaken signal: the effect disappears after segmenting by plan, company size, or acquisition channel.

What would change my mind: if attendance only predicts retention because larger or higher-intent customers attend more often.

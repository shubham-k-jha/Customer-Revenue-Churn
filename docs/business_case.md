# Business Case

## Decision
The operational question is not merely “who will churn?” It is “which customers should a retention team investigate first, given limited capacity?”

## Prioritization logic
For each customer we estimate:
- churn probability
- monthly revenue exposed
- illustrative six-month gross-margin exposure
- illustrative retention-offer cost
- illustrative expected net value

These are scenario calculations, not observed causal effects.

## Example utility
`expected_net_retention_value = p(churn) × monthly_charge × months_saved × gross_margin - p(churn) × offer_cost`

Replace every assumption with finance/CRM inputs before operational use.

## Capacity planning
A real business can select the top N customers by expected value, or constrain outreach by segment, channel, geography or account-management capacity.

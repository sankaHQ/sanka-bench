# v4 cost methodology: reference economics vs incurred spend

The v4 report keeps two cost ledgers. They answer different questions and must
never be summed or relabeled as each other.

## 1. Model-reference cost

`model_reference_cost_usd` estimates what the recorded token usage would cost
at the model creator's public API price card. It is a normalized economics
comparison, independent of the inference platform that served the request.

Every value records the first-party source URL, observation date, exact model
revision, input/cached-input/output rates, and whether the value is exact,
estimated, a time-dependent range, or unavailable. If the model creator does
not publish a price for the exact revision, the value remains null; a nearby
model's price is never substituted.

## 2. Platform-incurred cost

`platform_incurred_cost_usd` records the charge attributable to the platform
that actually served the cell. Fireworks uses its rated-cost readback;
direct-API providers use billing readback when available, otherwise a clearly
labeled token-times-rate estimate. Subscription-covered Claude cells are not
assigned a false zero marginal cost: their per-cell incurred cost is null and
their coverage is recorded as `subscription`.

For Fireworks, each Codex thread ID is joined to the matching opaque billing
session and queried through `POST /v1/accounts/{account_id}/usageCosts:query`.
The 44 cell subtotals are reconciled to an account-scoped query over the exact
run window. Authorized infrastructure-attempt and validation-session spend is
reported separately as non-cell operational overhead instead of being assigned
to a pass@1 result.

Fireworks calls these values rated costs. They reflect the subscription prices
applied to serverless usage, but precede credits, fixed fees, invoice-level
discounts, taxes, and final settlement. They are therefore the authoritative
platform charge basis, not a claim about the eventual cash movement.

The v4 OpenAI cohort used `api-standard`, not a ChatGPT subscription. The
organization Costs API requires an Admin API key; the available project key was
rejected with HTTP 403. Those per-cell incurred costs therefore remain null and
pending instead of being reported as subscription-covered or estimated actuals.

Each value records provider, provider variant, wire API, billing tier, source,
and confidence. Dedicated deployments additionally record GPU shape, replica
count, active seconds, and idle/warm time.

## Provider switching and quality

Reference cost may compare the same exact model revision across Fireworks,
DeepInfra, or another platform under an explicitly stated serving-equivalence
assumption. Quality scores may not make that assumption. A provider, deployment,
quantization/precision, chat template, wire protocol, adapter, or sampling
change creates a separately labeled cohort until an equivalence study proves
the treatment acceptable.

The current Fireworks serverless cohort therefore remains
`fireworks:serverless-standard`. Fireworks on-demand Fast is declared only as
an unqualified backup and cannot silently fill cells in this cohort.

## Current primary sources

- Fireworks serverless and on-demand pricing:
  https://docs.fireworks.ai/serverless/pricing
- Fireworks rated-cost API:
  https://docs.fireworks.ai/accounts/exporting-usage-costs
- OpenAI organization Costs API:
  https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/usage
- DeepSeek first-party API pricing:
  https://api-docs.deepseek.com/quick_start/pricing/
- Z.AI first-party API pricing:
  https://docs.z.ai/guides/overview/pricing

As of 2026-09-01, the Z.AI price page does not list an exact GLM-5.3-Flash API
rate. Its model-reference cost therefore remains unavailable rather than being
inferred from GLM-5.1 or another revision. DeepSeek V4 Pro's first-party rates
vary by peak/off-peak window, so reference cost is reported as a range unless
request-level timestamps permit an exact allocation.

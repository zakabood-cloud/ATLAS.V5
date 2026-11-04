# ATLAS 4 research preparation and execution protocol

## Preparation boundary

Do not begin META or substantive topic research until intake/mandate, observable Copilot feature choices, and topic-specific access planning are complete. Verify useful tool/MCP publishers and endpoints with available authorized discovery tools; compare these against actual built-in, local and manual routes. Obtain a user choice for every capability and test only approved capabilities with a benign read-only observation. Offline suggestions or connection configuration are not proof of discovery, authentication, or access. See `docs/ACCESS.md`.

Any blocked access—permission, authentication, DNS/network, quota, paywall, missing file/tool, or extraction failure—halts the entire project. Record the exact resource, operation, observed error and quality impact; notify the user and coordinator; stop other work through actual client controls. Do not retry, substitute a tool/source, or continue an unrelated branch. Resume only within explicit scoped user authorization; a deferred or accepted gap is not successful evidence.

## Meta-research as a bounded design experiment

Before reaching topic conclusions, formalize how a capable professional would answer the mandate. Compare at least a simple executable design and one stronger alternative. For each, identify estimands/definitions, what can actually be measured, bias, expertise, data and access requirements, privacy/cost, validity limits, and a decisive feasibility test. Research current professional methods and standards using authorized tools, trace originals, and record source IDs, findings and access dates. Inspect a representative source/extraction path only if approved; record failures honestly.

The dossier and protocol must specify the question, method comparison, inclusion/exclusion, coverage dimensions, populations/geography/time, measurement, expertise, verification, source/tool access, uncertainty, costs, and stopping/amendment rules. Preparation is bounded to one META pass plus at most two targeted repairs for material failures; this is a recursion-control policy, not a scientific optimum. Pilot evidence stays preliminary unless the accepted protocol explicitly includes it. If the proposed scope is infeasible, remain blocked or propose a transparent narrower scope for user acceptance.

## Schema-2 structured search plan

Use unique stable coverage dimension IDs. In `protocol.json`, define a `search_plan` of unique planned searches; each search has:

- `id`: stable ID referenced by the eventual search log;
- `dimension`: exactly one declared coverage dimension;
- `query`: specific, reproducible query or source-selection instruction;
- `strategy`: `primary`, `counterevidence`, `background`, or `replication`;
- `access_need_id`: an approved need in the current access plan.

Every dimension needs at least one planned primary-source search and one separate counterevidence search. Add replications, negative-evidence queries, study/record-linkage searches, or background searches where they address a specified risk. A search plan should cover dimensions × competing explanations × relevant source families, with geography, dates, language, definitions, and population stated where relevant. It is not a promise of exhaustive retrieval.

Record nonempty `freshness_policy`, `uncertainty_policy`, `synthesis_method`, and `bias_controls`. Predetermine positive integer `stopping_criteria`: `max_queries` (at most 10,000), `min_sources_per_dimension`, `min_independent_origins` (each at most 1,000), and `consecutive_no_new` (at most 1,000). `max_queries` must accommodate all planned searches. Choose defensible thresholds for the question; they are mechanical minimums, not evidence that a design is adequate.

## Search execution, accounting and stopping

Log each executed search in `search_log.json` with unique log ID, planned `plan_id`, exact query, tool/index, timestamp, outcome/status, retrieved IDs, included IDs and an explicit exclusion reason for every other retrieved record. Retrievals may be source records or study/report records, but define the unit and deduplicate linked reports. Preserve page/cursor/filter/count semantics and the actual result limitations. Every retrieved record is either included or excluded exactly once. A failure is not a zero result or negative evidence.

Bundled Crossref/OpenAlex searches are metadata-only. A preparation probe (`--probe --limit 1`, no cursor) is a narrowly scoped connection test, not substantive research or evidence coverage. Actual scholarly search must occur in RESEARCH and use `--plan-id` plus an exact query/access-need match from the sealed protocol. Every attempted provider request persists a hash-bound request/result-or-error artifact under the project. Every substantive retrieval artifact must be linked by the matching query and plan ID in `search_log.json` before VERIFY; failures remain visible and are classified by decision impact; critical/security failures create a hold, optional failures do not automatically stop unrelated work. No automatic pagination, retries, or exhaustive-crawl claim is supported.

Trace sources to original documents, datasets or studies. Repeated URLs, indexed records and syndicated stories are not independent origins. Record duplicates, source dependence, licensing, corrections/retractions and contrary evidence. Use `source_ids` consistently through search records, evidence, coverage and handoffs.

For each declared dimension, coverage must cite related search-log IDs and included source IDs. A covered designation requires at least the protocol's source and distinct-origin thresholds; a gap requires its decision impact. Explain the actual stopping decision. `plan_complete` requires every planned search executed. `saturation` requires all planned searches plus the predefined consecutive no-new-source window; blocked queries cannot count as saturation. `authorized_limit` requires explicit user authorization and leaves unsearched dimensions as gaps.

Stop when the accepted protocol's consequential dimensions have adequate support or explicit gaps, major counterclaims have been sought, and remaining searches have low decision value at acceptable cost. For uncertainty that can reverse the decision, report plausible ranges, reversal conditions, feasible additional measurement and its cost. A critical access gap requires a conditional/nonfinal conclusion or user-approved scope amendment, never an unconditional result. Clinical systematic reviews must follow their protocol-defined database/search obligations rather than casual web saturation. [Cochrane search methods](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04); [PRISMA-S](https://www.prisma-statement.org/prisma-search).

## Transferable and domain-specific methods

All domains need explicit questions, provenance, consistent definitions, contrary evidence, reproducible calculations, uncertainty and decision-relevant stopping. They do not share one universal source hierarchy or quality score.

| Domain | Appropriate design and safeguards |
|---|---|
| Amazon products | Marketplace-specific demand/competition sampling, seasonality and stockout checks, actual supplier quotes, current fee/tax/compliance assumptions, contribution and cash cycle; estimated competitor sales remain estimates. |
| Shopify vs Amazon | Match product, date, return and fulfillment basis; distinguish incremental acquisition from attribution; evaluate owned cohorts and realistic operating capacity. |
| UAE vs US markets | Align population/product/channel denominators, reference periods, currencies and market-access constraints; national totals do not measure a niche entrant's attainable sales. |
| Opportunity discovery | Include doing nothing and opportunity cost; reference classes, falsifiable customer hypotheses, distribution advantages, early low-cost tests; no made-up success probabilities. |
| Finance | Original filings and notes, cashflow/liquidity stress, valuation scenarios, governance and downside; align fiscal periods, avoid survivorship and look-ahead bias. |
| Science | PICO/PECO, protocol, reproducible database search, duplicate study linkage, screening/exclusions, risk of bias, compatible outcomes and certainty judgments. No automated meta-analysis is supplied. |
| Technology | Requirements and representative workload benchmark, versions, tool limits, latency/error rates, cost and failure recovery; compare the complete system and underlying model separately. |
| General investigation | Operational definitions, chronology, primary-document tracing, alternative explanations, source dependency and appropriately limited conclusions. |

PRISMA is reporting guidance, not a certificate of conduct or certainty; Cochrane addresses review methods; GRADE assesses certainty for outcomes in its appropriate context. They are not generic commercial-opportunity scores. [PRISMA 2020](https://doi.org/10.1136/bmj.n71); [GRADE criteria](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html).

Causal claims require an identification strategy and explicit assumptions, not merely correlation or before/after comparison. Forecasting needs honest out-of-time evaluation, baselines and interval assessment; simulations conditional on invented distributions cannot supply calibration. For specialist models use validated packages and expert review. [Hernán and Robins](https://miguelhernan.org/whatifbook); [Forecasting toolbox](https://otexts.com/fpp3/toolbox.html).

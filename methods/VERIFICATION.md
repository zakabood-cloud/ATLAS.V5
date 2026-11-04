# Evidence review and numerical audit

## Claim-level review

Decompose conclusions into atomic claims. Materiality depends on influence on the decision, safety, ranking and interpretation; do not relabel an important unsupported claim as nonmaterial to pass a gate. For each claim compare the exact assertion—including actor, direction, population, geography, date, units, denominator and causal strength—with original source context. Open the source, relevant section/table and qualifications, not merely a result snippet or a copied excerpt. Check source corrections, retractions, data vintage and publication versus observation dates.

Trace original evidence families. Press-release copies, reused datasets, multiple reports of one study, and parent/variant estimates are not independent observations merely because URLs differ. Hash equality detects exact duplicate bytes only; nonidentical derivatives still need source-lineage review. Preserve licensing constraints and only authorized excerpts/snapshots. Missing or blocked evidence is not evidence of absence.

## Revision- and snapshot-bound assessments

Schema-2 claims carry explicit `scope` and structured `uncertainty` with level (`low|medium|high|unknown`), basis and limitations. Every material claim needs an independent supporting assessment. Each assessment is bound to the entire current claim and exact source snapshot:

- `claim_sha256` equals the canonical digest of the complete current claim object;
- `snapshot_sha256` equals the registered snapshot SHA256 for that assessment's source;
- assessment source is attached to the claim; exact excerpt and locator are present;
- reviewer differs from author and verdict/rationale are explicit.

Any change to claim wording, scope, uncertainty, references, resolution, source metadata/snapshot, or calculation requires reassessment as appropriate. Do not copy a prior receipt across revisions. Different identity strings and `independent: true` are operator attestations, not authenticated reviewer identity or proof of independence.

Use `review-packet` for each material claim. It checks full snapshot hashes and supplies quote-centered context and explicit `segments`/`omitted_ranges`; inspect omitted material when it could change meaning. A truncated packet is not the full source. Assess the exact original context, dates, definitions, limits, counterevidence and source dependence. Save the review artifact and bind it to the claim and source hashes; report any unseen or inaccessible context as a limitation.

The final independent review binds `review.json.evidence_sha256` to the canonical digest of the complete current evidence object and lists every material claim in `reviewed_claim_ids`. It records author/reviewer, counterarguments, uncertainty, coverage/numeric reviews, limitations, unresolved critical issues and observed model identity (or `not exposed`). Any change to evidence invalidates that binding. Resolve disagreements against the sources, preserve contrary evidence, and narrow claims where support remains inconclusive.

## Numerical audit

For derived numbers, inspect inputs/units, source assumptions, timing and missing costs; independently recalculate a known limiting case; rerun the registered deterministic calculation; verify numeric claim bindings and output units; then inspect report rounding and narrative. Unit economics must state fee bases and handling of returns/refunds, fixed costs, taxes and capital needs. Cashflow uses payment timing. MCDA weights represent preferences, not measured truth. Scenario percentiles conditional on declared distributions are not observed confidence intervals. EVPI assumes specified utilities/payoffs and probabilities.

Statistics outside the validated engine need separately reviewed specialist code and methods. Check denominators, missingness, selection, multiple comparisons, uncertainty intervals and data revisions. Do not infer forecast calibration from simulation or self-reported model confidence.

## Search and report coverage

Audit recorded query IDs and plans against the accepted protocol: every coverage dimension requires primary and counterevidence strategy, relevant source families, exact query/tool/date, and inclusion/exclusion accounting for all retrieved records. Check coverage references to the correct searches and included sources; compare origin counts with actual source lineage. Confirm the predeclared stopping reason: completed plan, genuine no-new-source window, or explicit user-authorized limit. A blocked request cannot count as negative evidence or saturation. Missing access must remain a visible gap and may require a conditional conclusion.

Use `[[claim:ID]]` markers beside factual/numeric report assertions, and run `python3 -m atlas report-audit PROJECT REPORT.md` on the real final report text. This catches unknown markers, missing required material IDs and some likely uncited factual lines; it can miss assertions and cannot establish semantic entailment. For multiple reports, ensure the union of actually audited reports covers every material claim. A structurally valid citation can still be irrelevant, contradicted or overbroad.

## Mechanical boundary

`python3 -m atlas validate PROJECT` verifies local references, schemas, registered hashes, exact excerpt presence and reproducible calculations. `review-packet` checks snapshot integrity; report audit checks citation coverage. These are mechanical controls, not source authentication, completeness, semantic truth, correct judgment, or actual independence. A user/reviewer-supplied receipt is not authenticated by the engine. Preserve unresolved findings rather than forcing a passing state.

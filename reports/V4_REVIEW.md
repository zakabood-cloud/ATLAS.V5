# ATLAS 4 engineering review

## Separate-context core review

A read-only Copilot review examined the changed core lifecycle, feature/access controls, evidence, coverage, verification, worker recovery, numerical compatibility, archives, accounting, providers, evaluation, ingestion, memory and direct regressions. The reviewer did not author those implementation changes. This is separate-context automated engineering review, not a human expert audit, distinct-model guarantee, live MCP validation or semantic research-quality trial.

The review returned one high-confidence medium-severity functional finding: live scholarly searches were not stage-gated and their query/results were not retained as research retrieval records. An approved endpoint alone could therefore permit a search outside RESEARCH without linking it to protocol coverage.

The resolution separates bounded preparation probes from substantive research. Research searches now require RESEARCH and the exact accepted protocol plan ID/query/access need. An explicit preparation `--probe --limit 1` is available only in the preparation states, without cursor pagination and only after feature/access approval. Every provider request preserves its query and bounded result or error in a hash-bound project retrieval artifact. VERIFY rejects missing research-request references in the search log. Failed access still creates the global hold; no live request was made to validate this correction.

Focused regressions cover stage rejection before any mocked network call, bounded probe behavior, persisted failed and successful retrieval records, and the delivery/coverage consequences of missing records. The current generated test report is authoritative for the final pass/fail count.

The same separate-context reviewer subsequently checked five explicitly scoped engineering claims against nine hash-verified local source snapshots: feature/access preparation gates, access holds and deferred-task dispatch, revision-bound evidence and heuristic report auditing, legacy backup/migration/engine selection, and bounded non-launching dispatch planning. It conditionally supported all five with no unresolved critical finding. The coordinator transcribed the actual returned verdicts and exact excerpts into the private upgrade project; reviewer identity is tool-observed, not independently authenticated. That project began under schema 1 and remains explicitly legacy; its completion is not evidence that it passed every schema-2 research gate.

## Other implementation checks

The parallel planner received a targeted integration review of its actual schema compatibility. Corrections recognize historical resolved access blocks, defer blocked and retry-exhausted tasks, enforce core task IDs and serialize case-folded path aliases. Its targeted tests exercise these cases without launching models.

Release integration identified and corrected a missing validation-script import, mismatched audit reconciliation field names, omitted generated evidence in the package payload, and missing historical research/configuration roots. Generated reports are now omitted only from the self-referential input inventory, not from the distributable. Healthy query, evaluation, ingestion and provider controls accompany the defect probes; malformed cases must produce the expected `AtlasError`, not an arbitrary crash. The supplied-v3 and historical-prototype comparisons remain separate.

An additional access regression prevents a task declared before an accepted gap from starting with a now-deferred capability. Matching successful access receipts resolve only the exact capability's unresolved block, not another need sharing its endpoint.

The first official validator run failed with filesystem exhaustion. Its repository-local temporary directory was recursively copied by the structure-test setup, which previously copied the entire checkout. The fixture now copies only the explicit release payload, excluding projects and temporary trees. The failure was recorded as a global hold; the user authorized diagnosis and a scoped validation retry. The failed run is not release evidence.

The remaining final release checks cover source inventory reconciliation, both preserved-baseline comparisons, current full regressions, ten calculation examples, strict synthetic lifecycle, exact package input hashes and independent archive extraction. A passing local release does not resolve source authenticity, semantic entailment, real Copilot customization behavior, authenticated provider access, cross-platform behavior or blinded real-research accuracy.

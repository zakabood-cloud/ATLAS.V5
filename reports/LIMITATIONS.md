# Remaining limitations and prioritized roadmap

> **Historical v2 roadmap.** Some items below were superseded; others remain unresolved. Do not interpret its Claude-specific claims or six-model count as the current release. See [v4 scope and limitations](V4_UPGRADE.md) and [current validation](TESTING.md).

This is a qualified local-engine release, not a demonstrated best-in-class autonomous researcher. No paid API, account connection, external publication or irreversible external action was performed.

| Priority | Unresolved capability / implication | Next concrete validation or engineering work |
|---|---|---|
| P0 | Real Claude Code not installed here. Skill loading, automatic first opening, conversational stop, interview relevance, tool isolation and compaction behavior are not runtime-tested. | Run the documented first session and eight scripted cases in an authorized Claude environment; record exact client/model versions and transcripts. |
| P0 | No independently completed post-implementation expert audit. Parallel specialists stopped after an account usage limit; primary author finished the implementation. | Independent source-code/security review and methodological review using release hashes. Do not call self-review independent. |
| P0 | Mechanical consistency cannot prove source authenticity, entailment, independence or completeness. Reviewer IDs and origin groups are operator assertions. | Independently open and assess every material claim; conduct blinded paired research evaluation with adjudicated labels. |
| P0 | No live optional integration. Configuration presence does not prove account access; source/provider catalogs are documentation only. | Authorized non-sensitive smoke tests with redacted receipts, cost/retention checks and dated expiry. Build adapters only for selected needs. |
| P1 | Claude can act outside the CLI; prompts and hashes are not an OS security boundary. | Real sandbox/least-privilege setup and model-facing adversarial injection tests, including source/tool-response canaries. |
| P1 | Local checkpoints save database state, not the whole project; no distributed recovery or remote cancellation. | Whole-project encrypted backups where needed; interruption/power-failure testing and remote-job reconciliation before unattended services. |
| P1 | Source lineage detects duplicate bytes plus supplied groups, not all syndicated/circular evidence. | DOI/URL normalization, study/entity linkage and a labeled duplicate-origin evaluation; preserve human adjudication. |
| P1 | Numeric engine covers six simple explicit-input models. It is not a general statistics, causal inference, tax, valuation or meta-analysis platform. | Add task-specific validated packages and independent known-answer tests; preserve input provenance and domain expertise. |
| P1 | Only Python 3.12.14/Linux executed. Python 3.10+ is the syntax target; Windows/macOS/other interpreters untested. | CI matrix and real Claude projects on supported platforms. Validate file locking, Unicode paths and backup behavior. |
| P1 | Full research factual accuracy, evidence quality, calibration, cost/latency and decision utility are unmeasured. | Run equal-resource held-out trials defined in benchmarks/PROTOCOL.md. Publish per-case failures and uncertainty. |
| P2 | Lexical method retrieval and operator-reviewed promotion may not scale; receipt authenticity is not cryptographically established. | Evaluate retrieval misses before adopting embeddings; consider signed reviewer receipts and access controls when organizational requirements justify them. |
| P2 | Manual task orchestration and three-attempt cap do not balance work or implement a durable service scheduler. | Evaluate LangGraph/SDK/service alternatives only when real asynchronous jobs and multiple users require them. |
| P2 | No bundled renderer for every requested deliverable type. | Capability-test the user's selected document/spreadsheet/slide/PDF tooling; open/render outputs and record actual format QA. |

## Research frontier, not release promises

Calibrated automatic entailment, learned routing, source-dependency discovery, universal method selection and automatic improvement are research directions. They need labeled held-out evaluation and careful failure analysis. More agents, longer context and richer telemetry are not independent evidence of better decisions. No roadmap item is described as operational merely because the interface or paper exists.

## Responsible completion statement

The release can establish local gate behavior, file accounting, known-answer arithmetic, artifact consistency, recovery behavior and extractable packaging. It cannot honestly satisfy the user's full requirement for rigorously demonstrated live Claude research performance in this environment. The final quality gate lists these as unresolved qualifications, while delivering the functioning local repository and the concrete next validation protocol.

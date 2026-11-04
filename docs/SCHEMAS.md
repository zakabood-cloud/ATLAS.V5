# ATLAS project and artifact contracts

The Python implementation is authoritative. Project JSON is UTF-8, strict (no duplicate keys or nonfinite numbers), and stored under `projects/<id>/`. Artifacts and user attestations are not authenticated facts; hashes detect byte changes, not truth.

## State and stage order

New projects use state schema 2 and advance sequentially:

`INTAKE -> MANDATE -> ENABLEMENT -> META -> READINESS -> ORCHESTRATE -> RESEARCH -> VERIFY -> SYNTHESIS -> DELIVER -> MEMORY -> EVALUATE -> COMPLETE`

Schema 1 remains readable with its legacy order, which excludes ENABLEMENT. Migration is explicit and backed up; it reopens at MANDATE (or stays INTAKE), preserves old files without recertifying them, and requires new approvals and review.

## Intake, enablement and access

`mandate.json` is generated from recorded answers and acknowledged assumptions. It must state the inquiry, domain, user-ended interview, assumptions, deliverable and nonnegative paid budget. A local budget declaration does not replace actual spending authorization.

`enablement.json` (schema version 1) records the current question, observed environment and discovery limits, and a `features` list. Include all standard IDs: `subagents`, `model_selection`, `mcp`, `web_access`, `repository_access`, `execution`, `file_access`, and `customizations`; add other topic-relevant features discovered. Each row has `id`, `name`, `status` (`enabled|disabled|unavailable|unknown`), boolean `needed`, `basis`, `controlled_by` (`user|administrator|plan|platform|unknown`), `enablement_steps`, `cost`, `privacy`, and `quality_impact`. Do not infer hidden platform state. For `enabled`, provide `verification: {artifact, sha256}` pointing to a receipt with matching `feature_id`, `status: enabled`, `observed_at`, `expires_at`, `method`, and `limitations`. The receipt must be current and truthful.

`enablement-approve` records actual user choices for every feature:

- `use`: only when the feature is observed enabled.
- `enable`: request an actual change through supported user/admin controls; it blocks readiness until re-observed, unless the user later accepts a limitation.
- `accept_limit`: explicit acceptance of a needed feature limitation.
- `not_needed`: only when the feature is not needed for this work.

The file cannot toggle settings, override administrator controls, grant permissions, or buy subscriptions.

`access_plan.json` also uses schema version 1. It is inquiry-specific and required before META:

```json
{
  "schema_version": 1,
  "question": "Exact current inquiry",
  "coverage": ["primary_sources", "verification"],
  "selection_reason": "Compare existing tools with the incremental value of the proposed capability.",
  "needs": [{
    "id": "local-analysis",
    "name": "Local analysis",
    "kind": "local",
    "required": true,
    "paid": false,
    "purpose": "Reproduce calculations on approved project files",
    "endpoint": "local:approved-project",
    "coverage": ["verification"],
    "permissions": ["read project files"],
    "data_shared": "No external transfer",
    "privacy": "Local",
    "cost": "No external charge",
    "alternatives": "Manual calculation",
    "quality_impact": "Without reproduction, numeric conclusions remain unchecked"
  }]
}
```

Every need has the shown fields and `kind` is `mcp|builtin|local|manual`. Each coverage dimension must be covered. MCP needs also declare `publisher`, `verification_url` (official public HTTPS), and actual `publisher_verified_at`. Endpoints must not contain credentials, query strings or fragments. The example is illustrative, not a connected service or user approval.

`access-approve` requires a decision for every need: `use` or `defer`, a reason, and for `defer` a quality impact. Paid `use` also needs separate `paid_approved: true` from actual spending authorization. Every used capability requires an observed, benign read-only test after approval. `access-test` accepts an operator-supplied receipt with `ok: true`, exact approved `resource` and `operation`, `observed_at`, future `expires_at`, and `limitations`; it does not make the external call or authenticate the result.

Any blocked access creates a global hold. For a planned need, a retry receipt must go through `access-test`. For an external Copilot tool without a planned `need_id`, `access-resolve` records a matching `{ok:true,resource,operation,observed_at,method,limitations}` observation after an explicitly authorized retry. It binds a hash, but is still operator evidence. Every block in the current hold must be resolved before ordinary work resumes. See [ACCESS.md](ACCESS.md).

## Preparation and protocol

`dossier.json` has substantive `selection_reason`, `risks`, `limitations`, `expertise`, `tool_comparison`, at least two `methods_compared`, nonempty `method_sources` (`url`, `finding`, `accessed_at`), and a `pilot` result or exact access limitation. Do not invent a successful pilot.

New-project `protocol.json` uses schema version 2 and contains:

- unique nonempty `coverage` dimensions and nonempty `methods`, `evaluation_criteria`;
- nonempty `freshness_policy`, `uncertainty_policy`, `synthesis_method`, and `bias_controls`;
- a `search_plan` with unique IDs, query, coverage `dimension`, strategy `primary|counterevidence|background|replication`, and approved `access_need_id`; each dimension needs both primary and counterevidence searches;
- `stopping_criteria`: positive integers `max_queries` (at most 10,000), `min_sources_per_dimension` and `min_independent_origins` (at most 1,000 each), `consecutive_no_new` (at most 1,000); max queries must cover the plan;
- nonempty `inclusion`, `exclusion`, `verification`, `stopping_rule`, and `amendment_policy`; integer `meta_iterations` from 1 to 3.

`readiness.json` records `decision: ready|limited`, limitations, and `checks` for methods, evidence, tools, computation, budget, verification and permissions. Every check has `status: passed|limited` and `basis`; `limited` needs a `fallback`. Optional capability observations are not proof of actual provider access unless the corresponding read-only test is observed.

## Orchestration and search accounting

`plan.json` has `architecture_reason`, `model_policy`, and `tasks`. Each task has a unique safe ID, `objective`, `owner`, `evidence_required`, and `depends_on` list. Optional `write_paths`, `exclusive_resources`, and `access_need_ids` define coordination boundaries; these are declarations, not sandbox controls. Access IDs must have approved `use` decisions. The dependency graph must be acyclic. Dispatch with more than one worker requires the current subagents feature to be observed enabled and explicitly approved `use`; otherwise use one worker. Dispatch planning never launches workers.

Actual task output is schema-2 JSON with matching `task_id`, `summary`, `source_ids`, `limitations`, `unresolved`, and `execution` containing `executor`, `kind` (`research|local-code|synthetic`), `model_selection`, `model_identity`, `observed_at`, and observed `tools`. Report hidden model identity as `not exposed`; role labels do not establish identity. The fixture worker is synthetic only.

`search_log.json` records each query with unique `id`, `plan_id`, exact `query`, `tool`, `at`, `outcome`, `status: complete|blocked`, `retrieved_ids`, `included_ids`, and `exclusions` (`id`, `reason`). Every retrieved item is included or explicitly excluded exactly once. A blocked query points to `access_block_id` and is eligible only after the user accepts that gap. Each bundled scholarly-search attempt is bound to a state `retrieval_receipt` and persisted `retrieval/<id>.json` request/result-or-error artifact. For every substantive RESEARCH attempt, link that artifact in a search-log row with the identical query and `plan_id`; the VERIFY gate rejects unlogged attempts, whether successful or failed. Preparation probes are separately recorded, but are not substantive coverage and need not appear as research searches. Do not convert a failed search into a negative finding.

The Crossref/OpenAlex adapters are preflight-only when invoked with `--probe --limit 1` and no cursor in ENABLEMENT, META, READINESS or ORCHESTRATE. A substantive request is allowed only in RESEARCH and must use `--plan-id` whose accepted `search_plan` row matches the exact query and access need. `--live` is necessary but never sufficient authorization. Probes do not replace research and adapter results remain metadata rather than full text.

`coverage.json` has one `items` row per protocol dimension: `dimension`, `status: covered|gap`, `basis`, referenced `search_ids`, `source_ids`, and for gaps `decision_impact`; it also records `stopping_decision`, `stopping_reason`, and any required authorization. A covered dimension must meet the predeclared source and independent-origin minima. Stopping reason is `plan_complete`, `saturation` (all planned searches plus the no-new-source window), or user-authorized `authorized_limit`. These checks measure recorded accounting, not exhaustive recall or quality.

## Evidence and reviews

`evidence.json` schema 2 is `{schema_version:2,sources:[],claims:[],assessments:[],calculations:[]}`. Schema 1 is legacy and must be upgraded and re-reviewed before a schema-2 synthesis.

- Sources require `id,url,title,accessed_at,origin_group,snapshot,sha256`; local sources use `source_type: local`, a `local:` URL, and `provenance_note`. The snapshot is a bounded UTF-8 text file under the project. Hashes do not prove source authenticity.
- Claims require `id,text,kind,material,source_ids,author,scope,uncertainty`. Uncertainty has `level: low|medium|high|unknown`, a basis, and explicit limitations. Numeric claims need a decimal `numeric_value` and `units`. Derived numeric claims bind to reproduced calculation output; directly reported statistics must be marked `reported_statistic: true`.
- Assessments require the source, exact excerpt, locator, verdict, reasoning, reviewer and timestamp. A schema-2 assessment binds `claim_sha256` to the complete current claim and `snapshot_sha256` to its source. A material claim needs an independent supporting assessment; a contradiction needs explicit resolution.
- Calculations reference hashed JSON from `atlas quant` and bind output JSON pointers, numeric values and units to claims.

`review.json` for synthesis requires author/reviewer, non-self independent review, counterarguments, uncertainty, coverage and numeric reviews, limitations, `decision: pass|conditional`, and no unresolved critical issues. Schema 2 also binds `evidence_sha256` to the current complete evidence object, enumerates every material `reviewed_claim_id`, and records `model_identity` or `not exposed`. Review hashes do not prove a semantic judgment or actual independence.

`review-packet` verifies snapshots and includes quote-centered context and omitted ranges. Review the full source where needed. `report-audit` checks `[[claim:ID]]` markers, required material-claim coverage and some likely uncited factual lines. Passing is mechanical citation coverage, not semantic entailment.

## Synthesis, delivery and evaluation

`synthesis.json` requires conclusion, tradeoffs, uncertainty, failure conditions, strongest counterargument and known `claim_ids`.

`deliverables.json` has `contract_review` and nonempty files with project-relative `path`, `sha256`, `format_review`, `citation_review`, and `kind: report|artifact`. Reports include claim IDs and use `[[claim:ID]]` markers; non-Markdown/text reports also point to a hashed audit-text artifact. Every material claim must appear in an audited report. Rendering and substantive format review remain human/operator work.

`lessons.json` has `outcome` and a `proposals` list (possibly empty). `evaluation.json` has nonempty `criteria,results,failures,limitations,next_actions`; criteria must exactly match the accepted protocol, and `research_quality_proven` must be `false`.

See [USAGE.md](USAGE.md) for commands, [ACCESS.md](ACCESS.md) for approvals and recovery, and [MIGRATION.md](MIGRATION.md) for schema-1 projects.

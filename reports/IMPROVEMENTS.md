# Prioritized improvement register and traceability

All improvements below are implemented in this release unless a limit is explicitly stated. Expected research-quality impact is a reasoned hypothesis, not a measured causal gain. Local check results are in [TESTING.md](TESTING.md), source IDs resolve in [the source register](../research/SOURCES.md), and every original file maps through [the audit matrix](original_audit_matrix.csv).

Machine-readable [CSV](improvement_register.csv) and [JSON](improvement_register.json) include affected original files, implementation, evidence, tests, complexity and security/feasibility limits.

## I01 · P0 · Declared stage can be arbitrary or skipped

- **Original:** research_os/operations/STATE_MACHINE.md; research_os/engine/audit_project.py
- **Justification:** Original arbitrary_stage accepted; transactional/gated design rationale
- **Implemented in:** atlas/project.py; atlas/__main__.py
- **Verification:** StateTests.test_cannot_skip_intake; StateTests.test_unknown_state; StateTests.test_atomic_failure_keeps_stage
- **Expected effect:** Prevents unsupported local completion and preserves failed-gate state
- **Complexity:** Medium
- **Boundary:** Local engine feasible; does not constrain actions outside CLI

## I02 · P0 · Initialization is a prompt contract without an executable stop

- **Original:** CLAUDE.md; START_HERE.txt; research_os/engine/verify_install.py
- **Justification:** User lifecycle contract; CC01/CC02
- **Implemented in:** CLAUDE.md; atlas init; atlas-init skill
- **Verification:** ReleaseStructure.test_initialization_exact_message_and_stop; ReleaseStructure.test_failed_initialization_has_no_ready
- **Expected effect:** Correct local readiness and no premature topic creation
- **Complexity:** Low
- **Boundary:** CLI tested; actual Claude stop/invocation unverified

## I03 · P0 · Interview answers and consequential assumptions unenforced

- **Original:** research-intake skill; QUESTION_BANK.md; PROJECT_SCHEMAS.md
- **Justification:** Original intake principles retained; mandatory user requirements
- **Implemented in:** atlas/intake.py; atlas/project.py; methods/INTAKE.md; domains.json
- **Verification:** StateTests.test_partial_intake_persists; test_explicit_end_with_assumptions; test_adaptive_question_persistence; Boundaries.test_domain_specific_methods_and_deliverables
- **Expected effect:** Preserves partial answers, mandatory deliverables and explicit end assumptions
- **Complexity:** Medium
- **Boundary:** Storage/gates feasible; relevance and conflicts require conversation review

## I04 · P0 · Methodology readiness only in prose

- **Original:** research-meta skill; STATE_MACHINE.md; QUALITY_GATES.md
- **Justification:** ME01–ME07; pilot/feasibility design inference
- **Implemented in:** META/READINESS gates; atlas-meta skill; RESEARCH_PROTOCOL.md
- **Verification:** StateTests.test_meta_required; IntegrityRegressions.test_evaluation_criteria_required_before_research
- **Expected effect:** Forces documented alternative methods, pilot, coverage and bounded preparation before research
- **Complexity:** Medium
- **Boundary:** Records checked; quality and actual external method searches remain reviewer judgments

## I05 · P0 · Self-attested V2 can substitute for source support

- **Original:** audit_project.py; CLAIM_AND_DATA_STANDARDS.md
- **Justification:** Original fabricated_source_self_attested_v2 accepted; EV04–EV09
- **Implemented in:** atlas/evidence.py; methods/VERIFICATION.md
- **Verification:** EvidenceTests.test_fabricated_source_domain; test_excerpt_not_support_label; test_no_source_on_material_claim; test_self_review
- **Expected effect:** Blocks several concrete provenance failures and requires review records
- **Complexity:** High
- **Boundary:** No automatic entailment/authenticity proof; distinct IDs are not authenticated people

## I06 · P0 · Numerical narratives lack executable reproduction and claim binding

- **Original:** DECISION_AND_STATISTICS.md; quantitative-analyst.md
- **Justification:** Explicit input/calculation provenance; ME05–ME07; baseline lacks calculators
- **Implemented in:** atlas/quant.py; evidence calculation bindings; examples/
- **Verification:** QuantTests; NumericalProvenance.test_correct_calculation_wrong_claim; test_altered_calculation_with_new_hash; test_same_forged_units_rejected
- **Expected effect:** Reproduces six model types and prevents unrelated result/unit substitution
- **Complexity:** Medium
- **Boundary:** Assumptions remain unvalidated; no universal statistics/financial platform

## I07 · P0 · Accepted evidence/output changes can go unnoticed

- **Original:** STATE_MACHINE.md; PROJECT_SCHEMAS.md
- **Justification:** Original existence checks; SE03/SE04
- **Implemented in:** Stage seals; exact snapshot hashes; deliverable checks
- **Verification:** StateTests.test_snapshot_tampering_after_review; test_completed_output_empty_rejected; IntegrityRegressions.test_reopen_does_not_hide_altered_task_output
- **Expected effect:** Detects altered accepted artifacts and empty deliverables
- **Complexity:** Medium
- **Boundary:** Detects accidents, not malicious rewrite of both content and receipts

## I08 · P0 · No durable transactional state or verified recovery

- **Original:** STATE_MACHINE.md; research_os/state/.gitignore
- **Justification:** SE03/SE04 official database behavior
- **Implemented in:** SQLite events, state/ledger digests, checkpoint and restore
- **Verification:** StateTests.test_corrupt_database_recovery; test_changed_checkpoint_rejected; test_event_chain_tampering; IntegrityRegressions.test_task_ledger_tamper_detected
- **Expected effect:** Recoverable local workflow and visible corruption failures
- **Complexity:** Medium
- **Boundary:** Database backup only; no power-failure proof or distributed recovery

## I09 · P0 · Tool candidate status may imply working access

- **Original:** TOOL_AND_SOURCE_INTELLIGENCE.md; tool-mcp-architect.md
- **Justification:** CC07; provider docs ML/DA register
- **Implemented in:** atlas/integrations.py; config/integrations.json; docs/INTEGRATIONS.md
- **Verification:** Boundaries.test_configuration_not_authentication; test_fake_tested_capability_rejected; test_expired_capability; IntegrityRegressions.test_unavailable_api_without_fallback_blocks
- **Expected effect:** Separates discovery/config/auth/test and expires observations
- **Complexity:** Low
- **Boundary:** Offline introspection and contract tested; no live provider adapter

## I10 · P0 · Inherited tools and agent memory expand privileges

- **Original:** All original agents; SECURITY_AND_PERMISSIONS.md
- **Justification:** CC02/CC03/CC08/CC11; SE01/SE02
- **Implemented in:** Explicit agent tools; no reviewer memory; no skill grants or hooks
- **Verification:** ReleaseStructure.test_shipped_structure; metadata checks; path/symlink and inert-source tests
- **Expected effect:** Reduces avoidable privilege and installation exposure
- **Complexity:** Low
- **Boundary:** Static documented restrictions; real prompt injection and client enforcement unverified

## I11 · P1 · Duplicated master and conflicting bootstrap routes

- **Original:** ULTIMATE_CLAUDE_RESEARCH_OS_MASTER.md; CLAUDE.md; README.md
- **Justification:** 36 byte-identical embedded payloads; CC01/CC02
- **Implemented in:** Concise CLAUDE; six stage skills; one /atlas-init entry; master archival only
- **Verification:** master_payload_comparison.json; local link checks; stage skill invocation regression
- **Expected effect:** Removes duplicate instruction authority and simplifies maintenance
- **Complexity:** Low
- **Boundary:** Context efficiency inferred; token savings not measured

## I12 · P1 · Multi-agent roles lack executable dependencies or output ledger

- **Original:** ORCHESTRATION_AND_SEARCH.md; eight original agents
- **Justification:** AR01/AR02 task-dependent coordination; framework comparison AR03–AR06
- **Implemented in:** Five agents; task DAG/attempts/outputs; coordinator-only writes
- **Verification:** StateTests.test_cycle_rejected; test_task_retry_limit; test_tasks_need_actual_output; IntegrityRegressions.test_dependencies_block_early_task
- **Expected effect:** Prevents premature dependencies and false task completion without forcing agent proliferation
- **Complexity:** Medium
- **Boundary:** No scheduler/workload balancing or measured research gains

## I13 · P1 · Domain guidance not executable as profiles

- **Original:** DOMAIN_PLAYBOOKS.md; QUESTION_BANK.md
- **Justification:** Domain-specific ME/DA references and inquiry requirements
- **Implemented in:** methods/domains.json; eight benchmark cases
- **Verification:** Boundaries.test_domain_specific_methods_and_deliverables; IntegrityRegressions.test_all_eight_domain_plans_enter_research
- **Expected effect:** Changes intake/coverage by domain and provides specific future live rubrics
- **Complexity:** Low
- **Boundary:** Profile selection/inquiries tested locally; actual method choice unverified

## I14 · P1 · Coverage and contradictory evidence may remain informal

- **Original:** QUALITY_GATES.md; CLAIM_AND_DATA_STANDARDS.md
- **Justification:** ME03; EV05/EV06 source completeness and counterevidence
- **Implemented in:** Coverage exact dimensions; gap impact; contradiction resolution; freshness review
- **Verification:** EvidenceTests.test_contradiction_requires_resolution; test_duplicate_origins; IntegrityRegressions.test_stale_source_needs_explicit_resolution
- **Expected effect:** Prevents silently dropping planned dimensions or unresolved recorded contradictions
- **Complexity:** Medium
- **Boundary:** Cannot detect omitted evidence or all derivative sources automatically

## I15 · P1 · Memory policy lacks version/expiry/promotion mechanisms

- **Original:** MEMORY_POLICY.md; METHODS_INDEX.md; research-memory skill
- **Justification:** Original separation principles retained; controlled improvement rationale
- **Implemented in:** atlas/memory.py; memory/README.md
- **Verification:** Boundaries.test_memory_rejects_topic_conclusion; test_memory_version_expiry_and_search
- **Expected effect:** Makes method-memory promotion explicit, scoped, versioned and expiring
- **Complexity:** Low
- **Boundary:** Receipt quality/identity require real independent review; no semantic retrieval benchmark

## I16 · P1 · Costs are instructions without a local ledger

- **Original:** ORCHESTRATION_AND_SEARCH.md; TOOL_AND_SOURCE_INTELLIGENCE.md
- **Justification:** User no-paid-action requirement; CC12
- **Implemented in:** Sealed mandate budget; idempotent costs; zero default
- **Verification:** StateTests.test_zero_budget_fails_closed; test_cost_idempotency; IntegrityRegressions.test_cost_cannot_use_altered_mandate; test_cost_ledger_tamper_detected
- **Expected effect:** Rejects unauthorized declared spending and repeated altered cost keys
- **Complexity:** Low
- **Boundary:** Cannot intercept external billing; no paid calls made

## I17 · P1 · Pause/block/cancellation may be lost on resumption

- **Original:** STATE_MACHINE.md
- **Justification:** Original additional states retained as persisted holds
- **Implemented in:** hold/resume commands and CLAUDE contract
- **Verification:** IntegrityRegressions.test_hold_blocks_work_and_persists; test_aborted_project_requires_explicit_resume
- **Expected effect:** Prevents local continuation through a recorded stop
- **Complexity:** Low
- **Boundary:** Must separately cancel remote/client jobs; authorization is operator supplied

## I18 · P1 · Evaluation plan has no runner and can be selected after results

- **Original:** EVALUATION_PROTOCOL.md
- **Justification:** EV01–EV10 measurement limitations; user predefined metrics requirement
- **Implemented in:** Protocol evaluation_criteria; exact final criteria; tests; paired controls; benchmarks/PROTOCOL.md
- **Verification:** IntegrityRegressions.test_evaluation_cannot_change_predefined_criteria; scripts/validate_release.py; scripts/benchmark_controls.py
- **Expected effect:** Makes local findings reproducible and preserves unmeasured research uncertainty
- **Complexity:** Medium
- **Boundary:** Blinded research trials remain not run; no fabricated performance score

## I19 · P1 · Installer checks fences/size but not syntax or references

- **Original:** verify_install.py; EVALUATION_PROTOCOL.md
- **Justification:** Actual malformed_yaml/invalid_python baseline failures; CC02/CC03
- **Implemented in:** atlas/structure.py
- **Verification:** ReleaseStructure.test_invalid_frontmatter_detected; test_bad_python_detected; test_missing_local_link_detected
- **Expected effect:** Detects invalid shipped metadata, syntax and missing internal targets
- **Complexity:** Low
- **Boundary:** Restricted YAML subset; not full Claude parser or semantic policy analysis

## I20 · P1 · No independent extractability/completeness release gate

- **Original:** README.md; START_HERE.txt
- **Justification:** User final release requirements
- **Implemented in:** scripts/validate_release.py; release manifest; package/extraction receipts
- **Verification:** Final archive extraction, manifest equality, check, unittest and demo receipts
- **Expected effect:** Ensures complete downloadable project and original reference integrity
- **Complexity:** Low
- **Boundary:** Cloud/runtime/provider behavior outside local package remains unverified


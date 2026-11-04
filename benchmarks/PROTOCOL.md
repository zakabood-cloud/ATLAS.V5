# Evaluation protocol: controls versus real research

The local suite measures deterministic controls. The eight cases in `cases.json` are specified but **have not been executed as live model research**. Synthetic fixtures are labeled and must never be presented as business/scientific findings. No model/provider leaderboard is produced by this repository.

## Predefine a fair research trial

1. Freeze the original supplied ZIP and upgraded release hashes. Use isolated project copies so the original master cannot contaminate upgraded instructions. Record Copilot client/surface, visible model selection, actual model only if exposed, tool configuration and source access.
2. Convert each case into a specific inquiry with a scripted user profile, essential/optional answers and a chosen deliverable contract. Include partial answers, conflicting constraints, a user-ended interview and a missing-tool case. Keep these answers identical across systems. The interview itself remains under evaluation.
3. Give both systems the same authorized resources, time/cost ceiling and source access. Preserve query timestamps; use a frozen corpus when testing retrieval/attribution separately from live coverage. Log actual resource use rather than assuming equal agent count equals equal cost.
4. Before either output is reviewed, define material atomic claims, coverage dimensions, numerical known answers where possible, exclusion decisions and unacceptable failure conditions. Hold out cases and include variations to reduce prompt fitting. Do not use this release's synthetic training fixtures as the research-quality test set.
5. Randomize output order and anonymize system names. Two competent reviewers independently assess the same units, blinded where feasible. Adjudicate disagreements against original sources. Record judgments, rationales, disagreements and corrections. An LLM judge may help triage but is not independent ground truth.
6. Report per-case results and paired differences with uncertainty appropriate to the small sample. Do not manufacture significance from eight heterogeneous tasks. Replicate where stochastic variability matters and report failures and incomplete outputs as outcomes.

## Metrics, denominators and limits

| Metric | Measurement |
|---|---|
| Factual support | Supported factual claims / audited factual claims, with materiality and access gaps reported separately |
| Citation support | Claim-citation pairs that directly support exact wording / audited pairs; also measure uncited material claims |
| Evidence quality | Domain-specific risk-of-bias/directness/freshness assessment, not a universal numerical source-brand score |
| Coverage | Completed predefined decision dimensions / all required dimensions; report consequential missing dimensions explicitly |
| Arithmetic | Reproduced consequential calculations / required calculations, plus matching units and input provenance |
| Methods | Blinded rubric on question fit, search/selection, bias control, domain methods and stopping |
| Calibration | Only where forecasts/probabilities and later outcomes exist; Brier/log scores or interval coverage with a defined sample; otherwise unmeasured |
| Reliability | Failed/retried/duplicated jobs, recoverability, missing artifacts and interruption behavior |
| Efficiency | Actual model/tool cost, latency, query counts and reviewer time under equal resource rules |
| Decision utility | Qualified review of options, downside, reversal conditions and actionable next evidence; validate against later real outcomes where possible |

No single weighted total is the default. It can hide a fatal unsupported claim behind excellent formatting. Any composite needs declared weights and sensitivity before scoring.

## Interaction and adversarial scenarios

Fresh opening must initialize, emit the exact readiness sentence and stop. The next inquiry must trigger clarification, ask desired deliverables and avoid any topic/meta research before the interview ends. Partial answers persist; conflicts are surfaced; consequential assumptions are shown; missing authorization is requested specifically. Resume must consult artifacts, not invent prior completion.

Inject fabricated/reserved-domain citations, actual URLs with mismatched claims, stale evidence, derivative sources, incompatible statistics, unsupported financial assumptions, wrong arithmetic, unavailable MCP/API, missing credentials, malicious source instructions and corrupt state. A real prompt-injection test needs an actual model with a canary and constrained tool surface; the local test showing source text is inert to Python is not that test. An actual URL plus a matching quote can still fail semantic support, so both model-facing and independent human evaluation are required.

## Model-routing comparison

When evaluating Copilot model routing, use the cloud-agent **Auto** selection as a distinct system condition, not as a claim about a fixed model. Compare it with explicitly selected models only when those models are available to the same account and the comparison is authorized. Hold inquiry, user answers, tools, source access, time, and cost limits constant; randomize and blind outputs for review. Record the Copilot surface, selection shown at task start, actual routed model only if exposed, reasoning setting if shown, failures, latency, resource use, and reviewer time. Repeat held-out tasks where feasible. If the routed model is hidden or the picker is unavailable, record that limitation; do not infer it or claim a task-specific model switch occurred. Report factual support, citation support, coverage, arithmetic, calibration where outcomes exist, and failures separately rather than collapsing them into a single score. No such live comparison is claimed by this release.

## Local paired comparison

Run `python3 scripts/benchmark_controls.py` after structural checks pass. It extracts the immutable original into a temporary directory and compares selected checker defects against equivalent upgraded inputs. This is an intentionally adversarial engineering regression set, not a representative estimate of factual accuracy. Baseline and upgraded artifact formats differ; the intended defect, resource environment and expected behavior are held constant and recorded. Both systems' inability to detect meaningless but syntactically valid prose is retained as a limitation.

## Release gate

Run `python3 scripts/validate_release.py`. Required local criteria: structure pass; all unit/integration tests pass; synthetic lifecycle COMPLETE; original hashes all match; paired controls behave as expected. Then package, independently extract, verify the release manifest and rerun checks/tests/demo. Live Copilot and API verification, expert independent post-implementation audit and blinded research superiority remain unresolved release qualifications rather than fabricated green checks.

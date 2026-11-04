# ATLAS 3.0 release changes relative to v2.0

## Added functional modules

`atlas/retrieval.py`, `atlas/methodology.py`, `atlas/adapters.py`, `atlas/verification.py`, `atlas/sourcegraph.py`, `atlas/budget.py`, `atlas/scheduler.py`, `atlas/decision.py`, `atlas/evaluation.py`, `atlas/memory_search.py`.

## Existing components amended

- `atlas/__main__.py`: commands for safe discovery, evidence/report review, budgets, worker dispatch, benchmarking and local lexical search.
- `atlas/quant.py`: three additional executable model kinds, preserving old calculators.
- `atlas/project.py`: explicitly justified noncritical blocked/skipped terminal states, while retaining critical gates.
- `atlas/structure.py`: permits only the reviewed, narrowly scoped local hook.
- `.claude/settings.json`: conservative PreToolUse Bash guard (not a sandbox).
- `CLAUDE.md` and skills: use meta-research, tool discovery, independent source tracing and evaluation gates.
- `.claude/agents`: source-intelligence researcher and tool-integration architect.

## Preserved

- Original v2 research engine, 100 regression tests, archived original prototype, previous audit/reports, baseline research protocols.

## Explicit nonclaims

This release has **not** connected paid research engines, demonstrated live Claude Code agents, established semantic entailment, or won independently scored research benchmarks. See docs/IMPLEMENTATION_STATUS.md and docs/UPGRADE_MATRIX_106.csv.


Additional modules: `atlas/ingest.py`, `atlas/project_archive.py`, `atlas/experiment.py`; new optional ingestion and backup CLI commands, explicit correlation-matrix support, binary EVSI model and new integration tests.

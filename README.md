# ATLAS Research OS 5.0 — portable research controls for Copilot and Claude Code

**An auditable research toolkit**, with adaptive intake, topic-specific access approval, risk-based failure handling, structured search and evidence contracts, reproducible calculations, and Copilot coordination guidance.

This is a **bounded engineering toolkit**, not proof of superior decisions, exhaustive discovery, or factual accuracy. Python validates local contracts; the actual Copilot client, authorized tools, and qualified reviewers perform research. Repository instructions do not authenticate tools, enforce a sandbox, or prove model independence.

## First use with Copilot

Add the contents of this folder to the repository where you want ATLAS available. Open that repository in a GitHub Copilot surface that supports repository instructions and agent skills. Then ask:

> Initialize ATLAS according to `AGENTS.md`, run `python3 -m atlas init`, report verified readiness, and stop. Do not research or interview me yet.

On the next turn, provide your inquiry. Copilot first clarifies your objective, constraints, and **desired deliverables**. After mandate acceptance it inventories observable Copilot features, then analyzes topic-specific access needs, compares available tools with useful MCP/built-in/local alternatives, and **asks you to approve before META or substantive research**. Every used capability needs an observed approved test; configuration alone is insufficient. **Critical or security blocks pause affected decisions; optional-source failures are recorded without automatically stopping unrelated authorized work.**

New in v5: [upgrade overview and capability status](docs/ATLAS5.md), [environment and session guidance](docs/SESSION_ENVIRONMENTS.md). Start with [quickstart](docs/QUICKSTART.md), [access and stop/resume](docs/ACCESS.md), [usage](docs/USAGE.md), and [artifact contracts](docs/SCHEMAS.md). Existing projects need the [migration guide](docs/MIGRATION.md); installing v4 does not certify v3 evidence under the new contracts.

For GitHub.com, use native Auto at task start where available, otherwise the client default. See [Copilot integration](docs/COPILOT.md) and [model routing](docs/MODEL_ROUTING.md). Independent branches can use actual available subagents with disjoint outputs; small/tightly coupled work defaults to one researcher.

## Local checks

```sh
python3 -m atlas check
python3 -m unittest discover -s tests -q
python3 scripts/demo.py        # synthetic only
```

## Included capabilities

- State-schema-2 feature enablement and topic-specific access approvals, expiring observation receipts, and durable project-wide access holds.
- Structured primary/counterevidence search plans, source inclusion/exclusion accounting, coverage thresholds, and explicit stopping decisions.
- Claim scope and uncertainty, revision-bound review, full-snapshot hash checks, contextual review packets, and citation/omission checks including bullets and tables.
- Conservative source-lineage diagnostics, local BM25 retrieval, and hard-threshold methodology scoring.
- A task DAG, read-only dispatch recommendations, and structured execution handoffs. The bundled worker remains a **synthetic fixture**, not a real agent launcher.
- Ten executable quantitative examples, versioned reproduction, unit bindings, and explicit model assumptions.
- Exact-label, binary Brier, paired, and frozen-corpus retrieval evaluation with denominator and sampling caveats.
- Bounded ingestion, reviewed method memory, local budget accounting, and quiesced whole-project backup/migration.
- Two read-only bibliographic adapters (Crossref/OpenAlex), requiring project-specific approval and explicit live opt-in; metadata is not full text.

The supplied v3 ZIP, original prototype, and earlier reports remain historical baselines, not v5 validation receipts. **No live provider tests, hidden-model observation, paid integration, or demonstrated research superiority is claimed.** See the [v4 upgrade report](reports/V4_UPGRADE.md), [current testing record](reports/TESTING.md), [evaluation protocol](benchmarks/PROTOCOL.md), [security](docs/SECURITY.md), and [remaining validation work](docs/UPGRADE_ROADMAP.md).

## Platform and duration

ATLAS runs as a local, standard-library Python core with separate Copilot (`.github/`) and Claude Code (`.claude/`) instruction adapters. Modern Copilot sandbox sessions have no universal 59-minute execution cap; older Actions-based cloud-agent tasks may. ATLAS never imposes a time-based cutoff and offers resumable handoffs. Verify the actual environment before claiming any runtime capability.

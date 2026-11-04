# ATLAS Research OS 5.0 — Release design and measured capability boundary

ATLAS 5.0 builds on supplied Copilot v4.0.0 using a portable Python core with Copilot and Claude Code adapters. The system preserves **ready-and-stop → user inquiry → adaptive intake and deliverables → mandatory meta-research → readiness → research → verification → deliverables → reviewed memory**.

## Implemented local capabilities

- SQLite state and research-stage gates, dependency task graph, persistent audit events, checkpoints, controlled holds and recovery.
- Separate Copilot `.github/` and Claude Code `.claude/` instructions, skills and specialist agent prompts; actual agents run only when their respective clients expose working tools.
- Evidence integrity and source-origin checks, bounded lexical claim/context diagnostics, atomic report marker auditing, structured qualitative reviewer packets. These do **not** establish semantic truth automatically.
- Opt-in, approval- and budget-gated OpenAI/Gemini research requests, plus guarded Crossref/OpenAlex metadata discovery when available. External calls are **not live-tested**, and provider output is unverified until inspected against original sources.
- Local retrieval scoring and expansion, methodology scoring, budget reservation, financial-input provenance, quantitative analysis, research memory retrieval, source-group diagnostics, test benchmark scoring, read-only task dispatch advice and synthetic scheduler.
- Project backup and resumable handoff snapshots; no fixed session time cutoff.

## Not established

- Authenticated GitHub Copilot cloud/CLI/IDE and Claude Code execution and real task delegation in this release environment.
- Genuine multi-model autonomous research at commercial scale; paid databases, private SaaS accounts and MCP servers need user-controlled connections and approved API budgets.
- Reliable semantic evidence entailment or fact-checking solely through local lexical tools; independent reviewer remains required.
- Superiority to other research agents on a held-out live commercial/research benchmark.

## Priority for next operational validation

1. Load in your active Copilot surface, run `python3 -m atlas init`, ensure the correct ready/stop behavior, and confirm actual tools/delegation.
2. Run one complete topic from inquiry through final report with source-level independent review and compare against a simpler deep-research baseline.
3. Connect only approved external providers, test each with a harmless query, record raw response and costs, and validate that user permissions and rate limits are respected.
4. Repeat in Claude Code and record differences in actual agent/tool support. Do not infer runtime support from static file structure.

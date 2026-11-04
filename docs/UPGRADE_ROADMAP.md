# ATLAS upgrade roadmap

This roadmap separates changes that can be delivered in repository files from capabilities that require a live GitHub Copilot account, independently reviewed research, or authorized external services. It is not a forecast of research quality.

## Completed in this upgrade

- Documented GitHub Copilot cloud-agent **Auto** as the default model-routing policy where the task-start picker is available.
- Kept ATLAS custom-agent profiles free of pinned model overrides and clarified that agent roles do not establish model identity or independent review.
- Required task-level reporting of the visible selection and an explicit `not exposed` when the actual routed model cannot be observed.
- Added a blinded, equal-resource model-routing comparison to the evaluation protocol.

## Priorities

| Priority | Work | Why it remains | Exit evidence |
|---|---|---|---|
| P0 | Run a live GitHub.com Copilot smoke test for instruction/skill discovery, custom-agent availability, Auto selection, and task/model observability. | Repository checks cannot execute or inspect a Copilot cloud session; surface, plan, and administrator policies differ. | Dated session record with the entry point, visible selection, exposed capabilities, failures, and explicit unknowns. Do not claim hidden routing identities. |
| P1 | Compare Auto with available fixed-model conditions on held-out, domain-diverse inquiries. | No live benchmark establishes whether Auto improves ATLAS research or how variable its routing is. | Follow `benchmarks/PROTOCOL.md`: equal tools and resource limits, blinded reviewers, claim/citation and coverage measures, failures, costs/latency, and uncertainty. |
| P1 | Validate the semantic evidence-review workflow with qualified reviewers. | Local gates validate structure, excerpts, and attestations, but cannot prove entailment, reviewer independence, or accurate conclusions. | Independent claim-level review against original sources, adjudicated disagreements, and recorded reviewer scope; no identity-string-only assurance. |
| P1 | Test the actual repository/organization tool and MCP permission boundary used for research. | Instructions and custom-agent profiles do not grant, restrict, or sandbox client permissions. | Administrator-reviewed least-privilege configuration, privacy/retention assessment, and an authorized read-only pilot with observed results. |
| P2 | Add domain-specific live data adapters only for recurring, decision-relevant gaps. | Provider access, price, licensing, geography, and quotas cannot be inferred from local code or account settings. | Approved source/tool comparison, documented limits and provenance, explicit spending authorization where applicable, bounded pilot, and tests for failures and fallback. |
| P2 | Improve specialist retrieval/verification where a validated project needs it: multilingual and geographic coverage, correction/retraction tracking, visual PDF/chart inspection, and reference-class forecasting. | These are domain- and data-dependent gaps; generic automation may create false confidence. | Scoped benchmark with suitable source/outcome ground truth, expert review, documented access limits, and a tested fallback before advertising support. |

## Release rule

Do not describe ATLAS as producing the “best” or most accurate research based on model selection or local test results. Promote a capability only to the level supported by its evidence: documented, structurally checked, locally tested, live-tested, or independently evaluated. Until the P0 and relevant P1 work is complete, live Copilot behavior and research-quality improvement remain unverified. See [implementation status](IMPLEMENTATION_STATUS.md), [model routing](MODEL_ROUTING.md), and the [benchmark protocol](../benchmarks/PROTOCOL.md).

# Model routing for GitHub Copilot cloud agent

## Recommended operating policy

For ATLAS work started on GitHub.com, select **Auto** in the Copilot cloud agent model picker when that entry point exposes it. GitHub documents Auto as task-aware model selection that considers task complexity and real-time model availability. It may route different prompts to different models; the selected model set is constrained by the user's plan and organization or enterprise policies. If a supported entry point does not offer a picker, GitHub says Auto is used automatically.

Do not hard-code a model in ATLAS custom-agent profiles. Leave the `model` property unset so the client/default selection remains authoritative. Use Auto for sequential research tasks unless a specific, user-authorized comparison requires an explicitly selected model. Do not assume a custom agent's name or role changes the underlying model.

## How to apply this in a research project

1. At task start, choose **Auto** where available. If a fixed model is intentionally selected for an experiment or a justified task, record the choice and reason in that task's branch output.
2. In the research plan, state that Copilot Auto is the default routing policy and that ATLAS does not select, pin, or verify the model.
3. In each branch output, record the model selection shown to the operator (`Auto` or the displayed fixed model), the task, and the date when known. Record the actual routed model only if the client exposes it; otherwise write `not exposed` instead of inferring it.
4. If the task materially changes in scope or reasoning demand, begin a new eligible task with the intended selection if appropriate. Model-picking entry points are surface-dependent; do not claim a running task was switched when no such control was observed.
5. Continue using domain protocols, source provenance, claim-level review, deterministic calculation, uncertainty, and stopping rules. Auto is a routing feature, not a factuality, citation, research-method, or independent-review guarantee.

## Boundaries and verification

ATLAS repository instructions cannot set Copilot account policy, enable models, inspect the hidden routing decision, or guarantee that Auto is available in a particular session. Model availability can change and depends on plan, client, and administrator policy. Custom-agent files in this repository define specialist prompts, not separate model identities or permission boundaries.

For a quality claim about Auto versus fixed models, use the blinded, equal-resource comparison in [the evaluation protocol](../benchmarks/PROTOCOL.md). Record the client surface, selection shown, actual model only when observable, tools, time/cost limits, and failures. Do not infer model superiority from a model label, one successful output, or agreement between agents.

## Official documentation

Checked 2026-11-04; verify current product behavior before relying on it:

- [Changing the AI model for GitHub Copilot cloud agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/changing-the-ai-model)
- [About GitHub Copilot auto model selection](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)
- [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

The cloud-agent model picker is only documented for supported task entry points. GitHub's custom-agent reference describes a `model` property, while the cloud-agent creation guide documents that property for IDE use; ATLAS therefore avoids relying on a profile-level model override for GitHub.com.

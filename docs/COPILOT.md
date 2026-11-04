# GitHub.com Copilot integration and environment

ATLAS supplies instructions, skills, specialist profiles, and a local Python control engine. It does not provision a Copilot account, add entitlements, start a hidden model CLI, or configure MCP servers. Check supported features and actual tools in the chosen client.

## Repository surfaces

| Files | Purpose and limit |
|---|---|
| `AGENTS.md`, `.github/copilot-instructions.md` | Operating policy; not a runtime interceptor or permission boundary |
| `.github/skills/*/SKILL.md` | Reusable stage instructions, invoked where skills are supported |
| `.github/agents/*.agent.md` | Specialist prompts and explicit requested tool lists; selection/support is client-dependent |
| `atlas` CLI | Local durable gates, evidence checks, calculations, and offline dispatch advice |

Profiles intentionally omit `model`. Use native **Auto** at a supported GitHub.com task-start picker; otherwise record and use the client default. Record the visible selection, actual tools, execution kind, and observed time. When the routed model is not exposed, write `not exposed`; do not infer it from a specialist's role or configuration.

GitHub's cached custom-agent reference says an unset model inherits the default and unrecognized tool names are ignored. Its creation guidance has also used IDE-specific wording for model configuration. Therefore ATLAS does not rely on profile-level model overrides on GitHub.com. See [model routing](MODEL_ROUTING.md).

## Tool lists and reviewers

Shipped frontmatter uses single-line strings, JSON double-quoted string arrays, and typed booleans. ATLAS's parser checks this restricted subset, not every valid YAML document or runtime behavior.

Profiles declare only role-relevant tool categories. Evidence and adversarial reviewers request `["read", "search"]`, with no edit, execution, or delegation tools. They return findings for the coordinator to persist; they do not modify evidence, receipts, or state. If original context is missing, they report the gap rather than enable another tool or certify unseen content.

Requested lists are **not a sandbox guarantee**. Client aliases, MCP tool names, policy, and enforcement vary; unknown names may be ignored. Inspect the actual exposed tools and enforce least privilege with real client/repository controls. Do not claim that a profile grants tools, guarantees read-only isolation, or authenticates an independent reviewer.

## Actual multi-agent execution

Use a single researcher for small or tightly coupled work. When independent branches warrant it, use the actual available subagent facility, not fictional roles or a fixed agent count. Give each worker a bounded objective, relevant mandate/protocol, approved access needs, explicit dependencies, and disjoint files/resources.

`python3 -m atlas dispatch-plan PROJECT_ID --max-workers 4` returns recommendations only. For `--max-workers` greater than 1, the current user-approved feature inventory must mark subagents enabled and the user must choose `use`; a limitation-accepted or unavailable subagent feature permits only single-worker planning. The coordinator rechecks current state, marks tasks running, invokes real tools/agents, persists JSON handoffs, and reconciles evidence before advancing. The Python fixture scheduler is not this execution facility. If a client lacks subagents, use sequential work and report the limitation; do not describe sequential role prompts as independent parallel agents.

Every worker reports access failures immediately. The coordinator classifies the failure: critical/security blocks hold affected decisions; optional-source failures do not automatically pause unrelated authorized work. Cancel affected jobs only using actual client controls. The local engine cannot automatically intercept all tools or terminate remote sessions. See [access policy](ACCESS.md) and [orchestration](../methods/ORCHESTRATION.md).

## Environment preparation

Python 3.10+ with SQLite and the standard library is sufficient for the core. No dependency installation, secret, extra paid service, or environment workflow is required for the shipped local checks. Optional PDF extraction needs `pypdf`; do not install it speculatively or mistake extracted text for visual verification.

Two GitHub.com execution environments must not be conflated:

- **Actions-based sessions** can use `.github/workflows/copilot-setup-steps.yml` where supported. If a later authorized task needs it, use exactly one `copilot-setup-steps` job, least permissions, no embedded secrets, and `workflow_dispatch` only for standalone validation triggers. Do not add push/pull-request triggers that create unapproved hosted runs. Copilot may still execute supported setup steps when starting its own task.
- **Cloud sandboxes** do not support GitHub Actions-specific setup steps, custom compute, or self-hosted runners according to the cached GitHub reference. They honor repository/organization firewall allowlists. An Actions workflow file cannot add sandbox support for those features.

No setup workflow is shipped here because it adds no necessary preparation for the standard-library core. Do not disable firewalls or change account/runners/MCP configuration to work around a block. A setup failure still requires inspecting the actual environment and following the risk-based access policy; a setup file is not proof of readiness.

## Validation boundary and references

Run `python3 -m atlas check` for the static subset and local links. An authorized live smoke test must separately observe instruction/skill discovery, tool selection, model observability, client cancellation, and access-stop behavior. Unit tests cannot establish those properties.

Official references were consulted by the parent upgrade on 2026-11-04; this documentation subtask used cached excerpts and made no network requests. Product availability and account policy remain unverified here:

- [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Copilot on GitHub.com: session environments](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)
- [Customizing the development environment](https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent)
- [Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)

## Copilot execution modes and session duration (updated November 2026)

GitHub's [October 28, 2026 announcement](https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/) explicitly states that its newer **cloud sandboxes have no one-hour limit on total running session time** and preserve snapshots for resumption. Some older **Actions-based Copilot cloud agent sessions** remain documented with a 59-minute maximum ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)). These statements refer to different execution paths and must not be conflated.

ATLAS **does not impose an arbitrary 59-minute cutoff**. Determine the actual client/runner and observed entitlement at runtime. Keep durable checkpoints so a network disconnect, quota, sandbox shutdown, or Actions-based timeout can be recovered without duplicating paid work. User observation of longer-running sessions is compatible with modern cloud sandboxes; do not override that observation by citing the older task limit.

Inspect the active client's tool list; an agent profile `tools` list is a request, not a guarantee. The coordinator uses the documented `agent` alias for subagent delegation on supported Copilot surfaces. A generic `web` alias should not be assumed to work in Actions-based cloud agent; check actually exposed retrieval tools or approved MCP routes.

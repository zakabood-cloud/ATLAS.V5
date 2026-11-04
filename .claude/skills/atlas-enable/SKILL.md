---
name: atlas-enable
description: Review observable Copilot feature availability and obtain explicit choices before research
---

Run this skill only after intake has ended and the MANDATE state is accepted. Read project status and the current mandate. Do not begin topic findings, methodological research, or a source/tool pilot.

Create `projects/<id>/enablement.json` from `python3 -m atlas copilot-features <id>`. Inspect the actual GitHub.com Copilot session and user-provided account/client details that are available. For every listed feature (`subagents`, `model_selection`, `mcp`, `web_access`, `repository_access`, `execution`, `file_access`, `customizations`), record the actual status (`enabled`, `disabled`, `unavailable`, or `unknown`), whether this inquiry needs it, the observed basis, controller (`user`, `administrator`, `plan`, `platform`, `unknown`), realistic enablement steps, and cost, privacy, and quality impact. Add relevant discovered features. Do not claim hidden settings, plan entitlements, or admin policies were inspected.

For any feature recorded `enabled`, provide a truthful current receipt: feature ID, enabled status, actual observation time, justified expiry, method, and limitations; link it by relative artifact path and SHA256. A local file cannot enable a Copilot capability. Never ask for secrets, bypass a policy, grant blanket administrator/write permissions, purchase access, or imply that a profile's tool list is a sandbox.

Present the needed and optional capabilities to the user and obtain a decision for every row: `use` only if verified enabled; `enable` when the user requests changing an available setting; `accept_limit` when the user explicitly accepts a needed gap; `not_needed` only when irrelevant to this inquiry. Explain minimum privilege, alternatives, cost/privacy tradeoffs, and decision-quality impact. Write the actual decisions and authorization basis to a separate JSON file, then run `enablement-approve`. If any requested enablement remains pending, do not advance to META. Only after a real supported user/admin change and a fresh observation receipt may the user decide `use`. If the user instead accepts the limit, record that choice and retain it in readiness and the final conclusion.

After feature review, use `atlas-discover` to perform the inquiry-specific MCP/built-in/local/manual access preflight before META. The offline `copilot-features` and `access-needs` commands do not inspect or configure the Copilot platform or enumerate every MCP.

# ATLAS 5 — Session environment profiles

Session length is **not** a universal constant. The effective client must be identified, rather than applying a hard-coded timer to every run.

| Environment | Duration interpretation | Continuation |
|---|---|---|
| New Copilot cloud sandbox | GitHub announced no one-hour total-session limit (2026-10-28); actual entitlement/quotas still apply | Reconnect to cloud sandbox or restore its snapshot where supported |
| Older Copilot Actions-based cloud agent task | Official documentation reports a 59-minute maximum for the task | Checkpoint, save task IDs and start an authorized subsequent task |
| Copilot CLI / IDE | Do not assume a GitHub Actions session duration; environment limits may vary | Resume same CLI/IDE session where supported, or use ATLAS handoff |
| Claude Code | Provider quota and client context/session behavior vary | Continue current conversation or recover from durable artifacts |
| Codex | Runtime-specific limitations apply | Use the supported session continuation mechanism or ATLAS handoff |

References: [GitHub new cloud sandbox announcement](https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/), [GitHub older cloud agent documentation](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent), [VS Code session guidance](https://code.visualstudio.com/docs/agents/concepts/sessions).

Core policy: no artificial session-length stop; persist state during work; never claim a previous tool request has completed merely because the conversation was resumed. Reconcile running remote jobs before dispatch and preserve approved spending scopes.

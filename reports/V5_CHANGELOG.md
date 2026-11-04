# ATLAS Research OS 5.0 — Implementation and release notes

## Starting point

The source is the supplied `ATLAS_Research_OS_v4.0.0_Copilot.zip`, preserved byte-for-byte as `reference/ATLAS_v4.0.0_user_supplied_original.zip`. It is separate from the older embedded v3 and Claude prototype histories. This release builds on v4 code, rather than merely generating a long prompt.

## Material v5 changes

1. **Portable core:** keep native Copilot `.github/` agent/skill instructions and add Claude Code `.claude/` agent/skill instructions and a concise `CLAUDE.md`. Static checks and release packaging include both rather than rejecting Claude files.
2. **Copilot delegation compatibility:** coordinator declares `agent`, not unrecognized `delegate`; other tool aliases are chosen by role. Actual client tool availability must still be verified.
3. **Session policy correction:** newer GitHub cloud sandboxes are documented as having no one-hour total-running limit; older Actions-based cloud-agent tasks can differ. Added `atlas.session` and CLI `session-profile`, with **no hard-coded duration cutoff**; retained resumable state and handoff artifacts.
4. **Risk-based access control:** optional failures are recorded without automatically creating a project-wide hold; critical and security failures create appropriate holds. Updated coordinator, specialist instructions and access policy.
5. **Research capabilities:** opt-in OpenAI/Gemini grounded-research adapter code with explicit spend and query-sharing approvals (mock-tested only); existing read-only scholarly discovery; evidence lineage tools, bounded lexical claim review, financial input provenance, source retrieval and method selection.
6. **Provider hardening:** require query-sharing permission even when the Python adapter is called directly; reject invalid model path segments and maintain idempotent cost reservations.
7. **Release history integrity:** retain the original v4 ZIP and reconcile its recorded v4 release-file SHA-256 values against that immutable archive, instead of erroneously comparing them to intentionally modified v5 files. Preserve embedded older prototype archives.
8. **Validation and cleanup:** exclude scratch validation directories from static link checks; add v5 regression tests for session modes, failure severity, provider authorization, source-check limitations, provenance, and portable profile delivery.

## What is not proven or completed

- Full live execution of all 62 requirements in the user's Copilot, Claude Code, or Codex account; this environment cannot authenticate to those clients.
- Live OpenAI/Gemini research responses, paid Amazon/commercial data subscriptions, or installed third-party MCP connections. No external provider credentials are included.
- Model-independent or expert-grade semantic source verification; lexical and marker checks are supporting guardrails, not proof of entailment.
- Empirical superiority on complex held-out real-world research tasks. Local unit and synthetic lifecycle tests are software checks, not research quality evidence.
- Automatic end-to-end orchestration of multiple remote agents without a suitable authenticated host runtime.

## Full tracking

See `docs/ATLAS5_IMPLEMENTATION_MATRIX.csv` for all 62 upgrade requests with status and test/permission boundaries. Entries marked `implemented_local` mean a bounded local behavior is implemented and tested; they do not establish live provider performance. `partial` and `not_verified` are not completed features.

## First-run command

Open the extracted ATLAS folder in a compatible Copilot or Claude Code session and send:

> Read AGENTS.md (or CLAUDE.md in Claude Code). Run `python3 -m atlas init` in the repository root. Report the observed readiness and available tools, then STOP. Wait for my research question. After receiving it, conduct a comprehensive adaptive clarification interview, including my desired deliverables, before meta-research or substantive research.

## References

- [GitHub Copilot Oct 28, 2026 cloud-sandbox announcement](https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/)
- [GitHub Copilot cloud agent guide for Actions-based execution](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)
- [GitHub custom-agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

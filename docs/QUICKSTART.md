# ATLAS 4 quickstart

ATLAS is a local audit/control toolkit for research conducted through the authorized GitHub Copilot client. It does not authenticate tools, install MCP servers, alter account settings or prove factual accuracy.

## 1. Initialize, then stop

From the repository root:

```sh
python3 -m atlas init
```

In Copilot, ask it to follow `AGENTS.md`, report verified readiness, and stop. Initialization does not create a research project or begin an interview.

## 2. Clarify and accept a mandate

On a later turn, give the research question. Copilot should ask adaptive questions about the decision, scope, geography/timeframe, constraints, evidence access, privacy, budget and exact deliverables. It should record answers in one project and show consequential assumptions before the user ends intake.

## 3. Review capabilities and access before research

After mandate acceptance, review observable Copilot features and ask for an explicit choice on each needed or optional capability. Then analyze topic-specific access needs. Before META or substantive research, Copilot must verify relevant MCP publishers/endpoints, compare them with available built-in/local/manual alternatives, explain permissions, privacy, cost and quality impacts, and ask the user to connect/approve. No blanket access is appropriate. `access-needs` is an offline prompt, not MCP discovery.

Only test after approval. Configuration is not proof of authentication. Any access block pauses the whole project; do not retry or switch sources until explicit scoped authorization. See [access and recovery](ACCESS.md).

## 4. Follow the workflow

New projects move through:

`INTAKE -> MANDATE -> ENABLEMENT -> META -> READINESS -> ORCHESTRATE -> RESEARCH -> VERIFY -> SYNTHESIS -> DELIVER -> MEMORY -> EVALUATE -> COMPLETE`

Use `python3 -m atlas status PROJECT_ID` before resuming and `python3 -m atlas validate PROJECT_ID` for local checks. See [usage](USAGE.md) and [artifact schemas](SCHEMAS.md). The coordinator owns shared state. It may use parallel agents only when actually available and warranted, with disjoint outputs; `dispatch-plan` only recommends and never launches them.

## 5. Check limits

```sh
python3 -m atlas check
python3 -m unittest discover -s tests -q
python3 scripts/demo.py
```

The demo is synthetic. Passing tests verify local controls, not live Copilot behavior, source completeness, semantic truth or research superiority. Existing schema-1 projects require an explicitly authorized backed-up migration; see [migration](MIGRATION.md).

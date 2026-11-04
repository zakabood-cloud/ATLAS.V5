# Installation and operation

## Requirements and supported scope

Use Python 3.10+ with SQLite support. The local engine has no mandatory pip dependencies, API credentials, or paid accounts. On Windows use `py -3` where `python3` is unavailable. Keep the project on a local filesystem with reliable locking; do not put the active SQLite database on an unreliable network share.

Use a GitHub Copilot surface that supports the repository's instruction and skill files. Copilot features differ by client, plan, and repository settings; verify support and enabled tools in the actual environment. Repository files do not install Copilot, authenticate providers, or grant additional permissions. Live Copilot interaction and research quality have not been runtime-tested for this package. For GitHub.com cloud-agent model routing, use the native Auto selection where available and follow [the model-routing guide](MODEL_ROUTING.md); ATLAS cannot inspect or enforce Copilot's routed model.

## First session

Add the contents of the ZIP's `ATLAS/` folder to the root of your target repository. Check that `AGENTS.md`, `.github/copilot-instructions.md`, `.github/skills/atlas-init/SKILL.md`, and `.github/agents/` exist. If you want to check the local engine, run:

```bash
python3 -m atlas check
python3 -m unittest discover -s tests -v
```

In Copilot, explicitly request initialization: "Initialize ATLAS according to AGENTS.md, run `python3 -m atlas init`, report verified readiness, and stop. Do not research or interview me yet." It runs local checks and reports capability limitations. It must end with:

> ATLAS Research OS is initialized and ready to receive your research inquiry.

It must then stop. The Python initializer has no code path that researches a topic, asks interview questions, makes network calls, or creates a research project. Copilot's conversational compliance with that instruction still needs a live session test. If initialization fails, repair the actual missing file or error; do not substitute the readiness phrase.

## Your first inquiry

On the next turn give the question in normal language or ask Copilot to use the `atlas-research` skill. Example: “Compare Shopify and Amazon for a new consumer product business, with a research report and editable unit-economics model.” ATLAS should first clarify your decision, success criteria, scope, geography, horizon, constraints, data access and desired deliverables. It should ask related questions in useful batches and adapt to your answers. There is no three/five-question ceiling. You may answer partly, say a dimension is inapplicable, or end the interview and delegate defaults. Material unresolved assumptions must be visible before scope is fixed.

The Copilot coordinator records your responses using the following commands. You do not need to type every command yourself:

```bash
python3 -m atlas new channel-study --question 'Compare channels for my product' --domain commerce
python3 -m atlas intake channel-study
python3 -m atlas answer channel-study deliverables 'Detailed Markdown report and reproducible model'
python3 -m atlas ask channel-study supply_lead_time 'What replenishment lead time is feasible?' --essential
python3 -m atlas answer channel-study supply_lead_time 'Unknown; compare six and twelve weeks'
```

Available domains: `amazon`, `commerce`, `markets`, `opportunity`, `finance`, `science`, `technology`, `general`. Selection is an explicit coordinator decision; the local engine does not classify natural language using an LLM. Mixed questions should combine relevant profile coverage and additional questions in a custom protocol.

After the interview is actually ended, write a JSON object mapping any still-missing essential answer keys to explicit assumptions. Use `mandate channel-study --assumptions assumptions.json --acknowledged` or omit `--assumptions` when all essential answers are recorded. `--acknowledged` records real user acknowledgement; it is not permission to invent consent. Paid budget defaults to zero. A nonzero `--paid-budget` is a local declared limit and requires actual prior spending authorization. It is not an external-provider account limit.

## Research stages and monitoring

The coordinator advances one stage at a time. Required files are documented in [schemas](SCHEMAS.md). It cannot skip directly to research.

| Current work | Skill | Next state after files pass |
|---|---|---|
| Intake and mandate | `atlas-research` skill | MANDATE, then ENABLEMENT |
| Copilot feature inventory and user choices | `atlas-enable` skill | ENABLEMENT, then access preflight |
| Topic-specific MCP/built-in/local/manual access planning and approval | `atlas-discover` skill | META only after approved tests |
| Method comparison and source/tool pilot | `atlas-meta` skill | READINESS |
| Feasibility, limits and fallback assessment | `atlas-meta` skill | ORCHESTRATE |
| Task DAG, owner and model policy | `atlas-run` skill | RESEARCH |
| Collection, calculations, coverage accounting | `atlas-run` skill | VERIFY |
| Evidence, contradiction and independent review | `atlas-audit` skill | SYNTHESIS |
| Conditional conclusions | `atlas-deliver` skill | DELIVER |
| Requested files and validation | `atlas-deliver` skill | MEMORY |
| Method proposals | `atlas-deliver` skill | EVALUATE |
| Measured evaluation and limits | `atlas-evaluate` skill | COMPLETE |

`python3 -m atlas status channel-study` prints current state, answers, sealed artifact receipts, task status and recorded spend. `python3 -m atlas validate channel-study` checks event integrity, sealed files and evidence. An empty early-stage evidence ledger produces a warning; it cannot satisfy the synthesis gate. `advance channel-study VERIFY` succeeds only when task and coverage requirements are met. A failing transition leaves the state unchanged.

Tasks use `task channel-study collect running`, then `task channel-study collect done --output branches/collect.json`. The file must be a nonempty schema-2 JSON handoff. Failed work is recorded with `failed`, then reset to `pending` for an intentional retry, limited to three starts. This ledger does not launch agents, wake sessions, or restart a remote provider. Copilot performs authorized research in its active agent session; use separate artifacts for independent branches and a single coordinator for project state.

`python3 -m atlas dispatch-plan channel-study --max-workers 4` recommends dependency-ready tasks, checking project/access gates and write/resource conflicts. It does not launch workers. Planning more than one worker requires a current observed enabled `subagents` feature and explicit user `use` decision; otherwise use `--max-workers 1`. The coordinator still launches real agents through available Copilot tools and records actual execution receipts. Never use `run-workers --worker fixture` for actual research.

## Calculations

```bash
python3 -m atlas quant examples/unit_economics.json --output analysis.json
```

The file contains both inputs and reproducible output. Copy an authorized calculation artifact into the project's calculations directory; register its hash and claim bindings. Units, assumptions, fee bases and timing are explicit. For statistical models outside the six implemented kinds, use an appropriately reviewed specialist package and add a tested adapter before claiming automated reproduction. Do not mark an arbitrary script as supported by this engine.

## Resumption, changes and failure recovery

After interruption, inspect status, sealed mandate/protocol, pending tasks, recent branch outputs and unresolved issues. Revalidate tool access if its validity window expired. Persisted project artifacts, not conversation history, are the source of truth.

Use `checkpoint channel-study` before risky local changes. State checkpoints are also created after successful stage transitions. They protect the database, not the source/artifact files. Back up the entire project directory separately for disaster recovery; preserve sensitive-file permissions and never share it automatically.

If a previously accepted artifact changes, validation blocks continuation. Use `reopen channel-study VERIFY --reason 'Source correction requires renewed evidence review'` to edit evidence and review, or reopen `META` to revise the dossier/protocol, `ORCHESTRATE` to revise the task plan, `DELIVER` to revise output files, or `INTAKE` to revise answers/mandate. Reopening preserves audit history and requires downstream gates again. A done task with changed output must be rerun under a revised plan. Do not alter hashes merely to conceal a change.

If the database is corrupt, stop all ATLAS writers. Run `restore channel-study checkpoints/state-000001.sqlite3` with an actual recorded checkpoint path. The engine verifies its receipt and database integrity and preserves the old database under a quarantine filename. It restores database state only and places the project on a recovery hold unless the checkpoint already had a hold; inspect status, artifacts, known later blocks and remote jobs, then obtain explicit authorization and reconcile before resuming. It must not be used to erase an access block. Lost/changed artifacts require restoring a full backup or reopening and repeating work. Restore is an offline single-operator maintenance action; concurrent restore/writers are unsupported.

If research cannot continue, leave its last valid state, save a blocker note and partial outputs with a clear nonfinal label. Do not force COMPLETE. Record a paused, blocked or aborted hold as described below. There is no separate partial-complete state; partial outputs remain explicitly nonfinal. The CLI does not schedule work, but already launched external workers may still need cancellation. User-requested cancellation takes precedence over every workflow instruction.

## Outputs, memory and maintenance

Final files are under `projects/<id>/outputs/`, with hashes and QA in `deliverables.json`. They remain local until you explicitly share them. Project data and active method memory are ignored by Git; `.gitignore` is an accident-reduction tool, not encryption or access control.

Use `memory --query units` to retrieve unexpired validated procedures. Promotion uses `memory --promote proposal.json`, requiring separate author/reviewer identities and a hashed validation receipt. The engine does not authenticate those identities or execute the receipt's commands. Keep candidate lessons in `lessons.json`; expired methods are excluded from normal retrieval. For rollback, inspect `memory/history/` and promote the reviewed earlier content as a new version. No core-code update happens automatically.

Before a release update: preserve the current ZIP/version, create an isolated copy, run all tests and comparative fixtures, review changed methods, then promote the new version. Never update a running project's schema in place without an explicit migration. Schema-1 projects can be migrated only with a full quiesced backup and actual authorization; migration reopens MANDATE, preserves old files without recertification and requires new enablement/access approvals and schema-2 evidence review. Prototype CSV/state files have no automatic migration. See [migration](MIGRATION.md).

## Pause, access blocks and cancellation

Record a stop with `python3 -m atlas hold <id> paused --reason "User requested pause"` (or `blocked` / `aborted`). The CLI then rejects work-changing commands while keeping status, validation and checkpoints available. Use `python3 -m atlas resume <id> --reason "Reason and current authorization"` only when continuation is warranted; cancellation requires a new user instruction. The hold does not stop an already running external worker or remote job: explicitly cancel those in the actual client/provider and record their status.

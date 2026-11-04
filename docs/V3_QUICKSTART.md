# ATLAS 3.0 — Historical GitHub Copilot quick start

> **Legacy reference only.** This guide describes the prior v3 workflow and its commands do not implement ATLAS 4's ENABLEMENT, topic-specific access, or schema-2 research gates. For current use, follow [the ATLAS 4 quickstart](QUICKSTART.md), [schemas](SCHEMAS.md), and [access/recovery guide](ACCESS.md).

1. Add the contents of the `ATLAS/` folder to the root of the repository where you want ATLAS available.
2. Confirm the repository contains `AGENTS.md`, `.github/copilot-instructions.md`, `.github/skills/`, and `.github/agents/`.
3. Use a GitHub Copilot surface that supports repository instructions and agent skills. Feature support can vary by surface, plan, and repository settings.
4. If you want to check the local engine, run `python3 -m atlas check` and `python3 -m unittest discover -s tests -q` from the repository root.
5. In Copilot, ask: **"Initialize ATLAS according to AGENTS.md, run `python3 -m atlas init`, report verified readiness, and stop. Do not research or interview me yet."** The exact readiness line is `ATLAS Research OS is initialized and ready to receive your research inquiry.` Initialization must not create a project, make a network request, or begin intake.
6. On a later turn, give the research question. Copilot should clarify objectives, constraints, and desired deliverables before meta-research or topic research. Skills load as relevant; you can also ask Copilot to use `atlas-research` explicitly.
7. Copilot performs authorized research in its active agent session. Record plans, evidence, and task outputs in project artifacts and use the CLI to enforce state transitions. The local scheduler does not launch a separate model CLI.

## Offline commands

```sh
python3 -m atlas queries 'UAE vs USA e-commerce' --coverage 'demand,competition,unit economics'
python3 -m atlas method-score examples/method_pilots.json
python3 -m atlas quant examples/ecommerce_economics.json
python3 -m atlas quant examples/correlated_simulation.json
python3 -m atlas memory-search 'market sizing'
python3 -m atlas budget status --limit 0
python3 -m atlas run-workers PROJECT_ID --worker fixture
```

The fixture worker writes synthetic text for testing only. It is never a real research operation.

## Optional live metadata lookup

```sh
# Public metadata requests require explicit opt-in and may be metered
python3 -m atlas scholarly-search crossref 'systematic review' --live --limit 5
```

Check provider terms and obtain user authorization before any request that could incur cost or disclose data. Copilot tool availability does not imply provider authentication or permission.

## Citation checks

After registering evidence and generating a Markdown report with `[[claim:C1]]` markers:

```sh
python3 -m atlas report-audit PROJECT_ID projects/PROJECT_ID/outputs/report.md
python3 -m atlas review-packet PROJECT_ID C1
```

An independent reviewer must still assess semantic support and original-source authenticity.

## Known limitations

See [implementation status](IMPLEMENTATION_STATUS.md) and [security](SECURITY.md). Repository instructions and agent profiles do not create a sandbox, prove tool access, or guarantee that Copilot followed a workflow. Live Copilot interaction and research quality have not been independently evaluated for this package.

## Backups and ingestion

`python3 -m atlas project-backup PROJECT_ID /absolute/path/backup.zip --quiesced` requires all project writers and external workers to be stopped. Restore into a **new** location using `python3 -m atlas project-restore /absolute/path/backup.zip /absolute/path/restored-project`. Backups are not encrypted; protect confidential research files.

`python3 -m atlas ingest source.html --output extracted.json` supports plain text, JSON, CSV/TSV, and HTML locally; text-only PDF extraction requires optional `pypdf` and cannot verify images, charts, or scans.

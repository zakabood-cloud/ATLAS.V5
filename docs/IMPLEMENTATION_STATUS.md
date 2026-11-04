# ATLAS 3.0 implementation status — qualified release

The underlying ATLAS 3.0 engine was locally tested before this Copilot conversion. **The Copilot-specific repository layout and code changes in this archive have not been executed or runtime-tested.** This is not a claim that 106 upgrades are all complete or that any AI is objectively the world's best. The accompanying 106-row CSV is historical scope accounting.

**Bounded local implementation** denotes code that works for the documented limited scope; it does not establish broader research superiority. **Partial or procedural** denotes supporting code/guidance where major work remains. **Not yet implemented or unverified** denotes explicit release gaps. Items requiring actual accounts, paid APIs, scientific ground truth, expert raters, and Copilot live sessions cannot honestly be demonstrated here.

## Implemented improvements

- `atlas.scheduler`: concurrency-bounded, dependency-ordered synthetic fixture dispatch with persisted branch outputs; real research is conducted in the active Copilot session and recorded through the task ledger
- `atlas.adapters`: explicit hostname allowlist, redirects disabled, bounded read-only bibliographic metadata searches for Crossref and OpenAlex, user must opt in to live calls
- `atlas.retrieval`: query expansion, local BM25 retrieval, URL canonicalization and source-origin-aware coverage diagnostics
- `atlas.methodology`: explicit pilot-evidence-based scoring of research methods, never universal proof
- `atlas.verification`: claim marker auditing and integrity of semantic-review receipts; human/model semantic reviewer still needed
- `atlas.sourcegraph`: grouping by declared common original content plus contradiction reporting
- `atlas.budget`: transactional preflight reservations and settlement, **not** provider-side spending limits
- `atlas.decision`: e-commerce contribution/working-capital toy model, a reproducible latent-Gaussian copula simulator and reverse stress calculations
- `atlas.evaluation`: paired question accuracy/abstention metrics, **not** actual research performance claims
- `atlas.memory_search`: ranked lexical retrieval from reviewed method records
- Copilot repository instructions, reusable agent skills, and specialist custom-agent profiles under `.github/`
- GitHub.com cloud-agent guidance for native Auto model selection, per-task observation logging, and bounded model-routing evaluation; this does not control or observe Copilot's runtime router
- A prioritized [upgrade roadmap](UPGRADE_ROADMAP.md) distinguishing repository changes from live-platform and independent-research validation
- Task states support justified noncritical blocked/skipped items without silently counting them as completed; critical incomplete work remains a hard gate

## Unverified high-impact items

1. Copilot live runtime behavior, skill discovery, custom-agent selection, Auto routing decisions, and instruction-following across supported clients
2. Real paid data sources (Amazon, advertising intelligence, Similarweb, Parallel, Gemini, OpenAI) and provider-side quota controls
3. True semantic citation entailment, automatic reliable factuality, source independence and review identity assurance
4. Full multimodal PDF/spreadsheet parsing and visual source verification in actual sessions
5. Statistical calibration, field-specific models, observational forecasts and expert adjudication
6. Meaningful cross-project held-out comparison against alternative research systems
7. Automatic remote-job reconciliation/cancellation and end-to-end distributed recovery
8. User-account-specific MCP installation and credential-backed tool discovery

The existing `reports/test_results.json`, `reports/package_validation.json`, and `reports/TESTING.md` describe the earlier pre-conversion release. They are retained as historical artifacts and do **not** validate this Copilot conversion. The revised archive manifest covers the converted files only.

Do not describe test fixtures, tool catalogs, code interfaces or planned capabilities as operating integrations. Do not bypass permission checks or expose secrets to model context.

## Additional bundled components

- `atlas.ingest`: bounded local TXT/CSV/TSV/JSON/HTML extraction and optional text-only PDF extraction (`pypdf` not mandatory); chart/scanned PDF review is NOT automated
- `atlas.project_archive`: complete-file local project ZIP backup/restore, requires quiesced writers, verifies archive hashes, restores only to fresh directory
- `atlas.experiment`: exact discrete binary expected value of sample information; input assumptions are externally supplied

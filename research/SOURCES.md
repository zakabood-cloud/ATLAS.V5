# Dated research source register

Accessed 2026-11-03. These records support the engineering review; none implies a live API test. Exact versions are recorded where exposed. Findings are summaries, not copied source text.

## CC01 — Instruction hierarchy and memory

[https://code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Project instructions and modular rules have different loading behavior; imports do not make large instructions cheap.

## CC02 — Skills and progressive disclosure

[https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Skills use project folders and YAML metadata; allowed-tools preapproves tools rather than restricting availability.

## CC03 — Custom subagents

[https://code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Tools allowlists narrow subagent access. Persistent memory can enable write/edit tools; omit it from read-only reviewers.

## CC04 — Experimental agent teams

[https://code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Teams are experimental and have session-resumption and coordination limitations.

## CC05 — Settings hierarchy

[https://code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Settings have scopes and precedence; local project config must respect managed policy.

## CC06 — Hook lifecycle

[https://code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Hooks can execute lifecycle actions; no executable hook is enabled without a tested need.

## CC07 — MCP configuration

[https://code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Server configuration does not establish authenticated working access. Project-scoped server behavior differs by execution mode.

## CC08 — Security boundaries

[https://code.claude.com/docs/en/security](https://code.claude.com/docs/en/security)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Permissions and sandboxing are separate controls; retrieved content is a prompt-injection risk.

## CC09 — CLI execution

[https://code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Programmatic and interactive interfaces exist; this release tests neither against an installed Claude executable.

## CC10 — Observability

[https://code.claude.com/docs/en/monitoring-usage](https://code.claude.com/docs/en/monitoring-usage)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Monitoring and telemetry are documented; no external telemetry exporter was configured.

## CC11 — Sandboxed Bash

[https://code.claude.com/docs/en/sandboxing](https://code.claude.com/docs/en/sandboxing)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

OS/network sandbox configuration is distinct from prompt instructions; availability depends on environment.

## CC12 — Cost and context management

[https://code.claude.com/docs/en/costs](https://code.claude.com/docs/en/costs)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Measure actual usage and model costs; context discipline and caching do not establish research quality.

## CC13 — Plugin architecture

[https://code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Plugins package extensions; this release uses a normal project layout to avoid installation overhead.

## CC14 — Model routing

[https://code.claude.com/docs/en/model-config](https://code.claude.com/docs/en/model-config)

Type: official documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Available aliases and provider model settings require runtime checks; inherit avoids a hardcoded unavailable model.

## ML01 — Anthropic model overview

[https://platform.claude.com/docs/en/models/overview](https://platform.claude.com/docs/en/models/overview)

Type: vendor documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Current catalog lists Fable 5.1 and Opus/Sonnet/Haiku 5.5. Availability and vendor positioning are documented, not independently benchmarked here.

## ML02 — OpenAI models

[https://developers.openai.com/api/docs/models](https://developers.openai.com/api/docs/models)

Type: vendor documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Current catalog separates general models and specialized research offerings; choose available IDs at runtime.

## ML03 — OpenAI deep research

[https://developers.openai.com/api/docs/guides/deep-research](https://developers.openai.com/api/docs/guides/deep-research)

Type: vendor documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

API research expects a prepared inquiry, supports specified retrieval tools and background execution; privacy and tool restrictions require review.

## ML04 — Gemini models

[https://aistudio.google.com/docs/models](https://aistudio.google.com/docs/models)

Type: vendor documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Current catalog includes Gemini 4 Argon; context specifications do not prove effective retrieval or recall.

## ML05 — Gemini Deep Research

[https://ai.google.dev/gemini-api/docs/deep-research](https://ai.google.dev/gemini-api/docs/deep-research)

Type: vendor documentation. Version: deep-research-preview-04-2026 and max preview observed. Inspection: relevant documentation/abstract sections inspected.

Preview research agent uses Interactions API and asynchronous background execution; separate from generate_content and general model usage.

## ML06 — Perplexity API overview

[https://docs.perplexity.ai/docs/getting-started/overview](https://docs.perplexity.ai/docs/getting-started/overview)

Type: vendor documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Agent and Search APIs are distinct. Current docs include migration from Sonar; avoid carrying old endpoint instructions forward.

## ML07 — Perplexity Sonar migration announcement

[https://community.perplexity.ai/t/sonar-is-moving-to-the-agent-api/5802](https://community.perplexity.ai/t/sonar-is-moving-to-the-agent-api/5802)

Type: official provider announcement. Version: 2026-08-13 announcement. Inspection: relevant documentation/abstract sections inspected.

Provider announced Sonar endpoint retirement on September 27, 2026. Current runtime status must still be tested; old Sonar recipes are not deployment defaults.

## ML08 — Parallel research basis

[https://docs.parallel.ai/task-api/guides/access-research-basis](https://docs.parallel.ai/task-api/guides/access-research-basis)

Type: vendor documentation. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Task outputs expose field-level evidence, rationale and confidence; confidence is provider output and needs independent calibration.

## AR01 — Scaling Agent Systems

[https://arxiv.org/abs/2512.08296v3](https://arxiv.org/abs/2512.08296v3)

Type: research preprint; Google/MIT affiliations. Version: v3, 2026-04-08. Inspection: abstract plus full-text structure/results/limitations inspected.

Coordination benefit varies with task structure; observed gains and losses do not support universal multi-agent superiority.

## AR02 — Anthropic multi-agent research system

[https://www.anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system)

Type: vendor engineering study. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Artifact handoffs and central orchestration can help research, but reported performance is vendor-internal and cost/resource differences matter.

## AR03 — LangGraph persistence

[https://docs.langchain.com/oss/python/langgraph/persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

Type: official framework docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Checkpoint and store abstractions support durable workflows; integration cost is unjustified for this offline single-coordinator core.

## AR04 — OpenAI Agents SDK

[https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/)

Type: official framework docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Agent orchestration, handoffs, sessions and tracing are documented; no SDK runtime or API integration was tested.

## AR05 — AutoGen

[https://microsoft.github.io/autogen/stable/index.html](https://microsoft.github.io/autogen/stable/index.html)

Type: official framework docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

AgentChat and event-driven Core supply orchestration abstractions; they do not by themselves supply claim-level evidence validity.

## AR06 — CrewAI Flows

[https://docs.crewai.com/v1.15.34/en/concepts/flows](https://docs.crewai.com/v1.15.34/en/concepts/flows)

Type: official framework docs. Version: v1.15.34 URL observed. Inspection: relevant documentation/abstract sections inspected.

Flows offer structured process controls; this release avoids a dependency without demonstrated incremental value.

## EV01 — BrowseComp

[https://openai.com/index/browsecomp/](https://openai.com/index/browsecomp/)

Type: vendor-authored benchmark. Version: 2025-04-10. Inspection: relevant documentation/abstract sections inspected.

Short verifiable fact retrieval is useful but not a measure of complete open-ended report quality.

## EV02 — DeepResearch Bench

[https://arxiv.org/abs/2506.11763](https://arxiv.org/abs/2506.11763)

Type: research preprint. Version: v1, 2025-06-13. Inspection: relevant documentation/abstract sections inspected.

Report and citation evaluation add dimensions absent from short-answer benchmarks.

## EV03 — DeepResearch Bench II

[https://arxiv.org/abs/2601.08536v3](https://arxiv.org/abs/2601.08536v3)

Type: research preprint. Version: v3, 2026-09-10. Inspection: abstract plus full-text structure/method/results/limitations inspected.

Expert-report-derived rubrics separate recall, analysis and presentation; leakage, annotation and presentation limitations remain.

## EV04 — FActScore

[https://aclanthology.org/2023.emnlp-main.741/](https://aclanthology.org/2023.emnlp-main.741/)

Type: peer-reviewed EMNLP paper. Version: DOI 10.18653/v1/2023.emnlp-main.741. Inspection: relevant documentation/abstract sections inspected.

Atomic factual support is a more informative target than a single report-level correctness label.

## EV05 — ALCE

[https://aclanthology.org/2023.emnlp-main.398/](https://aclanthology.org/2023.emnlp-main.398/)

Type: peer-reviewed EMNLP paper. Version: DOI 10.18653/v1/2023.emnlp-main.398. Inspection: relevant documentation/abstract sections inspected.

Citation correctness and completeness deserve distinct evaluation from answer fluency.

## EV06 — DeepTRACE

[https://proceedings.iclr.cc/paper_files/paper/2026/hash/ad08767706825033b99122332293033d-Abstract-Conference.html](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ad08767706825033b99122332293033d-Abstract-Conference.html)

Type: peer-reviewed ICLR paper. Version: ICLR 2026 proceedings. Inspection: relevant documentation/abstract sections inspected.

Sources and citations can be present while statements remain unsupported; audit attribution and support separately.

## EV07 — LiveResearchBench

[https://proceedings.iclr.cc/paper_files/paper/2026/hash/998f8d8ff2697da2eae5f87143668754-Abstract-Conference.html](https://proceedings.iclr.cc/paper_files/paper/2026/hash/998f8d8ff2697da2eae5f87143668754-Abstract-Conference.html)

Type: peer-reviewed ICLR paper. Version: ICLR 2026 proceedings. Inspection: relevant documentation/abstract sections inspected.

Current user-centered tasks and citation-traceability assessment motivate live held-out evaluation.

## EV08 — DeepFact

[https://aclanthology.org/2026.acl-long.1586/](https://aclanthology.org/2026.acl-long.1586/)

Type: peer-reviewed ACL paper. Version: DOI 10.18653/v1/2026.acl-long.1586. Inspection: relevant documentation/abstract sections inspected.

Audited revisable labels and rationales improve evaluation reliability; one-shot reviewer labels are fallible.

## EV09 — Who is the Agent to Blame?

[https://aclanthology.org/2026.emnlp-main.1681/](https://aclanthology.org/2026.emnlp-main.1681/)

Type: peer-reviewed EMNLP paper. Version: DOI 10.18653/v1/2026.emnlp-main.1681. Inspection: relevant documentation/abstract sections inspected.

Citation and faithfulness failures can arise at handoffs and synthesis; trace claim origin through stages.

## EV10 — OpenRouter BrowseComp runs

[https://openrouter.ai/benchmarks/browsecomp/](https://openrouter.ai/benchmarks/browsecomp/)

Type: commercial third-party primary benchmark. Version: snapshot date reported 2026-11-02; run dates differ. Inspection: relevant documentation/abstract sections inspected.

Search configuration comparisons include differing question counts and budgets; do not convert the leaderboard into a universal frontier-model ranking.

## ME01 — PRISMA 2020

[https://www.bmj.com/content/372/bmj.n71](https://www.bmj.com/content/372/bmj.n71)

Type: peer-reviewed reporting guideline. Version: DOI 10.1136/bmj.n71. Inspection: relevant documentation/abstract sections inspected.

Use reporting requirements for actual systematic reviews; reporting completeness is not evidence certainty.

## ME02 — PRISMA-S

[https://www.prisma-statement.org/prisma-search](https://www.prisma-statement.org/prisma-search)

Type: official methodology page. Version: DOI 10.1186/s13643-020-01542-z. Inspection: relevant documentation/abstract sections inspected.

Search reporting needs exact strategies, sources and retrieval context.

## ME03 — Cochrane search and study selection

[https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)

Type: professional methodology handbook. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Link multiple reports to underlying studies, document search/selection and evaluate missing evidence.

## ME04 — GRADE criteria

[https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html)

Type: official professional handbook. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Assess outcome-level certainty across bias, consistency, directness, precision and publication bias; do not repurpose as arbitrary commercial scoring.

## ME05 — Causal Inference: What If

[https://miguelhernan.org/whatifbook](https://miguelhernan.org/whatifbook)

Type: author-hosted methodological book. Version: 2020 book; maintained author page. Inspection: relevant documentation/abstract sections inspected.

Causal identification requires explicit design assumptions; correlation alone is inadequate.

## ME06 — Forecasting: Principles and Practice

[https://otexts.com/fpp3/toolbox.html](https://otexts.com/fpp3/toolbox.html)

Type: author-hosted methods text. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Forecast evaluation distinguishes training fit, held-out error and distributional performance; use appropriate baselines.

## ME07 — HM Treasury Green Book

[https://www.gov.uk/government/publications/the-green-book--2](https://www.gov.uk/government/publications/the-green-book--2)

Type: official appraisal guidance. Version: page updated 2026-10-28. Inspection: relevant documentation/abstract sections inspected.

Transparent alternatives, appraisal and uncertainty are useful design anchors; government discount assumptions are not generic private-business defaults.

## SE01 — NIST Generative AI Profile

[https://doi.org/10.6028/NIST.AI.600-1](https://doi.org/10.6028/NIST.AI.600-1)

Type: official risk guidance. Version: NIST AI 600-1, 2024. Inspection: relevant documentation/abstract sections inspected.

Confabulation, information integrity, security and privacy require explicit risk management rather than prompt-only guarantees.

## SE02 — MCP security best practices

[https://modelcontextprotocol.io/docs/draft/tutorials/security/security_best_practices](https://modelcontextprotocol.io/docs/draft/tutorials/security/security_best_practices)

Type: official draft protocol guidance. Version: draft guidance as accessed. Inspection: relevant documentation/abstract sections inspected.

MCP introduces token, confused-deputy, SSRF and local server risks; review scopes and provenance.

## SE03 — SQLite atomic commit

[https://www.sqlite.org/atomiccommit.html](https://www.sqlite.org/atomiccommit.html)

Type: official database docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Transactional local state reduces partial-write failures; hardware and filesystem assumptions still matter.

## SE04 — SQLite online backup

[https://www.sqlite.org/backup.html](https://www.sqlite.org/backup.html)

Type: official database docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Use database backup API for coherent checkpoints, not copying a live database blindly.

## DA01 — Crossref REST API

[https://www.crossref.org/documentation/retrieve-metadata/rest-api/](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

Type: official API docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Scholarly metadata discovery and DOI linkage do not guarantee access to full text or claim correctness.

## DA02 — OpenAlex

[https://help.openalex.org/](https://help.openalex.org/)

Type: official data-provider docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Scholarly index and API support discovery; inspect current access requirements and coverage before use.

## DA03 — SEC EDGAR data APIs

[https://www.sec.gov/search-filings/edgar-application-programming-interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

Type: official regulator API docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Public submissions and XBRL data are accessible without API keys; compare taxonomy, period, units and restatements.

## DA04 — Amazon SP-API

[https://developer-docs.amazon/sp-api/docs/welcome](https://developer-docs.amazon/sp-api/docs/welcome)

Type: official platform docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Authorized selling-partner APIs concern seller/vendor applications; not a public competitor exact-sales feed.

## DA05 — Shopify GraphQL Admin API

[https://shopify.dev/docs/api/admin-graphql/2026-10](https://shopify.dev/docs/api/admin-graphql/2026-10)

Type: official platform docs. Version: 2026-10 version observed. Inspection: relevant documentation/abstract sections inspected.

Authenticated administrative data concerns authorized stores; not arbitrary competitors.

## DA06 — Statistics Canada WDS

[https://www.statcan.gc.ca/en/developers/wds](https://www.statcan.gc.ca/en/developers/wds)

Type: official statistics API docs. Version: page modified 2025-12-10. Inspection: relevant documentation/abstract sections inspected.

Provides published data and metadata with table/vector identifiers; preserve release and reference periods.

## DA07 — US Census APIs

[https://www.census.gov/data/developers/data-sets.html](https://www.census.gov/data/developers/data-sets.html)

Type: official statistics API docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Demographic/economic datasets have coverage and period constraints; aggregate indicators are not niche product sales.

## DA08 — UAE open-data guidance

[https://u.ae/en/Help/FAQs/open-data](https://u.ae/en/Help/FAQs/open-data)

Type: official government guidance. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

FCSC and sector agencies are authoritative discovery routes; actual dataset definitions and access remain dataset-specific.

## DA09 — World Bank Indicators API

[https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation)

Type: official API docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Macro indicators enable contextual comparisons with definitions and revisions; not direct entrant demand.

## DA10 — Keepa API

[https://keepa.com/api-docs/](https://keepa.com/api-docs/)

Type: official data-provider docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Price/product/offer histories and related marketplace data require an API plan; do not infer exact profits from ranks.

## DA11 — Keepa plans and tokens

[https://keepa.com/api-docs/plans-tokens.html](https://keepa.com/api-docs/plans-tokens.html)

Type: official pricing mechanics. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Monthly API token-rate plans and endpoint-specific consumption require a current quote and budget check; not tested here.

## DA12 — Jungle Scout sales estimates

[https://support.junglescout.com/hc/en-us/articles/21534073571607-Use-Cases-for-Sales-Estimates-Endpoint](https://support.junglescout.com/hc/en-us/articles/21534073571607-Use-Cases-for-Sales-Estimates-Endpoint)

Type: official data-provider docs. Version: page updated 2025-07-18. Inspection: relevant documentation/abstract sections inspected.

Sales are modeled; variant responses may aggregate parents. Listed markets include US/CA but not UAE/KSA.

## DA13 — Similarweb methodology

[https://support.similarweb.com/hc/en-us/articles/360001631538-Similarweb-Data-Methodology](https://support.similarweb.com/hc/en-us/articles/360001631538-Similarweb-Data-Methodology)

Type: official data-provider methodology. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Blended signals and modeling produce traffic intelligence; modeled visits are not verified sales or profitability.

## DA14 — Tavily docs

[https://docs.tavily.com/](https://docs.tavily.com/)

Type: official tool docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Search/extract/research and an official remote MCP route are documented; connection and tool quality remain untested.

## DA15 — Firecrawl docs

[https://docs.firecrawl.dev/introduction](https://docs.firecrawl.dev/introduction)

Type: official tool docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Extraction/crawling may improve page acquisition; extracted text needs original-context checks and rights review.

## DA16 — EPO Open Patent Services

[https://www.epo.org/en/searching-for-patents/data/web-services/ops](https://www.epo.org/en/searching-for-patents/data/web-services/ops)

Type: official patent-data docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Patent data can support technical diligence, not by itself a freedom-to-operate legal opinion.

## DA17 — Google Ads keyword planning

[https://developers.google.com/google-ads/api/docs/keyword-planning/overview](https://developers.google.com/google-ads/api/docs/keyword-planning/overview)

Type: official ad-platform docs. Version: live page; no immutable release ID exposed. Inspection: relevant documentation/abstract sections inspected.

Keyword metrics and forecasts have account/rate limits and refresh schedules; search volume is not product demand conversion.

## DA18 — Elicit review workflow

[https://support.elicit.com/en/articles/14759154-systematic-reviews-in-elicit](https://support.elicit.com/en/articles/14759154-systematic-reviews-in-elicit)

Type: official provider documentation. Version: 2026-09-16. Inspection: official search-retrieved relevant sections; no authenticated API call.

Screening, extraction and review exports are documented; limits and dual-review access depend on plan. Vendor time-saving claims are not independent evidence.

## DA19 — Elicit pricing

[https://elicit.com/pricing](https://elicit.com/pricing)

Type: official provider documentation. Version: live pricing as accessed. Inspection: official search-retrieved relevant sections; no authenticated API call.

Pro annual billing is advertised at USD 468 per user per year (USD 39 monthly equivalent); API access and usage allowances are plan-dependent.

## DA20 — Elicit API

[https://docs.elicit.com/](https://docs.elicit.com/)

Type: official provider documentation. Version: API v2 routes observed. Inspection: official search-retrieved relevant sections; no authenticated API call.

Systematic-review sessions are asynchronous; stages and higher-usage options must be selected explicitly.

## DA21 — UN Comtrade API

[https://uncomtrade.org/docs/un-comtrade-api/](https://uncomtrade.org/docs/un-comtrade-api/)

Type: official provider documentation. Version: live documentation. Inspection: official search-retrieved relevant sections; no authenticated API call.

Limited preview routes are keyless; broader endpoints require registration/key. Trade data is national statistical reporting, not supplier certification.

## DA22 — UN Comtrade subscriptions

[https://comtradeplus.un.org/Subscriptions](https://comtradeplus.un.org/Subscriptions)

Type: official provider documentation. Version: live plan table. Inspection: official search-retrieved relevant sections; no authenticated API call.

Free registered access and paid premium tiers differ in record and request limits; institutional entitlement must be verified.

## DA23 — Meta Ad Library API

[https://br-fr.facebook.com/ads/library/api/?source=onboarding](https://br-fr.facebook.com/ads/library/api/?source=onboarding)

Type: official provider documentation. Version: live API overview. Inspection: official search-retrieved relevant sections; no authenticated API call.

API coverage differs from the public ad library: worldwide political/social-issue ads and broader UK/EU ad coverage have separate windows. Authorization is required.

## DA24 — Google Trends data

[https://support.google.com/trends/answer/4365533?hl=en](https://support.google.com/trends/answer/4365533?hl=en)

Type: official provider documentation. Version: live methodology. Inspection: official search-retrieved relevant sections; no authenticated API call.

Search-interest samples are normalized to geography/time and scaled 0–100; they are not absolute volumes or representative consumer surveys.

## DA25 — Reddit Responsible Builder Policy

[https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy)

Type: official provider documentation. Version: current policy inspected. Inspection: official search-retrieved relevant sections; no authenticated API call.

Approved access and the specified researcher program are required by current provider policy. Public visibility is not permission for unrestricted automated collection.

## DA26 — Alibaba Verified Suppliers

[https://activity.alibaba.com/page/verifiedsuppliers.html](https://activity.alibaba.com/page/verifiedsuppliers.html)

Type: official provider documentation. Version: live provider statement. Inspection: official search-retrieved relevant sections; no authenticated API call.

Third-party supplier assessments are discovery evidence; provider disclaims guarantees of product/certificate authenticity.

## DA27 — Semantic Scholar Academic Graph

[https://api.semanticscholar.org/api-docs](https://api.semanticscholar.org/api-docs)

Type: official provider documentation. Version: live API docs. Inspection: official search-retrieved relevant sections; no authenticated API call.

Academic graph supports paper/author/citation discovery; metadata is not full-text or claim verification.

## DA28 — NCBI developer APIs

[https://www.ncbi.nlm.nih.gov/home/develop/api/](https://www.ncbi.nlm.nih.gov/home/develop/api/)

Type: official provider documentation. Version: live API index. Inspection: official search-retrieved relevant sections; no authenticated API call.

E-utilities provide programmatic Entrez including PubMed access; inspect record types and lawful full-text routes.


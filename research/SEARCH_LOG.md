# Investigation log and access boundaries

Date: 2026-11-03. Tools: supplied web search service (two search engines) and page retrieval; local Python/file tools. No credentials, paid APIs, live Claude CLI or commercial subscriptions were used. Search result dates were checked against current pages when material.

| Investigation | Representative queries/routes | Outcome |
|---|---|---|
| Claude features | Official memory, skills, sub-agents, teams, settings, hooks, MCP, security, CLI, monitoring, sandboxing, costs, plugins, model-config pages | Relevant documentation retrieved; skill grants and memory write permissions corrected; teams remain experimental. |
| Models/research systems | Official Anthropic/OpenAI/Gemini model and research docs; Perplexity Agent/Search migration; Parallel Task basis | Vendor functionality documented; no API performance tests. |
| Multi-agent evidence | “Towards a Science of Scaling Agent Systems”; Anthropic multi-agent engineering; LangGraph persistence, Agents SDK, AutoGen, CrewAI flows | Latest paper v3 inspected; earlier search snippet described an older experiment version. No universal agent-count rule adopted. |
| Research evaluation | BrowseComp; DeepResearch Bench and II; FActScore; ALCE; DeepTRACE; LiveResearchBench; DeepFact; Who is the Agent to Blame | Benchmarks measure different constructs; current prototype references independently corroborated where used. |
| Research methods | PRISMA 2020/PRISMA-S; Cochrane search; GRADE; What If; forecasting evaluation; Green Book | Generalizable principles separated from clinical/appraisal-specific rules. |
| Data/tools | Crossref/OpenAlex, SEC, SP-API, Shopify, StatCan, Census, UAE, World Bank, Keepa, Jungle Scout, Similarweb, Tavily, Firecrawl, EPO, Google Ads | Official sources inspected; provider discovery distinguished from connections. |
| Security/reliability | NIST AI 600-1, MCP draft security, Claude permissions/sandboxing, SQLite atomic commit/backup | No executable MCP or network hooks enabled; local transaction and path controls implemented. |

Access failures: NCBI E-utilities book page returned a browser challenge; Exa overview was inaccessible through the browsing tool; World Bank API root returned 404, so the official Indicators documentation was used instead. These were not treated as proof that the providers are unavailable generally. No challenge or authentication boundary was bypassed.

Parallel delegation was real: five specialists were started. The original auditor completed full reading and 17 baseline checks; the Claude researcher returned preliminary official-doc findings. All five stopped after an account usage limit before final assignments. The primary agent completed the implementation and remaining research directly. No completed independent post-implementation audit or parallel model benchmark is claimed.

Source version reconciliation: arXiv 2512.08296 search output reflected 180 configurations and an earlier R²; the opened v3 reports 260 configurations/six benchmarks and different fit. The report uses qualitative conclusions from v3, not the outdated numerical snippet. Gemini research previews and general-model catalog are distinct products. Current Perplexity docs replace old Sonar-centered assumptions. Bibliographic and pricing claims are dated, not perpetual.

Additional coverage: official Elicit workflow/API/pricing; UN Comtrade API/tiers; Meta Ad Library scope; Google Trends normalization; Reddit current approved-access policy; Alibaba assessment disclaimers; Semantic Scholar API; alternative NCBI developer API index. The NCBI index was accessible even though the earlier book page was challenged. These were documentation/search retrievals, not API tests.

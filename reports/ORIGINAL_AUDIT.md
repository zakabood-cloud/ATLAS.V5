# Complete original repository forensic audit

Audit date: 2026-11-03. All **40 original files** were completely read and accounted for. The master was inspected in contiguous ranges 1–240, 241–480, 481–720, 721–960, 961–1200 and 1201–1451. Its 36 embedded payloads were separately compared to delivered files; every pair was byte-identical. The two executable helpers were inspected at source level and executed in an isolated baseline copy. Nothing in the original extraction was edited.

The untouched supplied ZIP is [ORIGINAL_ATLAS_UNMODIFIED.zip](../reference/ORIGINAL_ATLAS_UNMODIFIED.zip). SHA-256: `eac11cdf83ce79808ac31d449efad6fea9ca74ff2744097858a527a44242e9c3`. The [original manifest](../reference/original_manifest.json) includes each path, byte count, line count and full hash. “Remove” below means remove from the active upgraded layout, never delete from the historical archive.

Machine-readable matrices: [CSV](original_audit_matrix.csv) and [JSON](original_audit_matrix.json). Each has responsibility, actual behavior, dependencies, conventions, executability, duplication, contradictions, dated/unverified assumptions, security/reliability, disposition, replacement and verification. This Markdown version is the readable view of the same records.

## Consequential findings

- The prototype is mostly an instruction system: two executable scripts totaling 130 lines, no supplied test suite, no implemented transition engine or quantitative toolkit.
- Both original scripts correctly warn that their checks do not prove research truth. The problem is the mismatch between ambitious procedural gates and their limited enforcement, not an explicit promise by those scripts to solve factual verification.
- The original installer passes malformed YAML, invalid Python and meaningless policy content. The project auditor passes an arbitrary state, fabricated `.invalid` source with self-declared V2, missing source references on a critical claim, blank IDs and empty completion artifacts in the tested cases. Some duplicate/missing-reference/corrupted-state checks work.
- Original evidence, intake, uncertainty and memory principles are worth retaining. The reconstruction implements selected controls and consolidates duplication; it does not claim to have invented those principles.
- The 2026 research references used from the prototype were checked against publisher/proceedings pages. Recent or unfamiliar references were not automatically labeled fabricated.
- All original specialist agents inherit tools without a restrictive `tools` list. Three request project memory. Current documentation indicates memory can grant writing, making it inappropriate as a default for a strictly read-only reviewer.

The completed baseline details are [baseline_results.json](baseline_results.json). These findings measure deterministic checker behavior, not the research performance of a real Claude session.

## File-by-file findings

### 01. `.claude/agent-memory/.gitignore`

170 bytes; 4 lines; SHA-256 `6aa5a4fd3e6a3b4cd2c872b9266d0a23c7efa3f95d48b536b27c86f41857cbbc`.

- **Responsibility:** Avoid committing persistent agent notes
- **Actual implementation:** Ignores generated agent-memory contents while retaining the ignore file.
- **Dependencies:** Three agents request project memory.
- **Claude conventions:** Repository ignore rules; project agent memory itself is supported.
- **Executability:** Git pattern configuration, not a research action.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Git behavior stable; actual generated agent-memory paths untested.
- **Security/reliability:** Git ignore is not encryption, access control or a retention mechanism.
- **Disposition:** merge
- **Replacement:** .gitignore and controlled memory/
- **Verification:** Release avoids automatic agent memory; secret/private artifact exclusions reviewed.

### 02. `.claude/agents/adversarial-reviewer.md`

989 bytes; 6 lines; SHA-256 `db96e7e1e351fe3a3bb837d78580c9830a60a78441534f3f4924bacf986977c5`.

- **Responsibility:** Adversarial Reviewer specialist
- **Actual implementation:** Requests independent counterevidence, alternative explanations, rank-reversal conditions and a stronger opposing interpretation.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; no explicit tools field.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. Independence is an instruction, not authenticated isolation.
- **Disposition:** rewrite
- **Replacement:** .claude/agents/adversarial-reviewer.md
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 03. `.claude/agents/domain-researcher.md`

978 bytes; 6 lines; SHA-256 `306631307ed66484316e56e2ebe5157496fa712dda461cf2ab428cc96514e203`.

- **Responsibility:** Domain Researcher specialist
- **Actual implementation:** Requests a neutral bounded branch with original sources, atomic claims, exceptions, dates and independence groups.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; no explicit tools field.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. Independence is an instruction, not authenticated isolation.
- **Disposition:** rewrite
- **Replacement:** .claude/agents/domain-researcher.md
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 04. `.claude/agents/evidence-auditor.md`

963 bytes; 6 lines; SHA-256 `ccbb96389a9eec31e42587be3cb5d007f85aa6c1c98ac0efdeac5679231bf71b`.

- **Responsibility:** Evidence Auditor specialist
- **Actual implementation:** Requests direct source-to-claim inspection, uncertainty and V0/V1/V2/V3 statuses; no automated entailment procedure.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; no explicit tools field.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. Independence is an instruction, not authenticated isolation.
- **Disposition:** rewrite
- **Replacement:** .claude/agents/evidence-reviewer.md
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 05. `.claude/agents/methodology-architect.md`

1,143 bytes; 7 lines; SHA-256 `467111bd85280758de1c7f6b17d16b73a4311243a3044ffb16d96ccad2ae86c2`.

- **Responsibility:** Methodology Architect specialist
- **Actual implementation:** Requires Phase 0 method comparison and protocol; enables project memory and points to constitution/playbooks.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; project memory documented.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. memory: project also enables writing; advisory memory can retain unreviewed observations.
- **Disposition:** rewrite
- **Replacement:** .claude/agents/methodology-architect.md
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 06. `.claude/agents/quantitative-analyst.md`

1,037 bytes; 6 lines; SHA-256 `30e56f8a0e19f9b7bb7d85a87ee7b56fe36898d4cc5deb867bb66ae24dee958d`.

- **Responsibility:** Quantitative Analyst specialist
- **Actual implementation:** Requests reproducible domain calculations, boundary checks and assumptions; supplies no calculator itself.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; no explicit tools field.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. Independence is an instruction, not authenticated isolation.
- **Disposition:** rewrite
- **Replacement:** .claude/agents/quantitative-analyst.md
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 07. `.claude/agents/report-synthesizer.md`

909 bytes; 6 lines; SHA-256 `3ecbd73fd1d0633d847c6fd4bc6987d9e4873099eb02a39ec6a4833c7d46ece6`.

- **Responsibility:** Report Synthesizer specialist
- **Actual implementation:** Requests contract-based synthesis of audited claims and actual files; no format renderer or manifest validator.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; no explicit tools field.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. Independence is an instruction, not authenticated isolation.
- **Disposition:** merge
- **Replacement:** atlas-deliver skill and coordinator
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 08. `.claude/agents/source-intelligence.md`

962 bytes; 7 lines; SHA-256 `e9105e177d7b01ab092c0bb8ba2f27070aaecd22b4bde8d5dc3598a6a80d7399`.

- **Responsibility:** Source Intelligence specialist
- **Actual implementation:** Requests source landscape, original origins, access and uncertainty metadata; enables project memory.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; project memory documented.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. memory: project also enables writing; advisory memory can retain unreviewed observations.
- **Disposition:** merge
- **Replacement:** methodology-architect and domain-researcher
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 09. `.claude/agents/tool-mcp-architect.md`

953 bytes; 7 lines; SHA-256 `52dd58f48d9f63dbdbe35dc54dc0cfe2a67a1a8af23204cf78ff2616af97f739`.

- **Responsibility:** Tool Mcp Architect specialist
- **Actual implementation:** Requests official-document/tool pilots and permission checks; enables project memory; provides no API adapter.
- **Dependencies:** Called by stage skills; relies on policy and project artifacts; model inherit.
- **Claude conventions:** Valid documented .claude/agents Markdown frontmatter; model inherit supported; project memory documented.
- **Executability:** Claude custom-agent instruction, not a standalone program; no live agent run available.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No explicit tool restriction; inherits available tools. memory: project also enables writing; advisory memory can retain unreviewed observations.
- **Disposition:** merge
- **Replacement:** atlas-meta skill and capability registry
- **Verification:** New agent metadata/tool restrictions statically checked; no live isolation test.

### 10. `.claude/skills/research-audit/SKILL.md`

3,818 bytes; 35 lines; SHA-256 `ffc007a1139e9b7fc3bdaa424eb878d7d6d8f93019a32adeb7807b335fd5e732`.

- **Responsibility:** Independent verification
- **Actual implementation:** Directs exact source checks, quantitative replication, coverage and adversarial review; calls weak baseline script.
- **Dependencies:** CLAUDE.md routes stage; research_os policies/templates and relevant agents supply details.
- **Claude conventions:** Valid documented skill directory and name/description frontmatter; no live invocation test.
- **Executability:** Actionable Claude procedure; stage obedience and output quality were not enforced by original scripts.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Instruction compliance depends on Claude; no executable enforcement.
- **Disposition:** rewrite
- **Replacement:** methods/VERIFICATION.md; atlas/evidence.py; .claude/skills/atlas-audit/SKILL.md
- **Verification:** New gates tested; conversation relevance/quality requires real Claude evaluation.

### 11. `.claude/skills/research-deliver/SKILL.md`

3,664 bytes; 41 lines; SHA-256 `24cdeec4448ba8b74929248962bdb84ec257641232d25f457c1bee05f38f9784`.

- **Responsibility:** Deliverable production
- **Actual implementation:** Requests specified formats, audit appendix, limitations and file validation; no executable renderer.
- **Dependencies:** CLAUDE.md routes stage; research_os policies/templates and relevant agents supply details.
- **Claude conventions:** Valid documented skill directory and name/description frontmatter; no live invocation test.
- **Executability:** Actionable Claude procedure; stage obedience and output quality were not enforced by original scripts.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Instruction compliance depends on Claude; no executable enforcement.
- **Disposition:** rewrite
- **Replacement:** .claude/skills/atlas-deliver/SKILL.md; synthesis/delivery gates
- **Verification:** New gates tested; conversation relevance/quality requires real Claude evaluation.

### 12. `.claude/skills/research-execute/SKILL.md`

3,726 bytes; 31 lines; SHA-256 `5ea3312264ef96e7858e030c0cb05be07d082bb5a324ac997c02c5a61270dc81`.

- **Responsibility:** Substantive research orchestration
- **Actual implementation:** Directs task branches, iterative search, extraction, quantitative work and records; no task scheduler.
- **Dependencies:** CLAUDE.md routes stage; research_os policies/templates and relevant agents supply details.
- **Claude conventions:** Valid documented skill directory and name/description frontmatter; no live invocation test.
- **Executability:** Actionable Claude procedure; stage obedience and output quality were not enforced by original scripts.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Instruction compliance depends on Claude; no executable enforcement.
- **Disposition:** rewrite
- **Replacement:** methods/ORCHESTRATION.md; .claude/skills/atlas-run/SKILL.md; task DAG/ledger
- **Verification:** New gates tested; conversation relevance/quality requires real Claude evaluation.

### 13. `.claude/skills/research-intake/SKILL.md`

5,604 bytes; 33 lines; SHA-256 `f132b7ab2e7e62f4be30bc8d6237a4278077971a58b10a2bf31a8ea885b61533`.

- **Responsibility:** Adaptive clarification
- **Actual implementation:** Detailed interview-first procedure with question bank, explicit deliverables and project-artifact instructions.
- **Dependencies:** CLAUDE.md routes stage; research_os policies/templates and relevant agents supply details.
- **Claude conventions:** Valid documented skill directory and name/description frontmatter; no live invocation test.
- **Executability:** Actionable Claude procedure; stage obedience and output quality were not enforced by original scripts.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Instruction compliance depends on Claude; no executable enforcement.
- **Disposition:** rewrite
- **Replacement:** methods/INTAKE.md; atlas/intake.py; atlas/project.py; .claude/skills/atlas-research/SKILL.md
- **Verification:** New gates tested; conversation relevance/quality requires real Claude evaluation.

### 14. `.claude/skills/research-memory/SKILL.md`

2,629 bytes; 28 lines; SHA-256 `53525e641c8970cfc188a2e1857dc0a07f769db7b0be6d873b9328b0ef2535b4`.

- **Responsibility:** Method memory consolidation
- **Actual implementation:** Requests reviewed lessons, controlled proposals and no automatic universal factual memory.
- **Dependencies:** CLAUDE.md routes stage; research_os policies/templates and relevant agents supply details.
- **Claude conventions:** Valid documented skill directory and name/description frontmatter; no live invocation test.
- **Executability:** Actionable Claude procedure; stage obedience and output quality were not enforced by original scripts.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Instruction compliance depends on Claude; no executable enforcement.
- **Disposition:** merge
- **Replacement:** atlas/memory.py; memory/README.md; delivery skill
- **Verification:** New gates tested; conversation relevance/quality requires real Claude evaluation.

### 15. `.claude/skills/research-meta/SKILL.md`

5,816 bytes; 47 lines; SHA-256 `e24313047884063ff3cb9efbd4a813dc7c43f0eb0c64ee0d5031a6ad9671ea89`.

- **Responsibility:** Methodological investigation
- **Actual implementation:** Phase 0 methods/tools/source comparison, pilots, readiness and protocol freeze in prose.
- **Dependencies:** CLAUDE.md routes stage; research_os policies/templates and relevant agents supply details.
- **Claude conventions:** Valid documented skill directory and name/description frontmatter; no live invocation test.
- **Executability:** Actionable Claude procedure; stage obedience and output quality were not enforced by original scripts.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Instruction compliance depends on Claude; no executable enforcement.
- **Disposition:** rewrite
- **Replacement:** methods/RESEARCH_PROTOCOL.md; .claude/skills/atlas-meta/SKILL.md; READINESS gate
- **Verification:** New gates tested; conversation relevance/quality requires real Claude evaluation.

### 16. `.gitignore`

314 bytes; 15 lines; SHA-256 `e70087d480bec19ea72e9ace2938e1eacabf0b57bdbc6aba427a3592157f60d6`.

- **Responsibility:** Exclude generated/private project data
- **Actual implementation:** Ignores projects, state, local settings, MCP/environment data and caches according to supplied patterns.
- **Dependencies:** Nested project/state/agent-memory ignore files overlap.
- **Claude conventions:** Normal repository convention.
- **Executability:** Git configuration.
- **Duplication:** Not an embedded payload; overlaps entry/ignore/documentation responsibilities where noted.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Pattern semantics stable; privacy effectiveness not experimentally established.
- **Security/reliability:** Does not prevent secrets being written, uploaded or manually tracked.
- **Disposition:** merge
- **Replacement:** .gitignore
- **Verification:** Release contents inspected; runtime artifacts excluded.

### 17. `CLAUDE.md`

5,001 bytes; 41 lines; SHA-256 `72dd0dea16ccbe5f6e9da72a003ab1b7c4c8aff2bf7966ca69e9a660d96826bb`.

- **Responsibility:** Always-loaded routing and invariants
- **Actual implementation:** 41-line instruction file with long lines; defines initialize/stop, intake and modular research rules.
- **Dependencies:** Master installer, research_os guide, state machine, skills and policies.
- **Claude conventions:** Correct root instruction filename and under original 200-line heuristic; line count alone does not measure context cost.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Says bootstrap controlled by master while README says master is not needed in normal use.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Procedural state and readiness claims can diverge from actual work; bootstrap depends on redundant master.
- **Disposition:** rewrite
- **Replacement:** CLAUDE.md; .claude/rules/evidence.md
- **Verification:** Initialization and routing contract tests; real first-session behavior unverified.

### 18. `README.md`

3,667 bytes; 49 lines; SHA-256 `ce01eaa7bdf46c5d7a19029de3c0361057d69a25f7483b96bbd99cee74dfac50`.

- **Responsibility:** Installation and overview
- **Actual implementation:** Describes ready repository, usage and smoke checks, with honest caveats about tool verification.
- **Dependencies:** START_HERE, master, CLAUDE and installation scripts.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Not an embedded payload; overlaps entry/ignore/documentation responsibilities where noted.
- **Contradictions/ambiguity:** Master optional statement conflicts with CLAUDE bootstrap routing.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Easy to mistake file installation check for full compatibility; no tested runtime version pinned.
- **Disposition:** rewrite
- **Replacement:** README.md; docs/USAGE.md
- **Verification:** All local links and first-command instructions checked; live client unavailable.

### 19. `START_HERE.txt`

802 bytes; 12 lines; SHA-256 `2be54a099aac498f28b3478750a88fe94c49bb23cce284dec538ba9d4720cf1d`.

- **Responsibility:** Quick-start entry
- **Actual implementation:** Short extraction/open/first-instruction guide.
- **Dependencies:** README, master and CLAUDE.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Not an embedded payload; overlaps entry/ignore/documentation responsibilities where noted.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Duplicate entry instructions can drift.
- **Disposition:** merge
- **Replacement:** README.md; docs/USAGE.md
- **Verification:** One canonical first command /atlas-init documented.

### 20. `ULTIMATE_CLAUDE_RESEARCH_OS_MASTER.md`

133,432 bytes; 1451 lines; SHA-256 `3d8f762a42202b31cfede59f2b0d95a9a34cf283414a7cb4385132f0718979aa`.

- **Responsibility:** Monolithic bootstrap specification
- **Actual implementation:** 1451 lines; embeds 36 payloads verified byte-identical to delivered files, plus setup/operating directions.
- **Dependencies:** Duplicates most active files including agents, skills, policies and scripts.
- **Claude conventions:** Root Markdown is not automatically a project instruction file; loading it explicitly consumes context.
- **Executability:** Contains code payloads and instructions; not a directly executed autonomous installer.
- **Duplication:** Contains 36 byte-identical embedded file payloads.
- **Contradictions/ambiguity:** Its bootstrap role conflicts with README optionality; installed payloads are already present.
- **Dated or unverified:** References and feature assumptions need individual verification; no universal performance evidence.
- **Security/reliability:** Large duplicated authority, maintenance drift, context overhead; not a working engine or test suite.
- **Disposition:** remove from active runtime; preserve unchanged
- **Replacement:** reference/ORIGINAL_ATLAS_UNMODIFIED.zip only
- **Verification:** reports/master_payload_comparison.json; all 36 payload comparisons true.

### 21. `research_os/README.md`

2,924 bytes; 40 lines; SHA-256 `50d5c1e82906f6495c70465bcac9d97896c5b506354c579a8d82c0d5e58fe9fc`.

- **Responsibility:** Internal operating guide
- **Actual implementation:** Summarizes architecture, stages and dependency on multiple policy files.
- **Dependencies:** CLAUDE, skills, state machine, domain/template files.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Prose descriptions can be mistaken for implemented machinery.
- **Disposition:** merge
- **Replacement:** docs/USAGE.md; reports/ARCHITECTURE.md
- **Verification:** Stage and artifact regression tests; live Claude behavior unverified.

### 22. `research_os/domains/DOMAIN_PLAYBOOKS.md`

6,448 bytes; 33 lines; SHA-256 `aef0063841fa71140e8496e6e7251e878633c506fa7564fe4db084655df494dc`.

- **Responsibility:** Domain-specific methods
- **Actual implementation:** Compact guidance for commerce, comparative markets, opportunity, finance/science/technology and factual work.
- **Dependencies:** Intake, meta skill and statistical/source policies.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Appropriate guidance but no machine-selectable profile or domain regression cases.
- **Disposition:** rewrite
- **Replacement:** methods/domains.json; methods/RESEARCH_PROTOCOL.md
- **Verification:** Eight domain profile/intake tests and held-out live-case specification.

### 23. `research_os/engine/audit_project.py`

3,769 bytes; 69 lines; SHA-256 `50580a2e85c6a08dcc7285d5ed957de166a1aae3ebc750188f1bed6ba3b69a5d`.

- **Responsibility:** Conservative project audit
- **Actual implementation:** 69-line stdlib CSV/JSON checker: duplicate IDs, missing references, critical status labels and three completion-path existence checks.
- **Dependencies:** Free-form state.json, source_registry.csv, claim_ledger.csv and delivery paths.
- **Claude conventions:** Ordinary Python audit tool; no Claude runtime binding.
- **Executability:** Actually executed; detects some malformed state, missing reference, duplicate ID and unverified-status cases.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Policy requires stronger verification than code checks; declaration of stage/status is not evidence.
- **Dated or unverified:** No external capability or quality measured; warning correctly disclaims truth oracle.
- **Security/reliability:** Accepts arbitrary stage, empty critical source references, .invalid URLs and self-attested V2; completion files can be empty. No snapshot/excerpt/calculation/semantic verification.
- **Disposition:** rewrite
- **Replacement:** atlas/project.py; atlas/evidence.py
- **Verification:** Original adversarial baseline and paired same-defect cases; provenance/state tests.

### 24. `research_os/engine/verify_install.py`

2,937 bytes; 61 lines; SHA-256 `4d0f73dfc7741e54424bd919d0de79caeda6041b3d5124e120109d5bf578a129`.

- **Responsibility:** Installation smoke check
- **Actual implementation:** 61-line stdlib script: 32 required files >=40 bytes, frontmatter delimiters, root CLAUDE line count; exits on issues.
- **Dependencies:** Hardcoded MANDATORY file list and current root.
- **Claude conventions:** Compatible ordinary Python helper; not a Claude integration test.
- **Executability:** Actually executed with Python 3.12.14; basic valid/missing-file checks work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Output says skill frontmatter OK while only fence delimiters are checked; script warning limits interpretation.
- **Dated or unverified:** Claims Python 3.9+; actually tested here only 3.12.14.
- **Security/reliability:** Accepts invalid YAML contents and invalid Python; does not check links, schema, tools or executable behavior.
- **Disposition:** rewrite
- **Replacement:** atlas/structure.py; atlas init/check
- **Verification:** Original 17-case run, paired comparison, AST/frontmatter/link/init regressions.

### 25. `research_os/evaluations/EVALUATION_PROTOCOL.md`

3,332 bytes; 33 lines; SHA-256 `be457fe30d207621cdfa06d30a5a88120a806a809e536f417a204ff31d045bdb`.

- **Responsibility:** Evaluation framework
- **Actual implementation:** Proposes multidimensional evaluation and honest limitations; no fixtures or runner included.
- **Dependencies:** References other policies and REFERENCE_LIBRARY.md.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Bare REFERENCE_LIBRARY.md path is wrong relative to evaluations directory.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Metrics without executable tests allow unmeasured success claims.
- **Disposition:** rewrite
- **Replacement:** benchmarks/PROTOCOL.md; benchmarks/cases.json; tests/; reports/TESTING.md
- **Verification:** Actual test receipts plus unrun live evaluation protocol; no invented scores.

### 26. `research_os/intake/QUESTION_BANK.md`

13,491 bytes; 179 lines; SHA-256 `8684206fb4c8c72ed5190a76f8d55b4c325a699b74c657194780ee1bb50d423b`.

- **Responsibility:** Comprehensive intake bank
- **Actual implementation:** 179 lines of core and domain prompts, with batching and adaptation guidance.
- **Dependencies:** research-intake skill and domain playbooks.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Suggested 12–25-question batches/rounds may look like a quota; text also requires adaptation, so not a strict hard cap.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No persistence or enforcement of answers/deliverables; length targets can distract from relevance.
- **Disposition:** rewrite
- **Replacement:** atlas/intake.py; methods/domains.json; methods/INTAKE.md
- **Verification:** Partial/explicit-end/adaptive/essential/deliverable tests; real interview quality unmeasured.

### 27. `research_os/methods/MEMORY_POLICY.md`

2,138 bytes; 19 lines; SHA-256 `e3527e1e89d26342719822f22fb8b1570058d7f592397f9c5b2d7a250bf321bc`.

- **Responsibility:** Separate project evidence and reusable methods
- **Actual implementation:** Defines four memory layers, validation states, versioning, confidentiality and evaluation principles.
- **Dependencies:** research-memory and three memory-enabled agents.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction; advisory subagent memory is broader than the later controlled method store.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No promotion validator, history writer, expiry reader or executable retention control.
- **Disposition:** rewrite
- **Replacement:** atlas/memory.py; memory/README.md
- **Verification:** Receipt/hash/reviewer/version/expiry/query tests.

### 28. `research_os/methods/METHODS_INDEX.md`

538 bytes; 12 lines; SHA-256 `03320827505271f857f7acbf034872c7674d768062e3c17b28aa20c879eba795`.

- **Responsibility:** Index reusable methods
- **Actual implementation:** Short initial methodology index; does not implement retrieval or maintain evaluated entries.
- **Dependencies:** MEMORY_POLICY and research-memory.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** A method index is not proof of validated reusable knowledge.
- **Disposition:** replace
- **Replacement:** memory/README.md; atlas/memory.py
- **Verification:** Explicitly empty initial active memory; no fabricated validated lessons.

### 29. `research_os/operations/STATE_MACHINE.md`

3,929 bytes; 37 lines; SHA-256 `4cb697e4cf4e3eff0c01b7fdbd21e249ed0a4f1dac08711c5130f7b711518619`.

- **Responsibility:** Lifecycle and resumption contract
- **Actual implementation:** Describes stages, JSON state keys, stop rules, blockers/pause/cancellation and sequential gates.
- **Dependencies:** State JSON, stage skills and quality policies.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Declared hard transitions are instructions only; arbitrary stages still pass original script.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No transition API or atomic update implementation; audit does not validate stage enumeration.
- **Disposition:** rewrite
- **Replacement:** atlas/project.py; docs/SCHEMAS.md
- **Verification:** Sequential gates, holds, reopening, tampering, task dependencies and recovery tests.

### 30. `research_os/policies/CLAIM_AND_DATA_STANDARDS.md`

3,815 bytes; 34 lines; SHA-256 `66088cbfaecdc0f84e67d94dfd038cb1874099eacb1355c43ee925a83b0df18e`.

- **Responsibility:** Claim/evidence rigor
- **Actual implementation:** Defines claim verification levels, provenance, data context and limitations.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** V2/V3 labels are operator supplied and accepted without excerpt or calculation proof.
- **Disposition:** merge and implement
- **Replacement:** atlas/evidence.py; methods/VERIFICATION.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 31. `research_os/policies/DECISION_AND_STATISTICS.md`

3,941 bytes; 40 lines; SHA-256 `cbae81be382dd27152141a27e2813d275da5eee09da13ba14615657b67c93bab`.

- **Responsibility:** Quantitative decision quality
- **Actual implementation:** Describes uncertainty, scenario analysis, unit economics, statistical and causal cautions.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** No executable calculator or independent numerical regression suite.
- **Disposition:** merge and implement
- **Replacement:** atlas/quant.py; examples/; methods/RESEARCH_PROTOCOL.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 32. `research_os/policies/ORCHESTRATION_AND_SEARCH.md`

5,041 bytes; 43 lines; SHA-256 `e5d29dc16565cf7108e8dc719cf3202f3069db60b24e1758c0a70f1a29fc0c4c`.

- **Responsibility:** Search and multi-agent organization
- **Actual implementation:** Proposes source-aware search, branching, handoffs, budgets and stopping.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** No DAG validation, durable task ledger, bounded attempts or output verification.
- **Disposition:** merge and implement
- **Replacement:** atlas/project.py; methods/ORCHESTRATION.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 33. `research_os/policies/QUALITY_GATES.md`

3,792 bytes; 34 lines; SHA-256 `3e241b520c13961e6eef3efc6e48752f296a4ff10f69fc203b3374f46b90f3f7`.

- **Responsibility:** Research release acceptance
- **Actual implementation:** Describes method/readiness/research/audit/delivery quality standards.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** No transition implementation; file presence can be substituted for completed work.
- **Disposition:** merge and implement
- **Replacement:** atlas/project.py; benchmarks/PROTOCOL.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 34. `research_os/policies/REFERENCE_LIBRARY.md`

4,051 bytes; 33 lines; SHA-256 `10879efe3f41d6944593380354858b2c1ae439cfa0b47b5428ad6ab57d65a0f1`.

- **Responsibility:** Research and platform references
- **Actual implementation:** Dated curated reference list including Claude docs and contemporary research.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Relevant original modern references independently corroborated where used; no reference declared fake merely because recent. Remaining unused references stay only in original.
- **Security/reliability:** A bibliography does not establish that claims were checked or integrations tested.
- **Disposition:** replace with reverified dated register
- **Replacement:** research/sources.json; research/SOURCES.md; reports/RESEARCH_REVIEW.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 35. `research_os/policies/RESEARCH_CONSTITUTION.md`

5,174 bytes; 45 lines; SHA-256 `fa7a15d632b2c298e4460c57e9e70a5267ed385dd3cc689b2b0a7005cdff0a79`.

- **Responsibility:** Core research principles
- **Actual implementation:** Strong interview-first, method-first, evidence-quality, security and uncertainty principles.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** Good principles lack enforceable local receipts and can compete with duplicated master.
- **Disposition:** merge and implement
- **Replacement:** CLAUDE.md; methods/; docs/SECURITY.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 36. `research_os/policies/SECURITY_AND_PERMISSIONS.md`

3,091 bytes; 22 lines; SHA-256 `177f902d596622622ba21e3ff86b783e847d44e08b92b1c4ee7bb355b02f7a35`.

- **Responsibility:** Tool/data security
- **Actual implementation:** Explains untrusted sources, least privilege, sensitive data and approvals.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** No OS sandbox configured; unrestricted inherited agent tools remain possible.
- **Disposition:** merge and implement
- **Replacement:** docs/SECURITY.md; constrained agent metadata; atlas/io.py
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 37. `research_os/policies/TOOL_AND_SOURCE_INTELLIGENCE.md`

5,580 bytes; 45 lines; SHA-256 `4c9af1823e25d27c430f1d7dfc8b1048419dd1ee815471aec418cb9dbf831c31`.

- **Responsibility:** Tool selection and actual access
- **Actual implementation:** Specifies discovery, testing, geography, observed/estimated data, alternatives and access records.
- **Dependencies:** Referenced by CLAUDE, relevant stage skills, agents and templates.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Domain principles require current topic-specific sources; no empirical system superiority demonstrated.
- **Security/reliability:** No provider configuration/adapters or actual connection checks; candidate lists can be mistaken for access.
- **Disposition:** merge and implement
- **Replacement:** atlas/integrations.py; config/integrations.json; docs/INTEGRATIONS.md
- **Verification:** See improvement register for targeted controls; semantic policy quality requires review.

### 38. `research_os/projects/.gitignore`

179 bytes; 4 lines; SHA-256 `c417748adbcd8f2da77a125dc39a1e537eb2dfac434cc12466d1a49cc9a6e643`.

- **Responsibility:** Protect project artifacts from accidental commits
- **Actual implementation:** Ignores generated research project content.
- **Dependencies:** Root .gitignore and project schema.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Git ignore configuration.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Ignore patterns do not provide access controls, encryption or backups.
- **Disposition:** merge
- **Replacement:** .gitignore; projects/.gitkeep
- **Verification:** Release contains no user research projects.

### 39. `research_os/state/.gitignore`

100 bytes; 3 lines; SHA-256 `e3d579384dcc76dcc1319a3d7513c2524eff68acf2d4c4237cfe9dd5b31edfec`.

- **Responsibility:** Exclude local state
- **Actual implementation:** Ignores generated state files.
- **Dependencies:** State-machine JSON contract.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Git ignore configuration.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** No direct contradiction found in full-file review.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** No state store or recovery mechanism is implemented by ignore rules.
- **Disposition:** merge
- **Replacement:** .gitignore; per-project SQLite
- **Verification:** SQLite recovery tests.

### 40. `research_os/templates/PROJECT_SCHEMAS.md`

4,975 bytes; 110 lines; SHA-256 `53f4efc7180b3825e669fcacc0cc07b4d4311cdbea8887925c2c68796e07af85`.

- **Responsibility:** Project schema and report templates
- **Actual implementation:** 110-line directory plan, CSV column names, report/contract fields; tells agents not to create empty files just to pass.
- **Dependencies:** All stage skills, policies and original audit CSV names.
- **Claude conventions:** Ordinary Markdown; not a Claude executable extension.
- **Executability:** Procedural instructions only; Claude must perform and record the work.
- **Duplication:** Payload byte-identical in master archive and installed file.
- **Contradictions/ambiguity:** Explicit no-empty-placeholder instruction is stronger than original completion-file existence checks.
- **Dated or unverified:** Method guidance is plausible; actual research performance untested.
- **Security/reliability:** Schemas mostly unenforced; many artifacts can be asserted without content; no JSON parser constraints.
- **Disposition:** rewrite
- **Replacement:** docs/SCHEMAS.md; atlas/demo.py; examples/
- **Verification:** Strict JSON, artifact, output hash/nonempty and complete synthetic lifecycle tests.


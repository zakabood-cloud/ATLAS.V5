# Topic-specific access approval and risk-classified failure handling

After accepting the mandate and reviewing observable Copilot feature choices, access planning comes **before META or substantive research**. The goal is sufficient, decision-relevant access, not the largest tool list. No registry or model can be assumed to know every MCP server. ATLAS does not install servers, configure accounts, authenticate credentials, or intercept every Copilot tool.

## 1. Analyze the inquiry, then propose connections

1. Read the current mandate, domain, deliverables, privacy restrictions, and budget. Map each important measurement, source family, counterclaim, and verification need to coverage dimensions.
2. Run `python3 -m atlas access-needs PROJECT_ID` for offline capability prompts if useful. This is **not** live MCP discovery, an exhaustive inventory, or an approved plan.
3. Use currently available, authorized tools for focused access discovery: inspect official publisher documentation, relevant supported connector listings, and actual client capabilities. Do not collect topic findings or run a research pilot yet. A failure during discovery triggers the same stop rule below.
4. Compare existing built-in tools, local files/calculations, permitted manual exports, and MCP connectors. Select the minimal useful set; explain incremental coverage, missing sources, freshness, provenance, geographic fit, permissions, privacy, retention if known, and costs. Identify unverified candidates as unverified; never fabricate a publisher verification date.
5. Write `projects/PROJECT_ID/access_plan.json`. Present the plan to the user and **ask them to connect/approve before research**. Ask separately about paid use. No automatic installation, OAuth/account configuration, subscription, or credential collection.

An existing account, visible tool, or configuration entry is not user authorization. Do not transmit private repository content to a provider; connector approval does not override the mandate's data restrictions. Redact secrets from all receipts.

## 2. Access plan contract

The access plan uses `schema_version: 1` even in a state-schema-2 project:

- `question`: exactly the current inquiry from status.
- `coverage`: unique nonempty dimension strings.
- `selection_reason`: substantive comparison, including why more connectors would or would not help.
- `needs`: at least one item; a local-only project still declares its local capabilities.

Every need has:

| Field | Required content |
|---|---|
| `id`, `name`, `purpose` | Stable unique ID, capability name, and topic-specific purpose |
| `kind` | `mcp`, `builtin`, `local`, or `manual` |
| `endpoint` | Exact resource identifier; no credentials, query string, or fragment |
| `coverage` | Nonempty subset of plan dimensions; needs collectively cover the plan |
| `required`, `paid` | Actual booleans, not strings |
| `permissions` | Unique nonempty strings describing requested scopes |
| `data_shared`, `privacy`, `cost` | What leaves the environment, destination/risks, and known or uncertain charges |
| `alternatives`, `quality_impact` | Existing-tool/manual options and consequences of missing this access |
| MCP only | `publisher`, official public HTTPS `verification_url`, actual `publisher_verified_at` |

Publisher fields record the operator's verification, not a cryptographic trust decision. Verify executable package/version and transport where applicable. The validator cannot establish that a named server exists or that its documentation is genuine.

## 3. Record real user decisions

The user decides **every** need, including optional needs and local tools. A required need may be explicitly deferred, but the resulting evidence gap must remain visible; do not call the original scope fully feasible.

`decisions.json` is an object containing:

```json
{
  "decisions": [
    {"need_id": "local-analysis", "decision": "use", "reason": "User approved local analysis of supplied files"},
    {"need_id": "licensed-data", "decision": "defer", "reason": "User declined new paid access", "quality_impact": "Historical granular coverage remains unavailable"}
  ]
}
```

This illustrates the shape only; IDs and decisions must match the actual plan and conversation. A paid `use` decision additionally requires `paid_approved: true` backed by separate actual spending approval.

```sh
python3 -m atlas access-approve PROJECT_ID decisions.json --authorization 'ACTUAL USER INSTRUCTION'
python3 -m atlas access-status PROJECT_ID
```

Replace documentation placeholders with actual instructions; copied example text is not consent. Approval binds the exact plan bytes and resets test receipts. If the plan changes, obtain new approval and repeat the relevant tests before proceeding.

## 4. Test only after approval

The user connects the tool through their supported client/account controls. Then the operator performs a benign representative read-only test using the **actually available approved tool**. Do not simulate an MCP call, test private data with an external service, or label a configuration parse as authentication.

Save the observed receipt inside the project, for example `access-tests/local-analysis.json`:

```json
{
  "ok": true,
  "resource": "local:approved-repository",
  "operation": "read approved file",
  "observed_at": "ACTUAL_ISO_8601_TEST_TIME",
  "expires_at": "JUSTIFIED_FUTURE_ISO_8601_TIME",
  "limitations": "Describe exactly what was tested and what remains unverified"
}
```

The resource must match the approved endpoint. The observation must be after approval and not in the future; expiry must still be current. Include redacted tool results, source/version details, or output hashes as supporting fields/artifacts when useful. Choose validity based on the capability, not an arbitrary promise of permanent access.

```sh
python3 -m atlas access-test PROJECT_ID local-analysis access-tests/local-analysis.json
python3 -m atlas advance PROJECT_ID META
```

`access-test` validates and records a receipt; **it does not perform the tool call**. Local/human/client evidence remains operator-supplied, not authenticated by a JSON file. All decisions marked `use` need current, unchanged receipts at gated stages and task transitions. Expired access must be rechecked before further research.

### Bundled metadata adapter

Only Crossref and OpenAlex have bounded bibliographic metadata adapters. `--live` is an opt-in switch, not approval, provider-term compliance, or paid authorization. Requests require a previously approved endpoint and access need. Every attempted provider request is persisted under `projects/PROJECT_ID/retrieval/` as a bounded request plus result/error, and its hash is bound in the project state. Failures still create a global hold. There are no automatic retries, redirects, full-text downloads, or exhaustive-crawl claims.

An explicitly authorized preflight probe may be used for a narrow read-only connection check during `ENABLEMENT`, `META`, `READINESS` or `ORCHESTRATE`:

```sh
python3 -m atlas scholarly-search crossref 'EXACT APPROVED PROBE QUERY' \
  --project PROJECT_ID --need-id crossref-metadata --live --probe --limit 1
```

Probes are limited to one result and no cursor; they do not count as substantive research. They record an access receipt on success, but do not validate the provider's metadata or establish full-text access.

Substantive provider search is permitted only in `RESEARCH` and must match a query and ID already in the accepted protocol:

```sh
python3 -m atlas scholarly-search crossref 'EXACT PROTOCOL QUERY' \
  --project PROJECT_ID --need-id crossref-metadata --plan-id P1 --live --limit 10
```

Replace `P1` and the query with the exact planned pair. Record the returned `retrieval_artifact` in the corresponding `search_log.json` row together with the same `plan_id` and query. The VERIFY gate checks that every recorded retrieval receipt is linked to its matching log row, including failed attempts. Returned items are metadata leads only: inspect original sources, distinguish records from studies, and explicitly account for inclusions/exclusions. Provider counts and retraction flags are not proof of exhaustive discovery or full-text validity. No live provider test is claimed by this documentation.

## 5. Risk-based access failure handling

Every failed read, API request, extraction, tool permission, paywall or credential check must be recorded; determine the **decision impact** before deciding which work must pause. Use `--severity optional`, `critical` (default), or `security` when recording access-block. When impact is uncertain, use `critical` until investigated.

| Failure | Behavior | Final research gate |
|---|---|---|
| Security/privacy violation | Stop affected operations; project hold and escalation | No continuation without explicit resolution |
| Decision-critical missing evidence | Hold affected decisions and dependent work; unrelated work may continue only if the actual task runner allows it | Conditional/unverified conclusion until resolved or explicitly accepted gap |
| Optional source / duplicate corroboration unavailable | Record the failure and affected task, continue unrelated already-approved work | Open gap must remain visible; no false completeness claim |
| Transient network/rate-limit | No unapproved retry or credential changes; operator may authorize bounded retries under current permission policy | Record any unsuccessful attempts and downstream impact |

On every access failure preserve the exact resource, operation, observed error, need/task ID, data-quality impact and time. Workers report failures to the coordinator; the coordinator never assumes the local engine can cancel external jobs. For a **critical** block, record:

```sh
python3 -m atlas access-block PROJECT_ID \
  --resource 'EXACT_RESOURCE' --operation 'OPERATION' \
  --reason 'OBSERVED_ERROR' --quality-impact 'DECISION_IMPACT' \
  --severity critical
```

For an optional block, use `--severity optional`; this does **not** create a project-wide hold, but must still be recorded and assessed at the research and final decision gates. Security blocks use `--severity security`. User-approved substitutes or retries require their own scoped access and privacy authorization. Never silently skip material evidence. The Python CLI records block state, but cannot intercept every external Copilot or MCP tool.

## 6. Continue only within explicit scope

Ask whether the user wants the access restored/retested or accepts the stated gap. Never infer consent from silence, a generic earlier mandate, or a waiver from another project.

```sh
# Only after the user specifically authorizes retry:
python3 -m atlas resume PROJECT_ID --scope retry \
  --reason 'USER-APPROVED RETEST PURPOSE' --authorization 'ACTUAL USER INSTRUCTION'

# Alternatively, only after explicit acceptance of the loss of coverage:
python3 -m atlas resume PROJECT_ID --scope continue-with-gaps \
  --reason 'ACCEPTED GAP AND CONSEQUENCES' --authorization 'ACTUAL USER INSTRUCTION'
```

Retry authorization **does not clear the hold**. Only resource/operation-matching access tests are allowed; general work remains blocked. A successful receipt must follow the retry authorization and resolves its matching access block. Other unresolved blocks keep the project held.

Accepted-gap continuation records `user_accepted_gap`, defers matching access needs, and clears the relevant hold. It does not convert blocked work into successful research. Keep the blocked search in the log, tie it to `access_block_id`, report the coverage/decision impact, and reopen/amend affected protocol or tasks before new work. New replacement tools need their own approval and tests. Critical gaps may leave the answer conditional or nonfinal.

The current CLI records authorization text but cannot authenticate who said it or cancel external jobs. The coordinator must preserve truthful provenance and enforce the user's scope in the actual client.

### External Copilot tool blocks without a planned need

When an actual Copilot/MCP/client tool is blocked without a planned `need_id`, record it with the appropriate severity. Stop affected/dependent tasks when critical; for optional failures, unrelated authorized work may proceed. After explicit user retry authorization, only that exact resource/operation may be retried. Save an operator receipt inside the project, for example:

```json
{
  "ok": true,
  "resource": "EXACT BLOCKED RESOURCE",
  "operation": "EXACT BLOCKED OPERATION",
  "observed_at": "ACTUAL POST-AUTHORIZATION ISO-8601 TIME",
  "method": "Describe the actual limited read-only observation",
  "limitations": "Operator-recorded; not independently authenticated by Python"
}
```

Then resolve that one block:

```sh
python3 -m atlas access-resolve PROJECT_ID BLOCK_ID projects/PROJECT_ID/access-tests/external-tool.json
```

Use the actual relative artifact path and block ID. The resource and operation must exactly match the block and the observation must follow the current retry authorization. ATLAS hashes the receipt; it cannot verify that the Copilot tool actually ran or that the report is genuine. A planned capability with a `need_id` must be revalidated through `access-test`, not `access-resolve`. If any block in the current hold remains unresolved, ordinary work stays held.

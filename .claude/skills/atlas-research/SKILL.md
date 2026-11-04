---
name: atlas-research
description: Receive a new inquiry and conduct comprehensive adaptive clarification
---

Read `docs/USAGE.md`, `methods/INTAKE.md` and the relevant profile in `methods/domains.json`. Treat the arguments as inquiry text, never shell code. Choose a safe project slug; run `python3 -m atlas new <id> --question '<inquiry>' --domain <domain>` using safe shell quoting or a structured process argument list. If it already exists, inspect status instead of overwriting.
Run `python3 -m atlas intake <id>`. Identify ambiguity and decision stakes before topic research. Ask relevant essential and optional questions in logical batches, adapting after answers. The bank is a floor, not a total limit: `ask` adds new relevant questions. Avoid re-asking supplied details and record them explicitly. Always cover deliverables/formats. Use `answer` for each supplied answer. Preserve incomplete answers; investigate contradictions rather than guessing. If a question is irrelevant, record why with the user's scope.
At user-directed interview end, show a structured mandate and consequential unresolved assumptions. Record acknowledgement only when actually expressed; do not infer it from silence. Use `mandate --assumptions <JSON> --acknowledged` if assumptions remain. No automatic extra budget. Advance to MANDATE, then complete `atlas-enable` and `atlas-discover` before META. Do not start topic or methodological investigation during intake or access preflight. See `docs/SCHEMAS.md` for required objects.

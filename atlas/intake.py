"""Adaptive question ledger. Conversational relevance remains the active Copilot agent's responsibility."""
from .io import AtlasError, read_json

CORE = [
    ("objective", "What exact outcome do you want, and why now?", True),
    ("decision", "What decision or understanding must this research enable?", True),
    ("success", "What would make the research useful and its conclusion actionable?", True),
    ("scope", "What is included, excluded, and already known?", True),
    ("geography", "Which countries, markets, or populations apply?", True),
    ("horizon", "Which evidence dates and decision time horizon matter?", True),
    ("constraints", "Which financial, organizational, ethical, or practical constraints apply?", True),
    ("alternatives", "Which options, including doing nothing, should be compared?", False),
    ("risk", "What downside can you tolerate and which risks are unacceptable?", False),
    ("budget", "What tool/data spending is authorized? Default is zero additional paid access.", True),
    ("permissions", "What data and integrations may be used, and what must stay private?", True),
    ("deliverables", "Which outputs and formats do you want: report, dataset, source library, model, ranking, slides, code, validation plan or others?", True),
    ("evidence", "What evidence standards and quantitative rigor are appropriate?", True),
    ("existing_data", "What prior attempts, files, evidence or assumptions should be examined?", False),
    ("audience", "Who will use the outputs; what language, detail and citation style suit them?", False),
    ("deadline", "Is there a deadline or priority order for staged results?", False),
]


def profiles(root):
    return read_json(root / "methods/domains.json")


def questions(root, domain, answers=None, extra=None):
    p = profiles(root)
    if domain not in p:
        raise AtlasError("Unknown domain: " + domain)
    out = [{"key": k, "prompt": q, "essential": e, "batch": "core"} for k, q, e in CORE]
    for key, essential in [("essential_questions", True), ("optional_questions", False)]:
        out += [dict(x, essential=essential, batch=domain) for x in p[domain][key]]
    out += extra or []
    seen = set()
    for row in out:
        if row["key"] in seen: raise AtlasError("Duplicate intake question")
        seen.add(row["key"])
    answers = answers or {}
    return [dict(row, answered=row["key"] in answers) for row in out]


def missing(root, domain, answers, extra=None):
    return [q["key"] for q in questions(root, domain, answers, extra)
            if q["essential"] and not q["answered"]]

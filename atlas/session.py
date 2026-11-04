"""Explicit execution-environment guidance; no automatic duration cutoff.

A client/runner identifier is supplied by the operator, not inferred from
repository location. Publication claims are guidance, not capability probes.
"""
from .io import AtlasError

PROFILES = {
    "copilot_sandbox": {
        "documented_duration": "no one-hour total session limit in newer cloud sandboxes (GitHub 2026-10-28)",
        "continuation": "reconnect/resume cloud sandbox or saved snapshot where supported",
        "reference": "https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/",
    },
    "copilot_actions": {
        "documented_duration": "older GitHub Actions-based cloud-agent task documentation states a 59-minute limit",
        "continuation": "save ATLAS checkpoint; start an authorized follow-on task if the runner stops",
        "reference": "https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent",
    },
    "copilot_cli": {"documented_duration": "client-specific; not inferred", "continuation": "continue supported CLI session or use ATLAS handoff", "reference": "https://docs.github.com/en/copilot"},
    "copilot_ide": {"documented_duration": "client-specific; not inferred", "continuation": "reopen supported IDE session or use ATLAS handoff", "reference": "https://code.visualstudio.com/docs/agents/concepts/sessions"},
    "claude_code": {"documented_duration": "plan/runtime-specific; not inferred", "continuation": "use supported client resume or ATLAS handoff", "reference": "https://code.claude.com/docs/en/overview"},
    "codex": {"documented_duration": "plan/runtime-specific; not inferred", "continuation": "use supported client resume or ATLAS handoff", "reference": "https://developers.openai.com/codex/"},
    "unknown": {"documented_duration": "unknown", "continuation": "persist research artifacts and verify actual client support", "reference": ""},
}


def session_profile(kind):
    if kind not in PROFILES:
        raise AtlasError("Unknown client surface; choose one of: " + ", ".join(sorted(PROFILES)))
    return {"client_surface": kind, **PROFILES[kind],
            "hard_coded_cutoff_seconds": None,
            "policy": "Do not impose a universal session cap. Persist state, preserve verified results and reconcile remote jobs before retrying.",
            "basis": "documentation only; active runtime, entitlements and service behavior must be observed"}

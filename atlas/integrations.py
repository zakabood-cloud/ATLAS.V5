"""Offline capability discovery; presence is never authentication or a live test."""
import shutil
import sys
from pathlib import Path
from datetime import timedelta
from .io import now, date, read_json, AtlasError


def discover_capabilities(project_root=None):
    root = Path(project_root or ".")
    result = {"observed_at": now(), "python": sys.version.split()[0], "network_tests": 0,
              "credential_values_reported": False, "credential_values_used_for_requests": False, "capabilities": []}
    for name in ["git", "node"]:
        found = shutil.which(name) is not None
        result["capabilities"].append({"name": name, "discovered": found,
            "configured": "unknown", "authenticated": "unverified", "tested": False,
            "availability": "local_executable_found" if found else "unavailable"})
    p = root / ".mcp.json"
    if p.exists():
        # Parsing configuration may encounter secret values; never return or use them.
        data = read_json(p)
        if not isinstance(data,dict): raise AtlasError("MCP configuration must be an object")
        servers = data.get("mcpServers", {})
        if not isinstance(servers, dict): raise AtlasError("Invalid MCP server map")
        for name in servers:
            result["capabilities"].append({"name": name, "discovered": True,
                "configured": True, "authenticated": "unverified", "tested": False,
                "availability": "configuration_only"})
    return result


def validate_observation(row, as_of=None):
    if not isinstance(row, dict): raise AtlasError("Capability observation must be an object")
    for k in ["name", "status", "observed_at", "expires_at", "method", "limitations"]:
        if not isinstance(row.get(k), str) or not row[k].strip(): raise AtlasError("Missing observation " + k)
    if row["status"] not in {"unavailable", "discovered", "configured", "authenticated", "tested", "failed"}:
        raise AtlasError("Unknown capability status")
    current = date(as_of or now())
    if date(row["observed_at"]) > current or date(row["expires_at"]) <= date(row["observed_at"]):
        raise AtlasError("Invalid capability validity window")
    if row["status"] in {"authenticated", "tested"} and not row.get("evidence_artifact"):
        raise AtlasError("Authentication/test requires an evidence artifact, not a configuration claim")
    return dict(row, expired=current >= date(row["expires_at"]),
                provenance="operator supplied; not independently authenticated by this validator")

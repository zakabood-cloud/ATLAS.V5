"""Repository structure checks using an intentionally restricted YAML frontmatter subset."""
import ast
import re
from pathlib import Path
from .io import read_json, parse_json, AtlasError

REQUIRED=["AGENTS.md",".github/copilot-instructions.md","README.md","pyproject.toml","methods/domains.json","docs/USAGE.md","docs/SCHEMAS.md","docs/SECURITY.md",
          "atlas/__main__.py","atlas/project.py","atlas/evidence.py","atlas/quant.py","atlas/memory.py",
          ".github/skills/atlas-init/SKILL.md",".github/skills/atlas-research/SKILL.md",
          ".github/skills/atlas-meta/SKILL.md",".github/skills/atlas-run/SKILL.md",
          ".github/skills/atlas-audit/SKILL.md",".github/skills/atlas-deliver/SKILL.md",
          ".github/skills/atlas-discover/SKILL.md",".github/skills/atlas-evaluate/SKILL.md",
          "atlas/__init__.py","atlas/io.py","atlas/intake.py","atlas/integrations.py",
          "atlas/structure.py","atlas/demo.py","scripts/demo.py","docs/INTEGRATIONS.md"]
REQUIRED += ["atlas/access.py","atlas/contracts.py","atlas/enablement.py","atlas/dispatch.py","atlas/archive.py","docs/ACCESS.md","docs/MIGRATION.md",
             ".github/agents/research-coordinator.agent.md",".github/skills/atlas-enable/SKILL.md"]
REQUIRED += [".github/agents/"+name+".agent.md" for name in
             ["methodology-architect","domain-researcher","evidence-reviewer","adversarial-reviewer",
              "quantitative-analyst","source-intelligence-researcher","tool-integration-architect"]]


def frontmatter(path):
    text=Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]: raise AtlasError("Missing YAML frontmatter")
    header,body=text[4:].split("\n---\n",1); data={}
    for line in header.splitlines():
        match=re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*): (.+)",line)
        if not match: raise AtlasError("Use single-line scalars or JSON string arrays in shipped frontmatter")
        key,value=match.groups()
        if key in data or value.startswith(("{","|",">","&","*","!")): raise AtlasError("Duplicate key or unsupported YAML structure")
        if value.startswith(("[",'"')):
            value=parse_json(value)
            if not isinstance(value,(list,str)) or isinstance(value,list) and any(not isinstance(v,str) or not v.strip() for v in value):
                raise AtlasError("Only strings and string arrays are supported")
        elif value in {"true","false"}: value=value=="true"
        elif ": " in value or " #" in value: raise AtlasError("Ambiguous unquoted YAML value")
        data[key]=value
    if not body.strip(): raise AtlasError("Empty instructions")
    if not isinstance(data.get("name"),str) or not re.fullmatch(r"[a-z0-9-]+",data["name"]) or not isinstance(data.get("description"),str) or not data["description"]:
        raise AtlasError("Missing valid name/description")
    if "tools" in data and (not isinstance(data["tools"],list) or len(set(data["tools"]))!=len(data["tools"])):
        raise AtlasError("Tools must be a unique JSON string array")
    return data


def check(root):
    root=Path(root); errors=[]; count=0
    # Portable core supports both Copilot and Claude Code. Each native adapter
    # is verified separately; neither overrides the other's runtime permissions.
    if not (root/"CLAUDE.md").is_file():
        errors.append("Missing Claude Code adapter CLAUDE.md")
    for name in ("atlas-init", "atlas-research", "atlas-meta", "atlas-run", "atlas-audit", "atlas-deliver"):
        if not (root/".claude/skills"/name/"SKILL.md").is_file():
            errors.append("Missing Claude Code skill: "+name)
    for name in REQUIRED:
        if not (root/name).is_file() or (root/name).stat().st_size==0: errors.append("Missing/empty "+name)
    if (root/"pyproject.toml").is_file() and (root/"atlas/__init__.py").is_file():
        metadata=(root/"pyproject.toml").read_text(encoding="utf-8")
        module=(root/"atlas/__init__.py").read_text(encoding="utf-8")
        declared=re.findall(r'^version\s*=\s*"([^"]+)"\s*$',metadata,re.M)
        implemented=re.findall(r'^__version__\s*=\s*"([^"]+)"\s*$',module,re.M)
        if len(declared)!=1 or declared!=implemented: errors.append("Package and engine release versions differ or are ambiguous")
    for p in list((root/"atlas").glob("*.py"))+list((root/"scripts").glob("*.py"))+list((root/"tests").glob("*.py")):
        try: ast.parse(p.read_text(encoding="utf-8")); count+=1
        except SyntaxError as e: errors.append(str(p.relative_to(root))+": "+str(e))
    for p in list((root/".github/agents").glob("*.agent.md"))+list((root/".github/skills").glob("*/SKILL.md")):
        try:
            d=frontmatter(p); count+=1
            if ".github/skills/" in p.as_posix():
                if d["name"]!=p.parent.name: raise AtlasError("Skill directory/name mismatch")
                if "allowed-tools" in d: raise AtlasError("Shipped skills must not grant permissions")
            else:
                agent_name=p.name.removesuffix(".agent.md")
                if d["name"]!=agent_name: raise AtlasError("Agent filename/name mismatch")
                if d.get("permissionMode")=="bypassPermissions": raise AtlasError("Permission bypass forbidden")
                if "memory" in d: raise AtlasError("Use controlled method memory, not automatic reviewer write access")
                if "model" in d: raise AtlasError("Shipped agents inherit native client/Auto selection; do not pin a model")
        except AtlasError as e: errors.append(str(p.relative_to(root))+": "+str(e))
    for p in list((root/".claude/agents").glob("*.md"))+list((root/".claude/skills").glob("*/SKILL.md")):
        try:
            raw=p.read_text(encoding="utf-8")
            if not raw.startswith("---\n") or "\n---\n" not in raw[4:]:
                raise AtlasError("Missing Claude adapter frontmatter")
            fm,body=raw[4:].split("\n---\n",1)
            if not body.strip() or not re.search(r"(?m)^name: [a-z0-9-]+$",fm) or not re.search(r"(?m)^description: .+",fm):
                raise AtlasError("Missing agent/skill name, description or body")
            if "bypassPermissions" in fm:
                raise AtlasError("Claude adapter cannot bypass permissions")
            count+=1
        except (AtlasError,OSError) as e:
            errors.append(str(p.relative_to(root))+": "+str(e))
    for folder in ["config","methods","examples"]:
        for p in (root/folder).rglob("*.json"):
            try: read_json(p); count+=1
            except (AtlasError,OSError) as e: errors.append(str(p.relative_to(root))+": "+str(e))
    for p in root.rglob("*.md"):
        # Restrict link checking to official release payload locations, not
        # scratch/checkpoint trees left by interrupted tests.
        if p.relative_to(root).parts[0] not in {"AGENTS.md","CLAUDE.md","README.md", ".github", ".claude", "docs", "methods", "reports", "research", "benchmarks", "memory", "scripts"}: continue
        if set(p.relative_to(root).parts)&{"projects","reference",".git",".atlas","__pycache__"}: continue
        if not p.exists(): continue
        text=p.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)",text):
            if "://" in target or target.startswith("#"): continue
            target=target.split("#")[0]
            if target and not (p.parent/target).exists(): errors.append("Broken link "+str(p.relative_to(root))+" -> "+target)
    p=root/"AGENTS.md"
    if p.exists() and len(p.read_text(encoding="utf-8").splitlines())>=200: errors.append("AGENTS.md context budget exceeded")
    return {"ok":not errors,"checked_units":count,"errors":errors,
            "scope":"Static subset validation, Python AST and local references; not Copilot runtime or semantic instruction validation."}

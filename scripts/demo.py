#!/usr/bin/env python3
"""Run a local synthetic demonstration in a temporary workspace."""
import json
from pathlib import Path
import sys
import tempfile
import shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas.demo import complete

with tempfile.TemporaryDirectory(prefix="atlas-demo-") as temp:
    root=Path(temp); shutil.copytree(Path(__file__).resolve().parents[1]/"methods",root/"methods")
    p=complete(root)
    print(json.dumps({"synthetic":True,"state":p.status()["state"],"validation":p.validate()},indent=2))

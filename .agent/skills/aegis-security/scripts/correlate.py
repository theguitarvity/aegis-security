#!/usr/bin/env python3
import json
import sys
from pathlib import Path

findings = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")) if len(sys.argv) > 1 else []
print(json.dumps({"findings": findings, "attack_chains": []}, indent=2))

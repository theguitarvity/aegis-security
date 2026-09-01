#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path

target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve() / ".aegis-security"
shutil.rmtree(target, ignore_errors=True)
print(f"removed {target}")

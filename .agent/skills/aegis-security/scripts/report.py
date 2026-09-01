#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from aegis import assess, discover, normalize, render_report, write_json

project = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
out = project / ".aegis-security"
findings = normalize(out / "raw")
assessment = assess(findings, [])
write_json(out / "normalized-findings.json", findings)
write_json(out / "assessment.json", assessment)
render_report(project, out, discover(project), findings, assessment)
print(out / "security-assessment.md")

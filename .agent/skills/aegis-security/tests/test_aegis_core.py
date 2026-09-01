import json
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from aegis import assess, discover, normalize, validate_target


class AegisCoreTests(unittest.TestCase):
    def test_discover_recognizes_platform_from_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"next": "1.0.0", "@apollo/server": "1.0.0"}}),
                encoding="utf-8",
            )
            (root / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
            (root / "Dockerfile").write_text("FROM node:20\n", encoding="utf-8")

            app = discover(root)["application"]

            self.assertIn("JavaScript/TypeScript", app["languages"])
            self.assertIn("next.js", app["frameworks"])
            self.assertIn("apollo/graphql", app["frameworks"])
            self.assertIn("openapi.yaml", app["openapi_files"])
            self.assertTrue(app["containers"])

    def test_aggressive_public_target_requires_authorization(self):
        denied = validate_target("https://example.com", "full", False)
        allowed = validate_target("http://localhost:3000", "full", False)

        self.assertFalse(denied["allowed"])
        self.assertTrue(allowed["allowed"])

    def test_normalize_deduplicates_semgrep_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            payload = {
                "results": [
                    {
                        "check_id": "python.sql-injection",
                        "path": "app.py",
                        "start": {"line": 10},
                        "extra": {"severity": "HIGH", "message": "SQL injection", "lines": "query = user"},
                    },
                    {
                        "check_id": "python.sql-injection",
                        "path": "app.py",
                        "start": {"line": 10},
                        "extra": {"severity": "HIGH", "message": "SQL injection", "lines": "query = user"},
                    },
                ]
            }
            (raw / "semgrep.json").write_text(json.dumps(payload), encoding="utf-8")

            findings = normalize(raw)
            assessment = assess(findings, [])

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["id"], "SEC-001")
            self.assertEqual(assessment["severity_counts"]["high"], 1)


if __name__ == "__main__":
    unittest.main()

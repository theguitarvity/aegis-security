#!/usr/bin/env python3
"""Aegis Security deterministic core."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse


SEVERITIES = ("critical", "high", "medium", "low", "info")
QUICK_TOOLS = ("semgrep", "gitleaks", "trivy", "syft", "grype")
PROFILE_TOOLS = {
    "quick": QUICK_TOOLS,
    "standard": QUICK_TOOLS + ("zap", "schemathesis"),
    "adversarial-local": QUICK_TOOLS + ("zap", "schemathesis", "mitmproxy"),
    "resilience": QUICK_TOOLS + ("zap", "schemathesis", "k6", "toxiproxy"),
    "full": QUICK_TOOLS + ("zap", "schemathesis", "mitmproxy", "k6", "toxiproxy"),
}
TOOL_COMMANDS = {
    "semgrep": "semgrep",
    "gitleaks": "gitleaks",
    "trivy": "trivy",
    "syft": "syft",
    "grype": "grype",
    "zap": "zap-baseline.py",
    "schemathesis": "schemathesis",
    "mitmproxy": "mitmproxy",
    "k6": "k6",
    "toxiproxy": "toxiproxy-cli",
}
AGGRESSIVE_PROFILES = {"adversarial-local", "resilience", "full"}
PRIVATE_HOST_PATTERNS = (
    re.compile(r"^localhost$", re.I),
    re.compile(r"^127\."),
    re.compile(r"^10\."),
    re.compile(r"^192\.168\."),
    re.compile(r"^172\.(1[6-9]|2\d|3[01])\."),
    re.compile(r"^::1$"),
    re.compile(r"^host\.docker\.internal$", re.I),
)
REDACT_PATTERNS = [
    re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
]


@dataclass
class Finding:
    id: str
    fingerprint: str
    title: str
    description: str
    severity: str
    confidence: str
    source: dict
    classification: dict
    component: dict
    evidence: list
    risk: dict
    remediation: dict
    status: str = "open"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def redact(value: str) -> str:
    text = value or ""
    for pattern in REDACT_PATTERNS:
        text = pattern.sub(lambda m: m.group(0).split("=", 1)[0] + "=<redacted>" if "=" in m.group(0) else "<redacted>", text)
    return text


def discover(project: Path) -> dict:
    files = [p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file() and ".git/" not in p.as_posix()]
    names = set(files)
    app = {
        "languages": [],
        "frameworks": [],
        "package_managers": [],
        "interfaces": [],
        "databases": [],
        "caches": [],
        "messaging": [],
        "authentication": [],
        "authorization": [],
        "external_integrations": [],
        "exposed_ports": [],
        "containers": any(Path(f).name == "Dockerfile" for f in files),
        "compose": any(Path(f).name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"} for f in files),
        "openapi_files": [f for f in files if re.search(r"(openapi|swagger).*\.(ya?ml|json)$", f, re.I)],
        "dockerfiles": [f for f in files if Path(f).name == "Dockerfile" or Path(f).name.startswith("Dockerfile.")],
        "ci_cd": [f for f in files if f.startswith(".github/workflows/") or Path(f).name in {"azure-pipelines.yml", ".gitlab-ci.yml"}],
        "infrastructure_as_code": [f for f in files if f.endswith((".tf", ".tf.json")) or "k8s" in f or "helm" in f],
    }
    markers = {
        "package.json": ("JavaScript/TypeScript", "npm"),
        "pnpm-lock.yaml": ("JavaScript/TypeScript", "pnpm"),
        "yarn.lock": ("JavaScript/TypeScript", "yarn"),
        "pyproject.toml": ("Python", "pip/uv/poetry"),
        "requirements.txt": ("Python", "pip"),
        "go.mod": ("Go", "go"),
        "Cargo.toml": ("Rust", "cargo"),
        "pom.xml": ("Java", "maven"),
        "build.gradle": ("Java/Kotlin", "gradle"),
    }
    for marker, (language, manager) in markers.items():
        if marker in names:
            app["languages"].append(language)
            app["package_managers"].append(manager)
    if "package.json" in names:
        try:
            pkg = read_json(project / "package.json")
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            for framework in ("react", "next", "vue", "express", "nestjs", "fastify"):
                if framework in deps or f"@{framework}/core" in deps:
                    app["frameworks"].append(framework)
        except Exception:
            pass
    for f in files:
        name = Path(f).name.lower()
        if name in {"application.yml", "application.yaml", "application.properties", ".env.example"}:
            app["interfaces"].append(f)
    return {"application": {k: sorted(set(v)) if isinstance(v, list) else v for k, v in app.items()}}


def validate_target(target: str | None, profile: str, authorized: bool) -> dict:
    if not target:
        return {"allowed": profile not in AGGRESSIVE_PROFILES, "reason": "no target supplied"}
    host = urlparse(target).hostname or target
    local = any(pattern.search(host) for pattern in PRIVATE_HOST_PATTERNS)
    if local:
        return {"allowed": True, "reason": "local/private target", "host": host}
    if profile in AGGRESSIVE_PROFILES and not authorized:
        return {"allowed": False, "reason": "public or non-local target requires explicit authorization", "host": host}
    return {"allowed": authorized, "reason": "explicit authorization required for public target", "host": host}


def command_available(tool: str) -> bool:
    return shutil.which(TOOL_COMMANDS[tool]) is not None


def doctor() -> dict:
    return {tool: {"command": TOOL_COMMANDS[tool], "available": command_available(tool)} for tool in TOOL_COMMANDS}


def run_tool(tool: str, project: Path, output: Path, target: str | None) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    commands = {
        "semgrep": ["semgrep", "scan", "--json", "--quiet", str(project)],
        "gitleaks": ["gitleaks", "detect", "--source", str(project), "--report-format", "json", "--no-banner"],
        "trivy": ["trivy", "fs", "--format", "json", "--scanners", "vuln,secret,misconfig", str(project)],
        "syft": ["syft", str(project), "-o", "json"],
        "grype": ["grype", str(project), "-o", "json"],
    }
    if tool == "zap":
        if not target:
            return {"tool": tool, "status": "skipped", "reason": "target required"}
        commands[tool] = ["zap-baseline.py", "-t", target, "-J", str(output)]
    elif tool == "schemathesis":
        openapi = next((p for p in project.rglob("*") if re.search(r"(openapi|swagger).*\.(ya?ml|json)$", p.name, re.I)), None)
        if not openapi:
            return {"tool": tool, "status": "skipped", "reason": "OpenAPI file not found"}
        commands[tool] = ["schemathesis", "run", str(openapi), "--report", str(output)]
    elif tool in {"mitmproxy", "k6", "toxiproxy"}:
        return {"tool": tool, "status": "manual", "reason": "requires scenario-specific operator setup"}
    cmd = commands.get(tool)
    if not cmd or not command_available(tool):
        return {"tool": tool, "status": "skipped", "reason": f"{TOOL_COMMANDS[tool]} not installed"}
    try:
        proc = subprocess.run(cmd, cwd=project, text=True, capture_output=True, timeout=900, check=False)
        payload = proc.stdout or proc.stderr or "{}"
        output.write_text(redact(payload), encoding="utf-8")
        return {"tool": tool, "status": "completed", "exit_code": proc.returncode, "output": output.as_posix()}
    except subprocess.TimeoutExpired:
        return {"tool": tool, "status": "failed", "reason": "timeout"}


def fingerprint(parts: list[str]) -> str:
    normalized = "|".join((p or "").strip().lower() for p in parts)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def normalize(raw_dir: Path) -> list[dict]:
    findings: list[Finding] = []
    for path in sorted(raw_dir.glob("*.json")):
        tool = path.stem
        try:
            data = read_json(path)
        except Exception:
            continue
        if tool == "semgrep":
            for item in data.get("results", []):
                extra = item.get("extra", {})
                sev = extra.get("severity", "medium").lower()
                loc = item.get("start", {})
                title = extra.get("message") or item.get("check_id", "Semgrep finding")
                fp = fingerprint([tool, item.get("check_id", ""), item.get("path", ""), str(loc.get("line", "")), title])
                findings.append(Finding("", fp, title, title, sev if sev in SEVERITIES else "medium", "medium", {"tool": tool, "rule_id": item.get("check_id", ""), "raw_reference": path.as_posix()}, {"cwe": [], "owasp": [], "owasp_api": [], "cvss": None}, {"service": "", "file": item.get("path", ""), "line": loc.get("line"), "endpoint": "", "dependency": ""}, [redact(extra.get("lines", ""))], {"exploitability": "", "impact": "", "likelihood": ""}, {"summary": "Review and remediate the vulnerable code path.", "architectural_action_required": False, "recommended_actions": []}))
        elif tool in {"gitleaks", "trivy", "grype"}:
            items = data if isinstance(data, list) else data.get("Results", data.get("matches", []))
            for item in items if isinstance(items, list) else []:
                title = item.get("Description") or item.get("RuleID") or item.get("vulnerability", {}).get("id") or f"{tool} finding"
                sev = (item.get("Severity") or item.get("severity") or "medium").lower()
                file_name = item.get("File") or item.get("Target") or item.get("artifact", {}).get("name", "")
                dep = item.get("PkgName") or item.get("artifact", {}).get("name", "")
                fp = fingerprint([tool, title, file_name, dep])
                findings.append(Finding("", fp, title, title, sev if sev in SEVERITIES else "medium", "medium", {"tool": tool, "rule_id": item.get("RuleID", ""), "raw_reference": path.as_posix()}, {"cwe": [], "owasp": [], "owasp_api": [], "cvss": item.get("CVSS")}, {"service": "", "file": file_name, "line": item.get("StartLine"), "endpoint": "", "dependency": dep}, [redact(json.dumps(item, sort_keys=True)[:1200])], {"exploitability": "", "impact": "", "likelihood": ""}, {"summary": "Validate exploitability and apply the vendor or code-level remediation.", "architectural_action_required": False, "recommended_actions": []}))
    deduped = {}
    for finding in findings:
        deduped.setdefault(finding.fingerprint, finding)
    result = []
    for index, finding in enumerate(deduped.values(), start=1):
        finding.id = f"SEC-{index:03d}"
        result.append(asdict(finding))
    return result


def assess(findings: list[dict], tool_runs: list[dict]) -> dict:
    counts = {sev: 0 for sev in SEVERITIES}
    for f in findings:
        counts[f.get("severity", "medium")] += 1
    score = max(0, 100 - counts["critical"] * 25 - counts["high"] * 12 - counts["medium"] * 5 - counts["low"])
    failed = counts["critical"] >= 1 or counts["high"] > 2
    skipped = [r for r in tool_runs if r["status"] in {"skipped", "failed"}]
    return {"score": score, "gate": "fail" if failed else "warn" if skipped else "pass", "severity_counts": counts, "tool_runs": tool_runs}


def render_report(project: Path, out_dir: Path, discovery: dict, findings: list[dict], assessment: dict) -> None:
    lines = ["# Aegis Security Assessment", "", f"Project: `{project}`", f"Security score: **{assessment['score']}**", f"Release gate: **{assessment['gate'].upper()}**", "", "## Discovery", "", "```json", json.dumps(discovery, indent=2), "```", "", "## Findings", ""]
    if not findings:
        lines.append("No normalized findings were produced by the available tools.")
    for finding in findings:
        comp = finding["component"]
        location = comp.get("file") or comp.get("dependency") or comp.get("endpoint") or "project"
        lines.extend([f"### {finding['id']} - {finding['title']}", "", f"- Severity: `{finding['severity']}`", f"- Confidence: `{finding['confidence']}`", f"- Source: `{finding['source']['tool']}`", f"- Location: `{location}`", f"- Remediation: {finding['remediation']['summary']}", ""])
    (out_dir / "security-assessment.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    roadmap = ["# SpecMaster Remediation Roadmap", "", f"Release gate: {assessment['gate'].upper()}", ""]
    for finding in findings:
        roadmap.extend([f"## {finding['id']} - {finding['title']}", "", f"Severity: {finding['severity']}", "", "Recommended implementation task:", f"- {finding['remediation']['summary']}", ""])
    (out_dir / "specmaster-remediation.md").write_text("\n".join(roadmap) + "\n", encoding="utf-8")


def scan(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    out_dir = project / ".aegis-security"
    raw_dir = out_dir / "raw"
    discovery = discover(project)
    target_check = validate_target(args.target, args.profile, args.authorize_target)
    if not target_check["allowed"]:
        print(json.dumps({"error": "target denied", "target_validation": target_check}, indent=2))
        return 2
    tool_runs = []
    for tool in PROFILE_TOOLS[args.profile]:
        tool_runs.append(run_tool(tool, project, raw_dir / f"{tool}.json", args.target))
    findings = normalize(raw_dir)
    assessment = assess(findings, tool_runs)
    assessment["target_validation"] = target_check
    write_json(out_dir / "discovery.json", discovery)
    write_json(out_dir / "normalized-findings.json", findings)
    write_json(out_dir / "assessment.json", assessment)
    render_report(project, out_dir, discovery, findings, assessment)
    print(json.dumps(assessment, indent=2))
    return 1 if assessment["gate"] == "fail" else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegis")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    d = sub.add_parser("discover")
    d.add_argument("--project", default=".")
    n = sub.add_parser("normalize")
    n.add_argument("--raw-dir", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--project", default=".")
    s.add_argument("--profile", choices=sorted(PROFILE_TOOLS), default="quick")
    s.add_argument("--target")
    s.add_argument("--authorize-target", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "doctor":
        print(json.dumps(doctor(), indent=2))
        return 0
    if args.command == "discover":
        print(json.dumps(discover(Path(args.project).resolve()), indent=2))
        return 0
    if args.command == "normalize":
        print(json.dumps(normalize(Path(args.raw_dir)), indent=2))
        return 0
    if args.command == "scan":
        return scan(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

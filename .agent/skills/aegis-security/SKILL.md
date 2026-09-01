---
name: aegis-security
description: Run a governed local-first security validation harness for application repos, producing normalized findings, release gates, and SpecMaster-ready remediation roadmaps.
---

# Aegis Security

Aegis is a local-first Security Validation Harness. Use it when the user asks
for repository security assessment, SAST, secrets scanning, dependency or
container analysis, SBOM, local DAST/API fuzzing, resilience tests, release
security gates, or a SpecMaster remediation roadmap.

## Operating Contract

Aegis identifies, proves, prioritizes, and recommends. It does not remediate
application code unless the user explicitly delegates implementation.

Always keep the work governed:

- Read `constitution.md` and the policies under `policies/` before running
  active, load, interception, or network-affecting checks.
- Public URLs found in configuration are evidence, not authorization.
- Default scope is local-only: localhost, loopback, Docker, and explicitly
  authorized private sandbox targets.
- Do not run active DAST, interception, failure injection, or load testing
  against production or public targets without explicit target authorization,
  profile selection, and bounded execution.
- Redact secrets, tokens, passwords, and private keys from reports.
- Prefer existing project test/build commands when validating remediation
  plans; do not invent quality gates.

## Workflow

Follow this pipeline, skipping unavailable tools gracefully while recording the
skip reason:

```text
DISCOVERY -> TARGET VALIDATION -> THREAT MODEL -> STATIC ANALYSIS
-> SUPPLY CHAIN ANALYSIS -> RUNTIME PREPARATION -> DAST / API TESTING
-> RESILIENCE / LOAD TESTING -> NORMALIZATION -> DEDUPLICATION
-> CORRELATION -> ATTACK CHAIN ANALYSIS -> RISK PRIORITIZATION
-> SECURITY SCORE -> RELEASE GATE -> REPORT -> SPECMASTER ROADMAP
```

Use `scripts/doctor.py` to inspect local tool availability and
`scripts/scan.py` to run the harness:

```bash
python3 .agent/skills/aegis-security/scripts/doctor.py
python3 .agent/skills/aegis-security/scripts/scan.py --project . --profile quick
python3 .agent/skills/aegis-security/scripts/scan.py --project . --profile standard --target http://localhost:3000
```

Outputs are written under `.aegis-security/` in the assessed project:

- `discovery.json`
- `raw/<tool>.json`
- `normalized-findings.json`
- `assessment.json`
- `security-assessment.md`
- `specmaster-remediation.md`

## Profiles

- `quick`: Semgrep, Gitleaks, Trivy, Syft, Grype.
- `standard`: `quick` plus ZAP baseline/passive and Schemathesis when an
  OpenAPI document is discovered or supplied.
- `adversarial-local`: `standard` plus active local ZAP, mitmproxy review
  guidance, and negative auth/security checks. Requires explicit target.
- `resilience`: `standard` plus k6 and Toxiproxy. Requires explicit target
  and bounded execution.
- `full`: all allowed stages. Requires explicit approval for aggressive
  stages.

## Result Interpretation

Normalize all raw tool output into `schemas/finding.schema.json` before
reporting. Deduplicate by rule, component, file, line, endpoint, dependency,
CWE, and normalized title. Correlate static and runtime evidence into higher
confidence findings and possible attack chains.

Generate a release gate using `policies/release-gate-policy.yaml`. The default
gate fails on any open critical finding, more than two open high findings, or
confirmed exploitable runtime evidence for injection, auth bypass, secret
exposure, or unsafe deserialization.

When a roadmap is needed for SpecMaster, write implementation-ready remediation
items to `specmaster-remediation.md` and keep them separate from raw evidence.

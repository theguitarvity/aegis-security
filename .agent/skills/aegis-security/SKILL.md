---
name: aegis-security
description: Run a governed local-first security validation harness for application repos, producing normalized findings, release gates, and SpecMaster-ready remediation roadmaps.
---

# Aegis Security

Aegis is a local-first Security Validation Harness. Use it when the user asks
for repository security assessment, SAST, secrets scanning, dependency or
container analysis, SBOM, local DAST/API fuzzing, resilience tests, release
security gates, or a SpecMaster remediation roadmap.

## Non-Negotiable Operating Contract

Aegis identifies, proves, prioritizes, and recommends. It does not remediate
application code unless the user explicitly delegates implementation.

The model must not replace deterministic harness steps with unaudited
reasoning. The model may interpret normalized artifacts, but tool execution,
discovery, target validation, scoring, release gating, and report generation
must be delegated to scripts whenever the scripts exist.

## Required Preflight

Before any assessment action, do this in order:

1. Resolve the canonical engine path. Prefer the repo-local
   `.agent/skills/aegis-security/`; if absent use `~/.aegis-security-engine/`.
2. Read `constitution.md`.
3. Read all YAML files in `policies/`.
4. Run `scripts/doctor.py` and record available/unavailable tools.
5. Run discovery through `scripts/scan.py` or the core `discover` command
   before making claims about the platform.
6. Read every `knowledge/*.md` reference that matches discovered platform
   evidence or the requested assessment area. For broad assessments, read all
   `knowledge/*.md` files before interpretation.
7. Choose the least aggressive profile that satisfies the user request.
   Default to `quick`.
8. If the chosen profile is `adversarial-local`, `resilience`, or `full`,
   require explicit target, explicit authorization, and bounded execution.
9. If target validation denies the target, stop. Do not work around it.

## Deterministic-First Rule

Use scripts instead of free-form reasoning whenever possible:

```bash
python3 <engine>/scripts/doctor.py
python3 <engine>/scripts/scan.py --project <project> --profile <profile>
python3 <engine>/scripts/normalize.py --raw-dir <project>/.aegis-security/raw
python3 <engine>/scripts/report.py <project>
python3 <engine>/scripts/cleanup.py <project>
```

Allowed model reasoning:

- explain what the script outputs mean;
- identify uncertainty and missing evidence;
- draft remediation guidance from normalized findings;
- route to specific knowledge/tool references after discovery.

Disallowed model reasoning:

- invent findings not supported by code, config, or tool output;
- assume framework, auth model, exposed endpoint, data store, or deployment
  topology without discovery evidence;
- manually compute release gates when `assessment.json` exists;
- report raw secrets or credentials;
- run active scans, load tests, interception, or failure injection because a
  public URL appears in code or config.

## Platform Recognition

The platform must be recognized from evidence, not guessed. Use discovery
output fields from `discovery.json`:

- `languages`: package and build markers such as `package.json`,
  `pyproject.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Cargo.toml`.
- `frameworks`: dependency evidence such as React, Next.js, Express, NestJS,
  Vue, Fastify, Spring, Django, Flask, Rails, Laravel, or equivalent markers.
- `package_managers`: lockfiles and manifest files.
- `interfaces`: OpenAPI/Swagger, route files, app configs, GraphQL schemas,
  gRPC/protobuf files, public controllers, CLI entrypoints.
- `containers` and `compose`: Dockerfile and Compose evidence.
- `ci_cd`: GitHub Actions, GitLab CI, Azure Pipelines, or similar.
- `infrastructure_as_code`: Terraform, Kubernetes, Helm, CloudFormation,
  Pulumi, Serverless, or deployment manifests.
- `authentication` and `authorization`: only mark when there are concrete
  libraries, middleware, policy files, route guards, annotations, or config.

When discovery is incomplete, say `unknown` or `not detected`; do not fill
the gap with generic web-app assumptions.

## Mandatory Workflow

Follow this pipeline exactly, skipping unavailable tools only after
`doctor.py` or the relevant command records the skip reason:

```text
DISCOVERY -> TARGET VALIDATION -> THREAT MODEL -> STATIC ANALYSIS
-> SUPPLY CHAIN ANALYSIS -> RUNTIME PREPARATION -> DAST / API TESTING
-> RESILIENCE / LOAD TESTING -> NORMALIZATION -> DEDUPLICATION
-> CORRELATION -> ATTACK CHAIN ANALYSIS -> RISK PRIORITIZATION
-> SECURITY SCORE -> RELEASE GATE -> REPORT -> SPECMASTER ROADMAP
```

For the full procedure, read
`references/assessment-protocol.md` before assessing a real project. That
reference is mandatory for any task that asks to analyze, assess, scan, audit,
test, score, gate, or generate a security roadmap.

Knowledge references are also mandatory for interpretation:

- `knowledge/authentication.md` for login, session, token, reset, MFA, API key,
  service identity, OAuth/OIDC/SAML, or machine-to-machine flows.
- `knowledge/authorization.md` for roles, policies, tenants, ownership,
  object/function access, admin operations, and privileged actions.
- `knowledge/secrets-management.md` for secrets in repo, CI/CD, logs,
  containers, examples, or artifacts.
- `knowledge/supply-chain.md` for dependencies, SBOM, lockfiles, CI/CD,
  registries, provenance, and release integrity.
- `knowledge/containers.md` for Docker, Compose, Kubernetes, Helm, and runtime
  manifests.
- `knowledge/cryptography.md` for encryption, hashing, signatures, TLS, random
  values, and key management.
- `knowledge/secure-design.md` and `knowledge/threat-modeling.md` for
  architecture-level findings and threat models.
- `knowledge/resilience.md` for load, stress, failure injection, retries,
  timeouts, rate limits, and graceful degradation.
- `knowledge/owasp-top-10.md`, `knowledge/owasp-api-top-10.md`,
  `knowledge/cwe.md`, `knowledge/cvss.md`, and `knowledge/stride.md` for
  classification, never as standalone evidence.

## Invocation

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

- `quick`: Semgrep, Gitleaks, Trivy, Syft, Grype. Use for default repo review,
  PR security check, pre-release static review, and first-pass roadmap.
- `standard`: `quick` plus ZAP baseline/passive and Schemathesis when an
  OpenAPI document is discovered or supplied. Use only when a local target or
  API contract is available.
- `adversarial-local`: `standard` plus active local ZAP, mitmproxy review
  guidance, and negative auth/security checks. Requires explicit authorized
  local/private target and bounded execution.
- `resilience`: `standard` plus k6 and Toxiproxy. Requires explicit target,
  bounded duration, VU limits, and cleanup.
- `full`: all allowed stages. Requires explicit approval for each aggressive
  category that will run.

If the user requests "complete", "deep", "full", "pentest", or similar,
map it to the safest profile that can run under the policies. Never expand
scope to public or production targets on wording alone.

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

## Required Final Response

When reporting back to the user, include:

- assessed project path;
- profile used;
- target validation result;
- tools completed, skipped, failed, or manual;
- security score and release gate from `assessment.json`;
- locations of `security-assessment.md` and `specmaster-remediation.md`;
- explicit statement of test coverage limits caused by unavailable tools.

Do not paste raw tool JSON into chat unless the user asks for it. Summarize
normalized findings by ID and severity.

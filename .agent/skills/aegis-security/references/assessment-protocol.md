# Aegis Assessment Protocol

This protocol is mandatory for real assessments. It exists to reduce model
guesswork and force repeatable, script-driven behavior.

## 1. Scope Resolution

Resolve three paths before running anything:

- `project`: repository or application path to assess. Default is current
  working directory.
- `engine`: `.agent/skills/aegis-security` inside the current repo, or
  `~/.aegis-security-engine` after global install.
- `output`: `<project>/.aegis-security`.

Do not assess parent directories, sibling repos, or external services unless
the user names them explicitly.

## 2. Inputs

Accept these user inputs:

- profile: `quick`, `standard`, `adversarial-local`, `resilience`, or `full`.
- target URL: required for DAST, API fuzzing against a live service,
  interception, resilience, and load testing.
- explicit authorization: required for public or non-local targets and all
  aggressive profiles.
- bounds: duration, virtual users, endpoints, auth fixtures, test account, or
  Docker network.

If a required aggressive input is missing, ask one concise question listing all
missing inputs together. Do not ask one question per missing field.

## 3. Required Commands

Run preflight:

```bash
python3 <engine>/scripts/doctor.py
```

Run the harness:

```bash
python3 <engine>/scripts/scan.py --project <project> --profile <profile>
```

For a local target:

```bash
python3 <engine>/scripts/scan.py --project <project> --profile standard --target http://localhost:<port>
```

For an explicitly authorized target:

```bash
python3 <engine>/scripts/scan.py --project <project> --profile <profile> --target <url> --authorize-target
```

Do not manually execute Semgrep, Gitleaks, Trivy, Syft, Grype, ZAP,
Schemathesis, k6, mitmproxy, or Toxiproxy when `scan.py` supports the selected
workflow. If a direct tool command is necessary because the script lacks a
mode, save raw output under `<project>/.aegis-security/raw/<tool>.json` and
then run normalization/report scripts.

## 4. Platform Recognition Rules

Only claim a platform element when discovery evidence exists.

Language evidence:

- JavaScript/TypeScript: `package.json`, lockfiles, `tsconfig.json`.
- Python: `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`.
- Java/Kotlin: `pom.xml`, `build.gradle`, Gradle wrapper.
- Go: `go.mod`.
- Rust: `Cargo.toml`.
- Ruby: `Gemfile`.
- PHP: `composer.json`.
- .NET: `.csproj`, `.sln`.

Framework evidence examples:

- Next.js: `next` dependency or `next.config.*`.
- React: `react` dependency.
- Express/Fastify/NestJS: dependency plus server bootstrap or route files.
- Django/Flask/FastAPI: dependency plus app/module markers.
- Spring: Maven/Gradle dependencies and `application.yml/properties`.
- Rails: `Gemfile` with Rails and `config/routes.rb`.

Interface evidence examples:

- REST: OpenAPI/Swagger files, route/controller files, API gateway config.
- GraphQL: `.graphql`, `schema.graphql`, Apollo/Yoga dependencies.
- gRPC: `.proto` files.
- WebSockets: ws/socket.io dependencies or gateway classes.
- CLI: bin entries, console scripts, command modules.

Auth evidence examples:

- OAuth/OIDC/SAML libraries or config;
- session/cookie middleware;
- JWT validation middleware;
- route guards, policy decorators, RBAC/ABAC files;
- identity provider environment examples.

If discovery misses a framework that the code clearly indicates, update the
deterministic discovery code or record a finding in the assessment notes. Do
not silently rely on model memory.

## 5. Target Validation Rules

Allowed by default:

- `localhost`
- `127.0.0.1`
- `::1`
- `host.docker.internal`
- RFC1918 private addresses
- Docker networks and named local services

Denied by default:

- public hostnames;
- production domains;
- cloud-hosted URLs;
- third-party APIs;
- URLs discovered in `.env`, config, README, CI/CD, OpenAPI servers, or
  package metadata without explicit user authorization.

For denied targets, stop and report the denial. Do not downgrade active scans
into passive browsing unless that still contacts the denied target.

## 6. Tool Execution Rules

Semgrep:

- Static source analysis.
- Save JSON output to `raw/semgrep.json`.
- Treat rule severity as initial severity, then let correlation raise
  confidence when runtime evidence confirms it.

Gitleaks:

- Secret detection.
- Save JSON output to `raw/gitleaks.json`.
- Redact secret material.
- Recommend rotation when evidence suggests a real secret.

Trivy:

- Filesystem, vulnerability, secret, IaC, and container misconfiguration scan.
- Save JSON output to `raw/trivy.json`.
- Separate vulnerable dependency, secret, and misconfiguration categories in
  interpretation.

Syft:

- Generate SBOM.
- Save JSON output to `raw/syft.json`.
- Missing SBOM should warn the release gate when dependency analysis is
  requested.

Grype:

- Dependency vulnerability analysis.
- Save JSON output to `raw/grype.json`.
- Correlate package identity with Syft when both are available.

ZAP:

- Baseline/passive only in `standard`.
- Active scan only in `adversarial-local` or `full`, and only against
  authorized local/private targets.
- Save JSON output to `raw/zap.json`.

Schemathesis:

- Requires OpenAPI/Swagger evidence.
- Prefer local target.
- Save machine-readable output or report pointer under `raw/schemathesis.*`.

mitmproxy:

- Manual/scenario-specific unless the project ships a configured flow.
- Never intercept unrelated traffic.
- Save explicit scope and observations; do not claim findings without evidence.

k6:

- Requires bounded duration and VU limits.
- Default max: 300 seconds, 500 VUs, lower if user gives lower bounds.
- Stop on high error rate or resource exhaustion.

Toxiproxy:

- Requires named local dependency and cleanup plan.
- Always restore proxy state during cleanup.

## 7. Normalization

Every raw result must become a canonical finding before it appears in final
reports. Canonical fields:

- `id`: stable `SEC-###`.
- `fingerprint`: deterministic hash from rule, component, location, endpoint,
  dependency, CWE, and normalized title.
- `severity`: `critical`, `high`, `medium`, `low`, or `info`.
- `confidence`: `high`, `medium`, or `low`.
- `source`: tool, rule ID, raw reference.
- `classification`: CWE, OWASP, OWASP API, CVSS.
- `component`: service, file, line, endpoint, dependency.
- `evidence`: redacted snippets or raw references.
- `risk`: exploitability, impact, likelihood.
- `remediation`: summary, architectural action flag, recommended actions.
- `status`: `open`, `accepted`, `fixed`, or `false-positive`.

If a tool emits data that cannot be mapped, preserve the raw file and add a
normalization warning. Do not invent missing CWE/CVSS/classification data.

## 8. Deduplication and Correlation

Deduplicate findings when they refer to the same weakness in the same affected
component. Use the fingerprint fields before natural-language judgment.

Correlation may raise confidence when:

- SAST and DAST identify the same endpoint/code path;
- a secret finding also appears in container or CI/CD context;
- a vulnerable dependency is reachable from an exposed service;
- IaC/container misconfiguration exposes a vulnerable service.

Attack chains require at least two linked findings and a plausible transition.
Label assumptions explicitly.

## 9. Release Gate and Score

Use `assessment.json` as source of truth. Default policy:

- fail on any open critical finding;
- fail on more than two open high findings;
- fail on confirmed runtime exploitability for injection, auth bypass, secret
  exposure, or unsafe deserialization;
- warn when required tools were skipped or SBOM is missing.

Do not override the gate because the model feels the project is safe.

## 10. Reporting

Generate:

- `security-assessment.md`: technical report for engineers/security reviewers.
- `specmaster-remediation.md`: implementation roadmap for SpecMaster.

The report must distinguish:

- evidence collected;
- model interpretation;
- prioritization;
- recommendation;
- implementation tasks.

The final chat response should be short and cite artifact paths instead of
copying full reports.

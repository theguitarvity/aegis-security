# Secrets Management

Use this reference for secrets in source, history, config, CI/CD, containers,
logs, examples, and generated artifacts.

## Evidence First

Run the harness so Gitleaks and Trivy secret scanning can produce raw and
normalized evidence. Never paste discovered secret values into chat or reports.
If you must refer to evidence, use file path, line number, detector/rule, and a
redacted preview.

## Required Review Steps

1. Run `scripts/scan.py --profile quick`.
2. Inspect normalized findings from `normalized-findings.json`.
3. If a secret tool reports a high-confidence credential, treat it as possibly
   compromised even when the repo is private.
4. Search only for context, not for displaying values: `rg -n
   "(SECRET|TOKEN|PASSWORD|PRIVATE KEY|AWS_|GITHUB_|SLACK_|STRIPE_|DATABASE_URL)"`.
5. Check `.env.example`, CI workflows, Docker/Compose files, test fixtures,
   deployment manifests, and README snippets.

## Findings To Open

Open a finding when evidence shows:

- private keys, access tokens, API keys, OAuth client secrets, database URLs,
  signing secrets, webhook secrets, cloud credentials, or provider tokens in
  repo files;
- secrets copied into Docker images through `ARG`, `ENV`, `COPY`, or build
  logs;
- CI/CD workflows echo secrets, pass them to untrusted scripts, or expose them
  to pull requests from forks;
- credentials shared across environments;
- secrets stored in plaintext database columns when not required;
- application logs include tokens, cookies, authorization headers, reset links,
  or full connection strings.

## Do Not Open A Finding Solely Because

- an example variable is named `API_KEY` with value `changeme`, `example`, or
  empty placeholder;
- a test fixture uses a fake token format documented as fake;
- a detector reports low-confidence random text without corroborating context.

Mark suspicious but unconfirmed values as manual review, not confirmed secret
exposure.

## Severity Guidance

- `critical`: likely live production credential, signing key, private key, or
  privileged cloud/provider token.
- `high`: non-production credential with possible lateral movement, shared
  environment credential, webhook secret.
- `medium`: sensitive token in logs/artifacts, weak secret injection pattern,
  missing rotation path.
- `low`: placeholder confusion or hardening gap with no secret value.

## Remediation Guidance

- revoke and rotate exposed credentials before removing them from code;
- purge history when appropriate, but do not treat history rewrite as rotation;
- move secrets to a managed secret store or CI secret mechanism;
- pass secrets at runtime instead of build time;
- add secret scanning to CI;
- add redaction filters for logs, traces, and reports;
- document owner and rotation cadence for each high-value secret.

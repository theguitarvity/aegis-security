# Threat Modeling

Use this reference to turn discovery into a practical threat model. Threat
models must be evidence-backed and should expose decisions the team can act on.

## Inputs

- `discovery.json`
- routes/controllers/API contracts
- auth/authz evidence
- Docker/Compose/Kubernetes/IaC
- CI/CD workflows
- data stores, queues, caches, object storage
- third-party integrations and webhooks
- normalized findings when available

## Required Sections

1. Actors: anonymous user, authenticated user, tenant admin, system admin,
   service account, CI job, third-party provider, attacker-controlled client.
2. Entry points: HTTP routes, APIs, webhooks, background jobs, CLI, queues,
   file uploads, admin panels, CI triggers.
3. Trust boundaries: browser/API, API/database, API/provider, CI/registry,
   public/private network, tenant/user boundary.
4. Data flows: sensitive data movement and storage.
5. Privileged operations: admin changes, billing, exports, credential
   creation, impersonation, destructive jobs.
6. STRIDE table: spoofing, tampering, repudiation, information disclosure,
   denial of service, elevation of privilege.
7. Existing controls and missing controls.
8. Findings/roadmap links.

## Evidence Rules

- Mark each item as `explicit`, `discovered`, `inferred`, or `unknown`.
- `inferred` requires a stated reason.
- Do not turn unknowns into findings unless the absence of a control is itself
  evidenced and material.
- Public URLs in config are dependencies or deployment hints, not scan
  authorization.

## Output Shape

Use tables:

```text
Component | Trust boundary | Data | Entry point | Threat | Control | Gap
```

Attack surface sketch:

```text
Actor -> Frontend -> API -> Domain -> Database
API -> External Provider
CI/CD -> Registry -> Runtime
```

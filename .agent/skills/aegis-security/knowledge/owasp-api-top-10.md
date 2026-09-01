# OWASP API Security Top 10

Use OWASP API Security Top 10 when discovery finds REST, GraphQL, gRPC,
webhooks, or other API interfaces.

## Evidence First

Use OpenAPI/Swagger, route/controller/resolver files, auth middleware, tests,
and runtime DAST/API results. Do not infer API exposure from a dependency
alone.

## Common Categories

- Broken Object Level Authorization: object IDs accepted without ownership or
  tenant checks.
- Broken Authentication: weak token/session/API-key flows.
- Broken Object Property Level Authorization: over-posting, mass assignment,
  field-level data exposure.
- Unrestricted Resource Consumption: unbounded pagination, expensive queries,
  uploads, exports, or async jobs.
- Broken Function Level Authorization: lower-privileged user can call admin or
  privileged operation.
- Unrestricted Access to Sensitive Business Flows: abuse-prone workflows such
  as signup, purchase, invite, reset, scraping, or booking without controls.
- Server-Side Request Forgery: API fetches untrusted URLs.
- Security Misconfiguration: unsafe CORS, debug, default admin, verbose errors.
- Improper Inventory Management: undocumented/shadow/deprecated API versions.
- Unsafe Consumption of APIs: trusting third-party payloads without validation,
  signature verification, or timeout constraints.

## Findings To Open

Open API findings only when a concrete endpoint, resolver, webhook, schema, or
contract path is involved. Include method/path or resolver name in
`component.endpoint` when known.

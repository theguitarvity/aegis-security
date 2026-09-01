# Secure Design

Use this reference for architectural review and threat-model-derived findings.
Secure design findings must tie to a concrete component, trust boundary,
privileged operation, or data flow.

## Review Areas

- trust boundaries between browser, API, worker, database, cache, queue,
  storage, third-party providers, and CI/CD;
- sensitive data classification and minimization;
- secure defaults and deny-by-default behavior;
- least privilege for users, services, jobs, and infrastructure;
- input validation at boundaries and output encoding at rendering sinks;
- idempotency and replay resistance for payments/webhooks/jobs;
- audit logs for privileged and security-sensitive actions;
- failure modes: timeout, partial failure, dependency outage, retry behavior;
- data retention, deletion, export, and privacy-sensitive workflows.

## Findings To Open

Open a finding when evidence shows:

- no trust boundary control for sensitive cross-boundary data;
- privileged operation lacks auditability;
- user-controlled input reaches dangerous sinks without validation/encoding;
- insecure default config enables public access, debug mode, broad CORS, or
  unauthenticated admin behavior;
- service/job has broad permissions beyond required operations;
- webhook/event handler lacks replay protection or sender verification;
- sensitive data retained or logged without clear need;
- error handling leaks secrets, stack traces, or internal data to users.

## Do Not Open A Finding Solely Because

- architecture is simple;
- custom design differs from a preferred pattern;
- a control is implemented in a place you did not expect.

Require a concrete risk path.

## Remediation Guidance

- add explicit trust-boundary controls and tests;
- centralize validation and policy enforcement near entry/data boundaries;
- default to deny/least privilege;
- introduce audit events for privileged operations;
- design safe retries, idempotency keys, and replay protection;
- reduce sensitive data collection and retention;
- replace debug/public defaults with environment-specific secure defaults.

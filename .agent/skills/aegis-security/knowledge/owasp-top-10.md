# OWASP Top 10

Use OWASP Top 10 as a web application risk taxonomy. Category membership is
classification, not proof.

## Use Rules

- Map a finding to OWASP only after the vulnerability is evidenced.
- Prefer tool-provided mappings when available.
- Do not force every finding into OWASP; supply-chain, CI/CD, and container
  issues may be better represented elsewhere.

## Common Categories

- Broken Access Control: missing object/function/tenant authorization,
  privilege escalation, insecure direct object reference.
- Cryptographic Failures: weak crypto, missing TLS validation, sensitive data
  exposure.
- Injection: SQL/NoSQL/command/template/LDAP injection.
- Insecure Design: missing threat controls, unsafe workflow design, missing
  abuse constraints.
- Security Misconfiguration: debug mode, unsafe headers, permissive CORS,
  exposed admin, default credentials.
- Vulnerable and Outdated Components: vulnerable dependencies/base images.
- Identification and Authentication Failures: weak login/session/token flows.
- Software and Data Integrity Failures: unsafe CI/CD, unsigned artifacts,
  dependency trust gaps.
- Security Logging and Monitoring Failures: missing audit logs for sensitive
  actions.
- Server-Side Request Forgery: untrusted URL fetches crossing trust boundary.

## Reporting

Include OWASP mapping under `classification.owasp`. Keep the evidence in
`evidence` and `component`; do not make the category the finding title unless
the tool does so.

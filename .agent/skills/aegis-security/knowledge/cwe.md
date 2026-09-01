# CWE

Use CWE to classify weakness type. CWE classification helps triage and
roadmapping, but it must not replace evidence.

## Rules

- Prefer CWE IDs emitted by Semgrep, Trivy, Grype, ZAP, or another tool.
- Add a CWE manually only when the weakness class is unambiguous from code or
  config evidence.
- Leave CWE empty when classification is uncertain.
- Do not cite CWE descriptions as proof that the project is vulnerable.

## Frequent Mappings

- SQL injection: CWE-89.
- Command injection: CWE-78.
- Path traversal: CWE-22.
- Cross-site scripting: CWE-79.
- Cross-site request forgery: CWE-352.
- Server-side request forgery: CWE-918.
- Hardcoded credential: CWE-798.
- Missing authentication: CWE-306.
- Missing authorization: CWE-862.
- Incorrect authorization: CWE-863.
- Cleartext transmission: CWE-319.
- Weak password hashing: CWE-916 or CWE-327 depending on evidence.
- Insecure random values: CWE-330.
- Deserialization of untrusted data: CWE-502.
- Information exposure in logs/errors: CWE-532 or CWE-209.

Use these mappings as defaults only after evidence confirms the weakness.

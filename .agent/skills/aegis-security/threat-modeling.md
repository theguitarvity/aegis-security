# Threat Modeling Guide

Derive threat models from discovery evidence. Identify actors, entry points,
trust boundaries, privileged operations, sensitive data, external dependencies,
and operational controls.

Use STRIDE for component-level threats and map likely web/API risks to OWASP
Top 10, OWASP API Top 10, and CWE when appropriate.

Simple surface sketch:

```text
Actor -> Frontend -> API -> Domain -> Database
API -> External Provider
CI/CD -> Registry -> Runtime
```

For each component capture: trust boundary, data classification, attack
surface, potential threat, existing control, and missing control.

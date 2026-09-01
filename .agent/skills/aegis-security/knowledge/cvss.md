# CVSS

Use CVSS to preserve vendor/tool severity context. Aegis severity is separate
and may consider reachability, exploitability, exposure, and correlation.

## Rules

- Preserve CVSS vector and score from tool output when present.
- Do not manually compute CVSS unless the user explicitly asks for formal CVSS.
- If a dependency tool provides multiple CVSS records, keep the relevant vendor
  source and avoid collapsing detail into a single invented score.
- Do not lower a critical policy finding only because no CVSS exists.
- Do not raise severity solely because a theoretical CVSS score is high when
  the affected package/component is not installed or reachable.

## Interpretation Guidance

- Network attack vector plus unauthenticated exploitability increases priority.
- Local-only vulnerabilities may still matter in CI/build/container contexts.
- Availability-only CVEs may become high priority for public critical services.
- CVSS does not cover secret exposure, authorization design flaws, and many
  architecture issues cleanly; use Aegis severity policy for those.

# STRIDE

Use STRIDE to classify threat-model items. STRIDE is a taxonomy, not evidence.
Do not open a finding just because a STRIDE category could apply.

## Categories

- Spoofing: pretending to be another user, service, tenant, webhook sender, or
  identity provider.
- Tampering: unauthorized modification of data, config, requests, events,
  artifacts, logs, or release outputs.
- Repudiation: inability to prove who performed a sensitive action.
- Information disclosure: unauthorized data exposure through APIs, logs,
  errors, storage, caches, exports, or side channels.
- Denial of service: resource exhaustion, unbounded work, dependency failure,
  retry amplification, lock contention.
- Elevation of privilege: moving from lower privilege to admin, tenant owner,
  service account, CI write permission, or broader role.

## Use Rules

For each threat, identify:

- actor;
- asset;
- entry point;
- trust boundary;
- missing or weak control;
- evidence source;
- potential finding ID or `none`.

If any field is unknown, mark it unknown. Do not invent it.

## Common Mappings

- Missing object-level authorization: elevation of privilege or information
  disclosure.
- Unverified webhook: spoofing and tampering.
- Missing audit log for admin action: repudiation.
- Broad CORS with credentials: information disclosure/tampering depending on
  exploitability.
- Unbounded upload or expensive query: denial of service.
- Unsigned mutable release artifact: tampering.

# Authorization

Use this reference for access control review after authentication has been
identified. Authorization findings must point to a protected object, function,
tenant boundary, role/policy, or privileged operation.

## Evidence First

Look for route guards, middleware, policy classes, decorators, annotations,
role checks, tenant filters, ownership checks, SQL predicates, ORM scopes,
GraphQL resolvers, admin routes, feature flags, and tests.

Do not assume that authentication implies authorization. Do not assume a
middleware name enforces object-level checks; confirm where the protected data
is loaded and returned or mutated.

## Required Review Steps

1. Identify privileged actions: admin panels, user management, billing,
   exports, API keys, integrations, webhooks, impersonation, organization
   settings, roles, and destructive operations.
2. Identify object references: IDs in paths, query params, request bodies,
   GraphQL variables, message payloads, and file names.
3. Trace each protected operation from entry point to data access. Verify the
   check happens before mutation/response and uses trusted server-side
   identity.
4. Compare read, create, update, delete, export, and bulk endpoints. Teams
   often protect read paths and miss bulk/export/mutation paths.
5. Use tests, policy files, and normalized tool output as evidence.

## Findings To Open

Open a finding when evidence shows:

- direct object reference without owner/tenant/policy check;
- role checks only in frontend code;
- authorization enforced after data is fetched, logged, streamed, or mutated;
- admin/debug/internal endpoint exposed without strong checks;
- tenant ID, user ID, role, organization ID, or scope accepted from client and
  trusted directly;
- GraphQL resolver bypasses REST/controller policy;
- batch/export endpoints omit per-object authorization;
- webhook handlers allow cross-tenant action or unverified sender identity;
- service-to-service calls use broad credentials without scoped authorization;
- tests show missing negative cases for critical protected operations.

## Do Not Open A Finding Solely Because

- a route has an ID parameter;
- RBAC uses string roles;
- authorization logic is custom;
- policy names are unfamiliar.

Require a demonstrable path from untrusted or lower-privileged actor to
unauthorized data/action.

## Severity Guidance

- `critical`: cross-tenant data access, admin privilege escalation, account or
  billing takeover, mass export of sensitive data.
- `high`: object-level bypass for sensitive records, role escalation,
  unauthorized destructive mutation.
- `medium`: missing authorization on lower-sensitivity data, inconsistent
  policy coverage, weak service scopes.
- `low`: missing tests or audit logs for otherwise protected operations.

## Remediation Guidance

- enforce authorization server-side at the operation/data-access boundary;
- use centralized policy/guard abstractions with explicit deny-by-default;
- derive tenant/user context from trusted identity, never client input;
- add negative tests for every role and tenant boundary;
- protect bulk/export/background/job paths with the same policies as single
  object operations;
- log denied privileged attempts without leaking sensitive data.

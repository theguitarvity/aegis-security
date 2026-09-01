# Authentication

Use this reference when discovery indicates login, sessions, tokens, API keys,
OAuth/OIDC/SAML, password reset, MFA, service accounts, or machine-to-machine
authentication.

## Evidence First

Do not assume the authentication model. Identify it from files, dependencies,
configuration, route handlers, middleware, annotations, guards, tests, and
OpenAPI security schemes.

Evidence markers:

- web sessions: cookie/session middleware, server-side session stores, CSRF
  middleware, `Set-Cookie`, `HttpOnly`, `SameSite`, `Secure`.
- JWT: JWT libraries, token verification middleware, `Authorization: Bearer`,
  JWKS, issuer/audience config, refresh token flows.
- OAuth/OIDC: client ID, issuer, discovery URL, callback routes, PKCE,
  scopes, identity provider config.
- SAML: metadata XML, ACS routes, entity ID, certificate config.
- API keys: header names, key hashing/storage, service account models.
- password login: password hashing library, password policy, reset tokens,
  account lockout/rate limiting.
- MFA: TOTP/WebAuthn/SMS/email challenge code, backup codes, step-up checks.
- machine-to-machine: client credentials, workload identity, mTLS, signed
  requests, internal service tokens.

If discovery does not show an auth mechanism, write `authentication: not
detected` instead of inventing one.

## Required Review Steps

1. Read `discovery.json` and identify auth-related files listed under
   `authentication`, `interfaces`, and framework markers.
2. Search the project for concrete auth terms with `rg`: `login`, `logout`,
   `session`, `jwt`, `bearer`, `oauth`, `oidc`, `saml`, `password`, `reset`,
   `mfa`, `totp`, `webauthn`, `api key`, `apikey`, `client_secret`,
   `refresh_token`.
3. Prefer existing tests for auth behavior before inferring behavior from
   implementation names.
4. Run Aegis scan scripts before writing findings. Use normalized findings as
   source of truth for report IDs.
5. Only create a manual finding when code/config evidence shows a specific
   weakness not emitted by a tool.

## Findings To Open

Open a finding when evidence shows:

- password hashes use weak algorithms, plain hashing, reversible encryption,
  unsalted hashes, or hardcoded salts;
- session cookies miss `HttpOnly`, `Secure`, or appropriate `SameSite` for the
  deployment model;
- JWTs are decoded without signature verification or accept weak/none
  algorithms;
- issuer, audience, expiration, not-before, or key rotation are not validated;
- refresh tokens are long-lived without rotation, revocation, reuse detection,
  or secure storage;
- password reset tokens are predictable, reusable, not expired, not bound to
  account context, or leaked in logs;
- login, reset, MFA, or OTP endpoints lack rate limiting or abuse controls;
- MFA bypass exists for privileged operations or account recovery;
- service credentials are shared across environments or stored in repo/config;
- API keys are stored in plaintext when a hashed representation would work;
- auth middleware is absent from protected routes that handle sensitive data or
  privileged actions;
- test fixtures expose real tokens, secrets, users, or provider credentials.

## Do Not Open A Finding Solely Because

- a route is named `login` or `auth`;
- a dependency has had historical CVEs but no installed vulnerable version was
  detected;
- a README mentions a public identity provider;
- an `.env.example` contains placeholder values;
- auth behavior is unknown. Mark it as `unknown` and recommend validation.

## Severity Guidance

- `critical`: auth bypass for admin/tenant data, token signing key exposure,
  real production credential exposure, password reset takeover.
- `high`: missing signature/audience validation, MFA bypass for privileged
  actions, plaintext reusable API keys, weak password hashing in production.
- `medium`: missing rate limiting on auth endpoints, cookie flags incomplete
  in a non-production config, refresh token lifecycle gaps.
- `low`: hardening gaps, incomplete logging/auditability, documentation drift.
- `info`: architecture notes without demonstrated exploitability.

## Remediation Guidance

Recommend concrete controls tied to evidence:

- centralize auth enforcement in middleware/guards and test every protected
  route;
- use vetted password hashing such as Argon2id, bcrypt, or scrypt with
  appropriate cost;
- validate JWT issuer, audience, signature, expiration, not-before, and key ID;
- use short-lived access tokens and rotated, revocable refresh tokens;
- set secure cookie attributes and CSRF protections based on client type;
- add rate limits and abuse telemetry to login, reset, OTP, and token flows;
- bind reset/MFA tokens to user, purpose, expiry, and one-time use;
- hash API keys at rest and show raw values only once at creation;
- rotate any secret that may have been committed or logged.

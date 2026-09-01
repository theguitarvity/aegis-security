# Supply Chain

Use this reference for dependencies, lockfiles, package managers, build
scripts, CI/CD, SBOM, provenance, registries, and release integrity.

## Evidence First

Prefer Syft and Grype output for package inventory and vulnerability evidence.
Use manifest/lockfile inspection to explain reachability and remediation, not
to invent CVEs.

## Required Review Steps

1. Identify package managers and lockfiles from `discovery.json`.
2. Run `scripts/scan.py --profile quick`.
3. Confirm whether SBOM generation succeeded (`raw/syft.json` or tool status).
4. Inspect install scripts, postinstall hooks, GitHub Actions, package publish
   jobs, Docker build jobs, dependency update automation, and registry config.
5. Map dependency findings to runtime components when possible.

## Findings To Open

Open a finding when evidence shows:

- critical/high vulnerable dependency from Grype/Trivy with installed affected
  version;
- missing lockfile for package ecosystem where lockfiles are expected;
- dependency fetched from untrusted Git URL, tarball, local path, or mutable
  branch in production path;
- install scripts execute untrusted code in CI/release path;
- CI/CD token has broad write permissions not needed by the workflow;
- release job can be triggered from untrusted pull request context;
- package publish lacks provenance/signing where project policy requires it;
- container base image has material vulnerabilities or unsupported OS;
- SBOM cannot be generated for a release artifact.

## Do Not Open A Finding Solely Because

- a package is old without a vulnerability/advisory or policy requirement;
- dev dependency has a CVE with no build/runtime impact unless CI exposure is
  relevant;
- there is no SBOM for a toy/local project and user did not request release
  gating.

## Severity Guidance

- `critical`: compromised release path, writable CI token exposure, malicious
  package execution, critical reachable dependency in exposed service.
- `high`: high vulnerable runtime dependency, unsafe publish workflow, broad
  CI permissions on protected branches.
- `medium`: missing lockfile, unsupported base image, incomplete SBOM, risky
  dependency source.
- `low`: hygiene gaps and update automation improvements.

## Remediation Guidance

- update or patch vulnerable dependencies;
- add/commit lockfiles and enforce frozen installs in CI;
- restrict CI permissions per job;
- separate pull request validation from release/publish credentials;
- generate SBOM for release artifacts;
- pin container bases by digest for releases;
- enable dependency review and automated update PRs with tests.

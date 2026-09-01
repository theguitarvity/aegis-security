# Containers

Use this reference when discovery finds Dockerfiles, Compose, Kubernetes,
Helm, or runtime manifests.

## Evidence First

Use Trivy output when available, then inspect Dockerfile/manifest evidence.
Do not infer runtime exposure from a Dockerfile alone; distinguish image build
risk from deployment risk.

## Required Review Steps

1. List Dockerfiles, Compose files, Kubernetes/Helm manifests, and CI image
   build jobs from `discovery.json`.
2. Run `scripts/scan.py --profile quick` so Trivy can assess filesystem,
   secret, vulnerability, and misconfiguration categories when installed.
3. Inspect base images, user, package installation, copied files, exposed
   ports, health checks, capabilities, volumes, networks, and secret handling.
4. For Kubernetes, inspect security context, RBAC, service account, ingress,
   network policies, probes, resources, and secret references.

## Findings To Open

Open a finding when evidence shows:

- container runs as root without need;
- privileged mode, broad Linux capabilities, host networking, host PID/IPC, or
  Docker socket mounted;
- secrets baked into image layers or provided as Dockerfile `ENV`;
- sensitive files copied into images, including `.env`, SSH keys, cloud
  credentials, or package registry tokens;
- vulnerable or unsupported base image with material CVEs;
- mutable or floating base tag for production image without digest pinning;
- missing resource limits for workloads exposed to untrusted traffic;
- Kubernetes service account token unnecessarily mounted;
- public ingress exposes admin/debug/internal service;
- no readiness/liveness checks for critical service.

## Do Not Open A Finding Solely Because

- `EXPOSE` appears in a Dockerfile;
- a container uses root during build stages but final runtime is non-root;
- a base image has CVEs in unused packages with no reachable service impact,
  unless policy fails on any CVE.

## Severity Guidance

- `critical`: Docker socket mount in exposed workload, privileged container
  with public attack surface, baked production secrets.
- `high`: root runtime plus exploitable service, high/critical reachable base
  image CVEs, public admin ingress.
- `medium`: missing resource limits, broad capabilities, mutable tags in
  release images, weak secret injection.
- `low`: hardening improvements without clear exploit path.

## Remediation Guidance

- use minimal, supported, pinned base images;
- run as non-root in final stage;
- drop capabilities and set read-only filesystem when feasible;
- remove secrets from image layers and inject at runtime through secret stores;
- avoid Docker socket mounts in application workloads;
- add resource limits, probes, and network policies;
- split build and runtime stages to reduce attack surface.

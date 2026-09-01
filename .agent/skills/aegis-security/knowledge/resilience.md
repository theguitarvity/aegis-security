# Resilience

Use this reference only for local/private, explicitly authorized resilience and
load testing. These tests can affect availability, so policy bounds are
mandatory.

## Required Preconditions

- profile is `resilience` or `full`;
- target is localhost, loopback, Docker, or explicitly authorized private
  sandbox;
- duration, virtual users, target endpoints, and stop conditions are bounded;
- cleanup plan exists for proxies, containers, and test data.

## Scenarios

- baseline latency and throughput for critical endpoints;
- spike traffic within configured limits;
- dependency latency with Toxiproxy;
- dependency timeout/failure;
- packet loss or connection reset for local dependency;
- retry storm detection;
- rate-limit behavior;
- graceful degradation when cache, queue, provider, or database is impaired.

## Findings To Open

Open a finding when evidence shows:

- unbounded retries amplify dependency failure;
- missing timeouts/circuit breakers cause request pileup;
- no rate limiting on expensive or abuse-prone endpoint;
- failure of optional dependency takes down critical path;
- resource exhaustion under bounded policy limits;
- load test triggers error rate above policy threshold;
- cleanup failure leaves proxy or test state active.

## Do Not Open A Finding Solely Because

- no load test was run due to missing authorization;
- performance is unknown;
- a dependency can fail in theory.

Record skipped coverage instead.

## Remediation Guidance

- set timeouts, retry budgets, exponential backoff, and circuit breakers;
- add rate limits and queue limits;
- make optional dependencies degrade gracefully;
- add health/readiness probes that reflect dependency state;
- add local resilience tests to CI or pre-release checks where safe;
- ensure cleanup restores network/proxy state.

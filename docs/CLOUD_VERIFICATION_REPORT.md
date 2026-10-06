# Cloud verification report

## Status

**No captured live cloud verification evidence is present in this repository.**

This checkout must not be described as currently attested or as having successfully
released the protected synthetic resource from a live Confidential Space workload.
The cloud implementation and verification procedure are prepared, but the observed
GCP checks remain pending.

## What is verified locally

- The policy engine evaluates authoritative sensitivity and confirmation state.
- Denied decisions cannot invoke an executor through the `CapabilityGate`.
- Missing, malformed, unknown, replayed, and error states fail closed.
- Offline mode creates no model or cloud client and needs no network, credentials,
  Gemini, or DNS.
- Attestation-gated resource release is covered by local boundary tests using
  synthetic evidence and data.

These checks do not constitute remote attestation or live protected-resource
release.

## Required live evidence

The procedure in [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) requires both:

1. denial when an unauthorised local principal requests the synthetic Secret
   Manager resource; and
2. successful release only to the expected digest-bound Confidential Space
   workload after launcher-token exchange, WIF/IAM evaluation, and expected-value
   hash validation.

Only captured observations of those checks can change this report to verified.

## Claim boundary

Even a successful future resource release would establish a narrower claim:
attested workload and environment properties satisfied the relying party's release
conditions. It would not prove model correctness, policy correctness, or application
freedom from bugs. Gemini inference remains remote and outside this project's TEE.

See [ADR-001](ADR-001-CONFIDENTIAL-RUNTIME.md), the
[threat model](THREAT_MODEL.md), and the
[official-source review](CLOUD_VERIFICATION_SOURCES.md) for the exact boundary.

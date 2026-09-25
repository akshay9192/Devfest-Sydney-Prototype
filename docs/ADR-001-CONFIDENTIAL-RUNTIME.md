# ADR-001: Use Confidential Space for protected resource release

- Status: Accepted for deployment; not yet deployed
- Date: 2026-09-25

## Context

The prototype needs a containerized controller, real remote attestation, and a
simple proof that a synthetic protected value is released to an authorized workload
but not to a local or wrongly measured caller.

## Comparison

| Criterion | Confidential Space | Confidential VM |
|---|---|---|
| Threat model | Hardened container workload protected from a potentially privileged operator | General VM memory isolation; guest OS and workload management remain the customer's responsibility |
| Deployment complexity | Opinionated image, launcher metadata, Artifact Registry, WIF provider, IAM conditions | Familiar VM deployment, but workload measurement and a relying-party release flow require more custom work |
| Attestation | Google Cloud Attestation issues OIDC tokens with Confidential Space, container, VM, project, service-account, and image claims | vTPM/hardware reports; Google Cloud Attestation support varies by technology and custom policy verification is needed |
| Protected secret release | Documented direct federated-resource or service-account impersonation patterns | Must assemble verifier, identity exchange, and resource policy more manually |
| Networking | Container networking is available but production image constraints and egress must be planned | General Compute Engine networking |
| Demo reliability | More setup, but the resource-release result directly demonstrates the intended claim | Easier debugging, less direct binding between app image and released resource |
| Cost | No extra Confidential Space fee; pay for the underlying VM and used services | Pay for VM and used services; configuration determines premium/availability |
| Limitations | Single-purpose workload model, supported zones/machines, production image limits, cloud prerequisites | Larger TCB and more ways to accidentally attest the VM while failing to bind the application |

## Decision

Use Confidential Space on a minimum supported CPU-only machine, selected only after
checking the intended project's region, zone, quota, and current supported
configurations. Use the production `confidential-space` image for the final result.
Constrain a Workload Identity Pool provider on `swname == 'CONFIDENTIAL_SPACE'`, the
`STABLE` support attribute, workload container digest, project, and service-account
claims that fit the final deployment. Grant that federated identity access to one
version of a non-sensitive Secret Manager secret.

The app will call Vertex AI through the `google-genai` SDK using short-lived
Application Default Credentials. The remote inference is outside this project's
TEE; only minimum synthetic context is sent.

## Threat boundary

Attestation increases confidence in the environment, boot state, Confidential
Space image, and bound workload identity represented by checked claims. IAM then
uses those claims to release a resource. It does not prove source-code intent,
runtime freedom from bugs, policy correctness, model correctness, or that remote
Gemini inference ran inside the TEE.

## Operational consequence

The cloud demo is incomplete until two observations exist: an unauthorized local
principal cannot read the secret, and the attested digest-constrained workload can.
A decoded token or green UI label alone is insufficient.

## Sources

- [Confidential Space overview](https://cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview)
- [Create and grant access to confidential resources](https://cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources)
- [Deploy Confidential Space workloads](https://cloud.google.com/confidential-computing/confidential-space/docs/deploy-workloads)
- [Google Cloud Attestation](https://cloud.google.com/confidential-computing/docs/attestation)
- [Confidential VM attestation](https://cloud.google.com/confidential-computing/confidential-vm/docs/attestation)
- [Confidential Space pricing](https://cloud.google.com/confidential-computing/confidential-space/pricing)

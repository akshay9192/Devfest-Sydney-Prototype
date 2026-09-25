# Goal

Build a resilient DevFest Sydney prototype that demonstrates one claim: an LLM may
propose an action, but deterministic software and a capability boundary decide
whether that action can execute.

# Non-goals

- Claiming that Gemini is deterministic or that Markdown enforces policy.
- Claiming that attestation proves a recommendation is correct.
- Processing or transmitting real confidential data.
- Autonomous policy mutation, a database, microservices, Kubernetes, or custom
  cryptography.
- Reproducing EvoHunt's playbook evolution system.

# Technical claims we intend to demonstrate

- `PLAYBOOK.md` can influence a typed proposal but cannot grant authority.
- Strict schema validation rejects malformed, ambiguous, and extended model output.
- The same proposal and authoritative policy produce the same decision.
- A denied action and an unknown capability never reach an executor.
- Receipts identify inputs and decisions without retaining document contents.
- Offline mode makes no model or cloud network calls.
- A Confidential Space deployment can use attestation claims and workload identity
  to gate a synthetic protected resource.

# Claims we explicitly will NOT make

- Gemini inference runs inside this project's TEE.
- Confidential Computing proves semantic correctness, policy correctness, or model
  correctness.
- This architecture is a novel research contribution.
- Cached evidence is live attestation.
- A policy hash is proof that the policy itself is good.

# Architecture

```text
untrusted request + advisory playbook
                 |
                 v
       Gemini / deterministic fake
          typed Proposal only
                 |
                 v
      deterministic PolicyEngine <--- authoritative YAML + app confirmation state
                 |
        ALLOW ---+--- DENY
          |             |
          v             +----> receipt only
   CapabilityGate
          |
   fixed executor map
          |
   local summary or simulated sink
```

FastAPI serves a one-screen static interface and four demo actions. The process
keeps demo state in memory under a lock; policy and playbook files are read from
fixed paths. The model receives synthetic scenario metadata and advisory text, but
never a callable tool or policy-write interface.

# Threat model

Treat browser input, user text, playbook text, candidate rules, model output, and
cached evidence as untrusted. Trust the small Python controller, immutable runtime
configuration, policy files loaded from fixed paths, executor mapping, and—only in
cloud mode—the configured attestation/resource-release chain. Protect policy
authority, executor capabilities, credentials, synthetic protected state, and
receipt integrity/confidentiality. See `docs/THREAT_MODEL.md` for details.

# Development phases

The work is governed by a strict local-first gate:

1. Inspect the repository, environment, skills, architecture, and threat model.
2. Complete the domain, authoritative context, deterministic policy, capability,
   receipt, proposer, and local attestation boundaries.
3. Build the stage interface around backend-generated events and explicit fallback
   labels. Review desktop and mobile screenshots before accepting the design.
4. Run unit, integration, property, adversarial, chaos, browser, accessibility,
   repeatability, clean-install, container, and offline-network verification.
5. Record every local requirement in `docs/LOCAL_READINESS.md`. Cloud work is
   forbidden until every row has evidence and the document says `LOCAL READINESS:
   PASS`.
6. After that gate only, revalidate official GCP documentation, deploy the same
   container to Confidential Space, and test real authorized and unauthorized
   protected-resource release.
7. Rehearse live and fallback paths, run `make release-check` and `make cloud-verify`,
   clean the repository, and push only the fully verified result.

The local design pass uses a deep graphite base (`#090b0f`), carbon panels
(`#11151b`), quiet text (`#9aa5b4`), paper text (`#f3f6fa`), proposal blue
(`#78a8ff`), allow green (`#63d6a3`), and deny coral (`#ff6b5e`). A network font is
deliberately avoided because the offline guarantee is stronger than a cosmetic
dependency; the narrow native stack is tuned through weight, width, and spacing.
The page is a left-to-right authorization rail at desktop sizes and a vertical
sequence on mobile. The only emphatic motion is the poisoned instruction entering
and being stopped at the policy boundary.

# Test strategy

- Unit tests cover strict value types, policy rules, loaders, hashes, receipts,
  state transitions, and capability allowlisting.
- Hypothesis varies reasons and advisory content while holding authoritative inputs
  fixed.
- Adversarial tests cover injection, extra fields, type confusion, claimed consent,
  candidate overrides, replay, concurrency, oversize input, log injection, XSS,
  missing policy/resource, and failed attestation.
- Integration tests spy on executor calls across safe, poisoned, denied, and
  explicitly confirmed flows.
- Playwright waits for network idle, drives the rendered UI, captures screenshots
  and console errors, and checks keyboard access.
- Core deterministic modules must retain at least 90% line coverage.

# GCP deployment strategy

Choose Confidential Space. Build one non-root container, publish it to Artifact
Registry, and run it on a production Confidential Space image backed by a supported
Confidential VM. Map and constrain Google Cloud Attestation claims in a Workload
Identity Pool, including `swname`, stable image support, workload image digest,
project, and service account as appropriate. Grant the federated principal access
to one non-sensitive Secret Manager version. Prove denial from the developer
machine and release from the authorized workload. Vertex AI remains a remote
service called with Application Default Credentials and minimum synthetic context.

# Demo fallback strategy

`make demo-offline` (and its Windows Python equivalent) uses only a deterministic
fake proposer, local policy evaluation, simulated executors, and explicitly labeled
cached example evidence. It performs zero external requests. Screenshots and a
pre-recorded terminal result provide a second fallback, but are never labeled live.

# Success criteria

- The safe scenario allows local summarization.
- Poisoning only the playbook changes the fake model proposal to external upload;
  policy denies it and executor call count remains zero.
- Explicit authoritative confirmation plus an allowlisted synthetic destination
  allows the simulated upload exactly once.
- All local tests, lint, typing, security checks, coverage gate, and browser tests
  pass where their tools are available.
- The exact same UI works offline without network access.
- Documentation separates enforced properties, assumptions, prior art, and limits.
- Cloud status is reported as unverified until real evidence and resource-access
  outcomes are observed.

# Risks

- Model aliases and SDK behavior change; keep the model configurable and validate
  responses again with Pydantic.
- A mutable policy file weakens the authority claim; deployment must restrict who
  can build images and modify protected policy/resources.
- Demo state could cross requests; serialize mutations and bind receipts to request
  IDs.
- YAML coercion and permissive schemas can create ambiguity; use strict types,
  reject unknown fields, and fail closed.
- Browser rendering can turn explanatory model text into XSS; use `textContent`.
- Live cloud/network dependencies can fail on stage; offline mode is the primary
  talk path.

# Open questions

- Which GCP project, billing account, region, and zone are intended? Cloud work must
  wait because `gcloud` is absent and no project can be inspected.
- Which Gemini model is enabled in that project on deployment day? The model ID is
  configurable because current model lifecycle dates are short.
- Is Docker available on the eventual deployment workstation? It is absent here.

# Plan critique

The initial brief contains more machinery than the 70-second technical demo needs.
Candidate-rule promotion, KMS receipt signing, a general rule DSL, persisted state,
and a live variance run are useful follow-ons but distract from the authority
boundary. The MVP therefore keeps candidate rules visibly non-authoritative,
generates unsigned demo receipts, uses a deliberately narrow YAML policy schema,
and makes the variance experiment optional and offline-capable.

Confidential Space is not a web hosting platform and its production image is
deliberately restrictive. Treat it as the attested controller/resource-release
runtime, not as proof that Vertex AI inference is inside the TEE. A stage demo that
shows only a green "verified" badge would be security theatre; the cloud gate is
complete only when the same synthetic secret is denied locally and released to the
claim-constrained workload.

A Python policy engine can only be a reference monitor if every executor path goes
through it. The implementation must keep executor instances private to the
capability gate and expose no generic function-calling or filesystem tool to the
model. Receipt hashes improve traceability but do not prove code or policy quality.

The architecture is not academically novel. AgentSpec, reference-monitor designs,
policy-as-code systems, information-flow work, and tool firewalls already establish
runtime enforcement around agents. The useful contribution is a small, teachable
integration and a careful demonstration of the boundary between mutable procedural
guidance and runtime authority.

The revised implementation scope is therefore: strict proposals, a fixed policy
schema, one capability gate, two simulated executors, safe receipts, one screen,
offline determinism, and one real Confidential Space resource-release test when
cloud prerequisites are available.

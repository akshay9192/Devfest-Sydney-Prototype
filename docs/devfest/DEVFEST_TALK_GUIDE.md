# DevFest talk guide

## Core thesis

Don't put guarantees inside the prompt. Put guarantees around the model. The model
can suggest; deterministic software decides whether any executable capability
exists.

## Audience takeaway

Treat model output as typed but untrusted input. Evaluate authoritative application
state in ordinary policy code, then expose only explicitly allowed capabilities.
Use confidential-computing attestation for the separate question of protected
resource release.

## What to say

- Prompts and playbooks influence behaviour; they do not confer authority.
- `DENY` means the capability gate never calls an executor.
- Unknown, malformed, missing, and error states fail closed.
- The attack slide is a controlled deterministic adversarial example.
- The external executor and all data are synthetic.
- Gemini is a remote Vertex AI service outside this project's TEE.
- The repository is a teaching-oriented engineering synthesis, not a new research
  architecture.
- This checkout documents the cloud design; it does not contain current live
  attestation evidence.

## What not to claim

- Do not claim prompts can guarantee safety or that typed output is trusted.
- Do not claim Confidential Computing proves policy, application, or model
  correctness.
- Do not claim Gemini inference occurs inside the Confidential Space workload.
- Do not describe the simulated upload as a real external integration.
- Do not claim a live cloud verification or current attestation result.
- Do not claim research novelty.

## Five-slide structure

1. Problem: prompts influence behaviour but should not define authority.
2. Architecture: untrusted proposal above the boundary; enforced policy and
   capability mediation below it.
3. Attack: poisoned guidance changes the controlled proposal.
4. Boundary: authoritative confidential state plus no confirmation yields `DENY`;
   the executor is never called.
5. Takeaway: deterministic boundary, separate attested resource-release model, and
   repository QR.

## Questions

**Can you show the demo?**

Yes. The repository includes an offline deterministic demo that needs no network,
credentials, Gemini, or DNS. The talk is intentionally complete without it.

**Is Gemini running inside the TEE?**

No. Gemini inference is remote. The Confidential Space workload protects
controller-held state and supports claim-bound release of protected resources.

**Is this a novel architecture?**

No. It is a small implementation and teaching synthesis of established
reference-monitor, policy-as-code, capability, and confidential-computing ideas.

**Why not just use prompts?**

Prompts influence a probabilistic component and can be overridden, poisoned, or
misinterpreted. A deterministic gate can make an unauthorised capability
unavailable regardless of the proposal.

**What does Confidential Computing actually add?**

It lets a resource owner make protected-state release conditional on attested
workload and environment claims. It does not validate intent or guarantee correct
model output.

# Architecture

## Authority and data flow

```text
UNTRUSTED                         TRUSTED APPLICATION CORE

request ----+
            +--> proposer --> strict Proposal --> PolicyEngine
PLAYBOOK ---+       |                              |
 advisory           | no tools                     +--> Decision + Receipt
                    |                              |
                    +------------------------------+--> CapabilityGate --> executor
                                                        fixed allowlist
```

Authority descends in this order:

1. `SYSTEM_POLICY.yaml` defines non-overridable safety constraints.
2. `VALIDATED_USER_POLICY.yaml` can narrow or personalize behavior within those
   constraints.
3. `PLAYBOOK.md` is untrusted advisory context for the proposer.
4. `CANDIDATE_RULES.yaml` is untrusted staging data and is not loaded by the policy
   engine.

The proposal's `reason` is display-only. Confirmation comes from authoritative
application state, not from a model statement. Extra fields and unknown enum values
are rejected. Loader, evaluation, attestation, or execution uncertainty produces a
deny decision.

## Components

- `RealGeminiProposer` calls Gemini through the current `google-genai` SDK with a
  Pydantic response schema, then validates the result locally again.
- `DeterministicFakeProposer` makes offline demonstrations repeatable: normal
  guidance proposes local processing; the known poison marker proposes an external
  upload.
- `PolicyEngine` evaluates explicit Python conditions backed by narrow YAML data.
- `CapabilityGate` owns the only executor mapping and invokes it only for an allow
  decision whose action is allowlisted.
- `ReceiptService` hashes configuration and records safe decision metadata. It
  excludes input documents, credentials, raw tokens, and arbitrary environment
  values.
- `AttestationProvider` reports local/cached/live state and mediates protected
  resource release. Cached evidence is always labeled as an example.

## Network boundary

In live mode, Gemini is a remote Vertex AI service. This repository's Confidential
Space TEE protects controller-held state and can obtain an attested federated
identity, but it does not place Vertex inference inside this workload TEE. Only
synthetic scenario labels and the minimum advisory context are sent to Gemini.

Offline mode constructs no cloud or model client and performs no outbound request.

## State and concurrency

Demo mutation is intentionally process-local. A lock serializes playbook poison,
reset, and scenario execution, preventing cross-request state changes during a
decision. Replays are rejected using bounded request-ID memory. Restarting the
process restores files from the repository rather than preserving user sessions.

## Confidential Space path

```text
container digest + Confidential Space/VM claims
                       |
                       v
             Google Cloud Attestation
                       |
                       v
          Workload Identity Pool condition
                       |
          pass --------+-------- fail
            |                     |
 synthetic Secret Manager      no resource
 value released                access
```

Attestation establishes measured environment and identity claims evaluated by the
relying party. It does not establish that the policy is correct, the application is
bug-free, or a recommendation is semantically sound.

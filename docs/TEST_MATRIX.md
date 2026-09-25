# Test matrix

| Case | Expected proposal | Authoritative context | Policy result | Executor called? | Expected UI state | Tests |
|---|---|---|---|---|---|---|
| SAFE_LOCAL | `SUMMARIZE_LOCALLY` | confidential, unconfirmed | ALLOW | once | local capability executed | integration, E2E |
| CONFIDENTIAL_EXTERNAL_NO_CONFIRMATION | `UPLOAD_EXTERNAL` | confidential, unconfirmed | DENY | no | boundary locked | unit, property |
| CONFIDENTIAL_EXTERNAL_CONFIRMED | `UPLOAD_EXTERNAL` | confidential, confirmed | ALLOW | once | simulated upload | integration |
| POISONED_PLAYBOOK | `UPLOAD_EXTERNAL` | confidential, unconfirmed | DENY | no | poison visible, guarantee unchanged | integration, E2E |
| MALFORMED_PROPOSAL | invalid | confidential, unconfirmed | DENY | no | invalid proposal | adversarial |
| UNKNOWN_ACTION | rejected by schema | confidential, unconfirmed | DENY | no | invalid proposal | unit, adversarial |
| POLICY_FILE_CORRUPTED | any/none | confidential, unconfirmed | DENY | no | policy invalid, no execution | integration, chaos |
| CANDIDATE_POLICY_OVERRIDE | `UPLOAD_EXTERNAL` | confidential, unconfirmed | DENY | no | boundary locked | integration |
| PROMPT_INJECTION | arbitrary | confidential, unconfirmed | policy-derived | only if allowed | rendered as text | property, adversarial, E2E |
| REPLAYED_REQUEST | same request | unchanged | DENY on replay | no second call | replay denied | integration |
| OFFLINE_MODE | deterministic fake | scenario metadata | policy-derived | policy-derived | cached evidence label | integration, E2E |
| ATTESTATION_FAILURE | independent | attestation failed | no protected release | no protected capability | failed / not released | unit |

Invariant coverage is maintained in `docs/SECURITY_TESTING.md`; this matrix maps the
audience scenarios to their observable results.

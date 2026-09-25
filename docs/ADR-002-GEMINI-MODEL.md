# ADR-002: Use Gemini 3.5 Flash for the live proposer

- Status: Accepted; live project verification pending
- Date checked: 2026-09-25

## Decision

Use `gemini-3.5-flash` as the default live model, while retaining the `GEMINI_MODEL`
environment override. The model identifier remains in the composition layer and is
not coupled to policy, capability, or domain code.

## Rationale

Google's current model lifecycle page lists Gemini 3.5 Flash as a stable model
released on 2026-05-19 and available through at least 2027-05-19. The structured
output documentation includes it among supported models. It is the appropriate
latency and capability tier for a small typed proposal; this prototype does not need
a Pro model's higher cost or latency.

## Alternatives

| Model | Assessment |
|---|---|
| `gemini-2.5-flash` | Rejected as the default: retirement is scheduled for 2026-10-20. |
| `gemini-3.8-flash` | Rejected for the stage default: it is in the shorter-availability group, despite being newer and supporting structured output. |
| `gemini-3.5-flash-lite` | Viable lower-cost fallback, but 3.5 Flash provides more reasoning capacity for negligible demo volume. |
| Preview models | Rejected because a conference demo should prefer a stable endpoint. |

## Verification boundary

Documentation establishes lifecycle and feature support. Availability, latency,
authentication, and five-run behavior in the intended project remain unverified
until a project and Application Default Credentials are available.

## Sources

- <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions>
- <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output>
- <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/gcp-auth>

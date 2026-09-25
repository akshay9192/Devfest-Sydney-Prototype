# Repository instructions

Before making material code changes, read these files completely:

- `skills/karpathy-guidelines/SKILL.md`
- `skills/clean-code/SKILL.md`
- `docs/ARCHITECTURE.md`
- `docs/THREAT_MODEL.md`

Preserve the authority boundary: playbook text, user input, model output, and
candidate rules are untrusted. Only validated application state and authoritative
policy can authorize a capability. Every executable action must pass through the
policy engine and capability gate, and every uncertainty must fail closed.

Use synthetic data only. Do not add a real external upload implementation. Do not
claim Gemini inference occurs inside this project's confidential runtime.

For each material change, add or update a meaningful verification. Keep the offline
demo independent of network, cloud credentials, Gemini, and DNS.

# Security testing

The suite tests enforcement behavior, not just happy paths.

## Automated layers

- Unit tests cover strict proposal fields, exact enum values, policy loading,
  action/destination consistency, confirmation authority, hashes, receipt omission,
  protected-resource release, and capability allowlisting.
- Hypothesis generates arbitrary rationale and advisory text to ensure neither can
  change fixed authoritative outcomes.
- Integration tests run the safe, poisoned, confirmed, replayed, corrupted-policy,
  and candidate-override flows while counting executor calls.
- Adversarial tests exercise unknown actions, missing/extra fields, case and
  whitespace variations, YAML type confusion, oversized scenarios, fabricated
  confirmation, log injection, path-shaped input, and concurrent requests.
- Browser tests wait for network idle, operate the rendered controls, capture a
  poisoned-state screenshot and console errors, use the keyboard, and inject an XSS
  payload that must render as text.

## Commands

```text
make lint
make typecheck
make test
make test-security
make test-e2e
make verify
```

On Windows without Make, invoke the corresponding `.venv/Scripts/python.exe -m`
commands shown in the Makefile.

## Coverage meaning

The local gate measures `app/domain` and `app/services` and requires 90% overall.
Branch and invariant coverage matter more than the percentage. Live Gemini and live
GCP paths require credentials and are separately integration-tested at deployment;
their failure behavior is covered locally.

## Security tools

Ruff, mypy, Bandit, pip-audit, and a repository-aware secret-pattern check run
locally. Use gitleaks when installed for Git-history scanning. Trivy is reserved for
the built container because it is unavailable without Docker. Any high or critical
finding blocks release unless documented as a verified false positive.

## Current observed verification (2026-10-02)

`make release-check` passed: 84 non-E2E tests, 2 E2E tests, 18 security tests
(a subset of the 84), 97.99% core coverage, and 20/20 reliability cycles. Ruff,
mypy, Bandit, pip-audit, and the repository secret scan passed. Git-history
gitleaks found no leaks. Trivy HIGH/CRITICAL scans are recorded in
`CLOUD_VERIFICATION_REPORT.md`. Rehearsal tests reject unexpected image/project/hash
evidence and verify cleanup when log retrieval fails. Local tests do not establish
cloud IAM denial: the separately observed STS rejection is identified precisely
in the cloud report.

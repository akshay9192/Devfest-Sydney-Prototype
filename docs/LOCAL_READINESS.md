# Local readiness

`LOCAL READINESS: NOT YET VERIFIED`

The cloud phase remains locked until every item below has current evidence.

| Requirement | Status | Evidence |
|---|---|---|
| Application and frontend boot | PASS | Playwright starts Uvicorn and loads after network idle |
| Live Gemini | BLOCKED | no project, location, API key, ADC, or `gcloud` available |
| Offline, safe, poison, allow, deny, reset | PASS | integration and browser suites |
| Authority and fail-closed invariants | PASS | unit, property, adversarial, and chaos tests |
| Receipts and log safety | PASS | receipt and structured-log regression tests |
| Browser, keyboard, responsive, console | PASS | 1440×900, 1920×1080, 390×844; zero console errors |
| Network-independent offline mode | PASS | no model/cloud client; socket-denial integration test |
| Docker build and run | PASS IN CI; unavailable locally | GitHub Actions built, ran, health-checked, and browser-tested commit `61ab1e2` |
| Demo under 70 seconds | PASS | 65-second runbook; controller loop under 20 ms |
| Clean README setup | PASS | fresh virtualenv install passed; current suite has 69 non-E2E and 2 E2E tests |
| Twenty-cycle offline reliability | PASS | 20/20 complete reset/safe/poison/reset cycles |
| Security scans | PASS | Bandit, pip-audit, and repository secret scan passed locally; CI gitleaks and strict Trivy HIGH/CRITICAL gates passed |

This document must never say PASS based on planned, mocked, cached, or unavailable
checks.

CI evidence: <https://github.com/akshay9192/Devfest-Sydney-Prototype/actions/runs/36098319568>.
Overall local readiness remains unverified because a billed project and Application
Default Credentials are still unavailable for the required live Gemini exercise.

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
| Docker build and run | blocked | Docker executable unavailable |
| Demo under 70 seconds | PASS | 65-second runbook; controller loop under 20 ms |
| Clean README setup | PASS | fresh virtualenv install and all 68 tests passed |
| Twenty-cycle offline reliability | PASS | 20/20 complete reset/safe/poison/reset cycles |
| Security scans | PARTIAL | Bandit, pip-audit, secret scan pass; Trivy/gitleaks unavailable |

This document must never say PASS based on planned, mocked, cached, or unavailable
checks.

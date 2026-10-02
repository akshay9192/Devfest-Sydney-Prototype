# Local readiness

`LOCAL READINESS: PASS`

Current local and live integration checks passed on 2026-10-02. See the detailed
cloud report for the separate live resource-release evidence and limitations.

| Requirement | Status | Evidence |
|---|---|---|
| Application and frontend boot | PASS | Playwright starts Uvicorn and loads after network idle |
| Live Gemini | PASS | one real safe `gemini-3.5-flash` smoke: `SUMMARIZE_LOCALLY`, `ALLOW` |
| Offline, safe, poison, allow, deny, reset | PASS | integration and browser suites |
| Authority and fail-closed invariants | PASS | unit, property, adversarial, and chaos tests |
| Receipts and log safety | PASS | receipt and structured-log regression tests |
| Browser, keyboard, responsive, console | PASS | 1440×900, 1920×1080, 390×844; zero console errors |
| Network-independent offline mode | PASS | no model/cloud client; socket-denial integration test |
| Docker build and run | PASS | local release build; deployed digest command override fails closed locally; container/browser smoke |
| Demo under 70 seconds | PASS | 65-second runbook; controller loop under 20 ms |
| Clean README setup | PASS | fresh virtualenv install passed; current suite has 84 non-E2E and 2 E2E tests |
| Twenty-cycle offline reliability | PASS | 20/20 complete reset/safe/poison/reset cycles |
| Security scans | PASS | Bandit, pip-audit, and repository secret scan passed locally; CI gitleaks and strict Trivy HIGH/CRITICAL gates passed |

This document must never say PASS based on planned, mocked, cached, or unavailable
checks.

CI evidence: <https://github.com/akshay9192/Devfest-Sydney-Prototype/actions/runs/36098319568>.
Current `make release-check` passed with 97.99% core coverage. The prior CI link
is historical; current commit CI is inspected separately after publication.

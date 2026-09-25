# Phase two progress checkpoint

Last updated: 2026-09-25 (Australia/Sydney)

## Objective

Phase two must verify two independent boundaries:

1. untrusted playbook/model output cannot authorize a prohibited action; and
2. one synthetic protected resource is released only to the expected attested
   Confidential Space workload.

The first boundary remains verified locally. The second boundary has not yet been
tested in Google Cloud and must not be represented as verified.

## Repository state

- Base checkpoint: `70f47a70f80387696c83fa14561c8f30bc943cc2`
- Last implementation/evidence commit before this handoff: `0e6a9a77c26e8a98164dd19c190c64db5e2aa543`
- Branch: `main`
- Remote: `https://github.com/akshay9192/Devfest-Sydney-Prototype.git`
- Local and remote `main` matched at the last check.
- The working tree was clean, and reproducible local caches, test screenshots,
  coverage data, and virtual environments were removed.

## Completed work

### Independent release verification

GitHub Actions workflow:

<https://github.com/akshay9192/Devfest-Sydney-Prototype/actions/runs/36098793805>

Result: **PASS**

The workflow verified:

- Ruff formatting and lint;
- strict mypy;
- 69 non-E2E tests;
- 18 adversarial/security tests;
- 2 Playwright E2E tests;
- 97.99% core coverage;
- 20/20 offline reliability cycles;
- Bandit;
- pip-audit;
- repository secret scanning;
- full-history gitleaks scanning;
- production container build and startup;
- container health and rendered-browser smoke testing; and
- a strict Trivy HIGH/CRITICAL gate.

### Container

- Runtime: official Python `3.12.14-alpine3.23` image.
- Manifest digest:
  `sha256:d339953547bb5bc57eb5c1ff3224c40890ce56e494b13a52a574658e5a0f888a`
- Runs as a non-root user.
- CI build, run, health check, and browser smoke: **PASS**.
- Trivy HIGH/CRITICAL findings: **zero**.
- Docker remains unavailable on the local Windows host; this is CI evidence and
  must not be described as a local Docker pass.

Two Debian bases were rejected after Trivy found ten unfixed HIGH findings. No
finding was suppressed. The root cause and regression are recorded in
`docs/REGRESSION_LOG.md` as REG-006.

### Gemini preparation

- Default model: `gemini-3.5-flash`.
- Model remains configurable through `GEMINI_MODEL`.
- SDK client uses `enterprise=True`, Application Default Credentials, the stable
  `v1` API, a 15-second timeout, and Pydantic structured output.
- Lifecycle and structured-output research is recorded in
  `docs/ADR-002-GEMINI-MODEL.md` and `docs/CLOUD_VERIFICATION_SOURCES.md`.
- Live project availability, authentication, latency, and five-run behavior remain
  **unverified**.

### Confidential Space preparation

- `app.cloud_verify` is packaged in the production container as a one-shot,
  fail-closed verifier.
- The verifier obtains the launcher attestation token, exchanges it through WIF,
  attempts Secret Manager access, checks the expected SHA-256, and emits only safe
  metadata.
- It exits unsuccessfully unless protected-resource release is live and verified.
- The protected resource value is never logged, returned in receipts, rendered, or
  sent to Gemini.
- The deployment design binds WIF to Confidential Space, `STABLE`, debug disabled,
  the operator project, the attached workload service account, the verifier command,
  and the immutable container digest.
- The attached VM service account must never receive Secret Manager accessor.
- Prepared instructions are in `docs/GCP_DEPLOYMENT.md`; cleanup instructions are in
  `docs/GCP_CLEANUP.md`.

## Tooling state

- Python: 3.12.6
- Git: 2.47.0.windows.2
- GitHub CLI: 2.97.0, authenticated as `akshay9192`
- Docker: unavailable locally
- Google Cloud CLI: unavailable
- Trivy: unavailable locally; verified in CI
- gitleaks: unavailable locally; verified in CI
- GNU Make and Bash: unavailable locally
- No Google/GCP/Vertex environment configuration or Application Default
  Credentials were found.

## External blocker

Cloud work cannot start safely until the user supplies the intended billed GCP
project and an authenticated execution environment.

Required input:

1. the exact billed GCP project ID; and
2. either an official `gcloud` installation with user authentication and ADC on
   this host, or an authenticated Google Cloud Shell workspace for that project.

Do not silently choose a project. Do not create downloadable service-account keys.

## Resume sequence

1. Read `AGENTS.md`, the repository-local skills, and this checkpoint.
2. Confirm `git status`, `git log`, local `HEAD`, remote `main`, and GitHub auth.
3. Confirm the intended project using `gcloud auth list` and
   `gcloud config get-value project`.
4. Query supported Confidential Space N2D/SEV zones and quota in that project;
   select the lowest-cost supported region/zone deliberately.
5. Enable only the documented APIs and enumerate every role before granting it.
6. Run at least five live `APP_MODE=live` Gemini scenarios and record latency,
   proposal, policy decision, and executor count. Invariant violations must be zero.
7. Build the already-verified container, push it to Artifact Registry, and resolve
   its immutable `sha256:` digest.
8. Create exactly one synthetic Secret Manager resource and record only its hash.
9. Create the claim-constrained WIF pool/provider and resource-level IAM binding.
10. Prove local/non-attested access is denied.
11. Prove the VM-attached service account has no direct secret access.
12. Prove a wrong workload digest is denied where feasible.
13. Prove the exact expected Confidential Space workload is allowed.
14. Audit IAM, logs, receipts, and Gemini inputs for secret exposure.
15. Produce `artifacts/cloud-verification.json`,
    `docs/CLOUD_VERIFICATION_REPORT.md`, and curated ALLOWED/DENIED evidence only
    after observing real results.
16. Re-run the entire release workflow, rehearse all fallback modes, document cost
    and cleanup, stop/delete unneeded compute, then push final evidence.

## Claim boundary at this checkpoint

Defensible now:

- The playbook and Gemini proposal have no direct authorization authority.
- Fixed authoritative inputs and policy version produce deterministic
  authorization.
- Denied actions cannot reach the configured executor through the application
  capability path.
- The offline fallback, production container, and independent CI release gates pass.

Not yet defensible:

- Live Gemini works in the intended GCP project.
- A Confidential Space workload has been deployed.
- Real attestation-gated resource release works.
- Unauthorized cloud access has been observed failing.
- The cloud prototype is fully verified.

Current status: **DEVFEST PROTOTYPE: NOT YET FULLY VERIFIED**

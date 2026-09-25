# Regression log

## REG-001

**Symptom:** Policy evaluation used the sensitivity claimed by the model proposal.

**Root cause:** Confirmation logic read `proposal.sensitivity` even though document
sensitivity is authoritative application metadata.

**Why existing tests missed it:** Tests varied reasons and confirmation claims but
kept model and application sensitivity identical.

**Regression test:**
`test_model_cannot_downgrade_authoritative_confidential_sensitivity` supplies a
model claim of `PUBLIC` with an authoritative `CONFIDENTIAL` context.

**Fix:** `PolicyEngine.evaluate` now requires an immutable `AuthoritativeContext`.
The engine uses that context for sensitivity and confirmation.

**Verification:** PASS

**Commit:** `4317fd1`

## REG-004

**Symptom:** The deployment guide claimed the attestation verifier could run inside
the workload container, but the runtime image did not contain that script and its
default command only started the web server.

**Root cause:** Local and cloud packaging paths had not been traced together. The
verification helper lived outside the packaged `app` module.

**Why existing tests missed it:** Local tests imported the source-tree script and no
container-capable environment was available on the workstation.

**Regression test:** CI now builds and runs the production image, exercises the UI
through that container, and the packaged `app.cloud_verify` command fails closed
without attestation configuration. Unit coverage also proves a released value with
the wrong hash cannot produce verified evidence.

**Fix:** Package the one-shot verifier under `app`, constrain its Confidential Space
command/environment overrides with image launch-policy labels, and bind the WIF
condition to that exact command override.

**Verification:** PASS. GitHub Actions built and ran the production image, completed
browser smoke testing against it, and passed the container vulnerability gate.

**Commit:** `5935800`

## REG-005

**Symptom:** The first GitHub Actions run failed Ruff import formatting for the thin
source-tree attestation wrapper.

**Root cause:** The wrapper was simplified after the last local lint invocation, so
the committed form had one extra blank line between its import and module guard.

**Why existing tests missed it:** Runtime tests imported the wrapper successfully;
this was a style-gate defect, not a behavior failure.

**Regression test:** The corrected file passes Ruff, and CI remains the independent
release gate. CI also now runs `bash -n` against the deployment script.

**Fix:** Apply Ruff's import formatting and rerun the full local checks.

**Verification:** PASS. Local checks and the replacement GitHub Actions run passed.

**Commit:** `5b66fac`

## REG-006

**Symptom:** Trivy rejected both Debian 12 and Debian 13 Python runtime images for
ten HIGH vulnerabilities in base operating-system packages.

**Root cause:** The Debian images contained affected util-linux, ACL, and gzip
packages. Debian had published no fixed package versions when checked, so upgrading
from bookworm to trixie changed versions without removing the findings.

**Why existing tests missed it:** Docker and Trivy were unavailable on the local
host. The first independent CI container scan exposed the base-image findings.

**Regression test:** CI scans the built runtime image for all HIGH and CRITICAL
findings, including vulnerabilities with no published fix, and fails through
`scripts/check_trivy_report.py` when any are present.

**Fix:** Use the current official Python 3.12 Alpine 3.23 image pinned by immutable
manifest digest. No vulnerability was suppressed or ignored.

**Verification:** PASS. CI built and ran the image, exercised the rendered UI, and
reported zero HIGH/CRITICAL findings.

**Commit:** `61ab1e2`

## REG-003

**Symptom:** A fresh virtual environment could install successfully, but pytest
could not enumerate the machine-level temporary directory under a different
execution context.

**Root cause:** The test configuration relied on pytest's implicit per-user temp and
cache directories.

**Why existing tests missed it:** The warmed environment already owned those paths.

**Regression test:** The complete suite is rerun from `.clean-venv` using the
repository configuration.

**Fix:** Pytest now uses ignored, workspace-owned temp and cache directories.

**Verification:** PASS — 68 tests, Ruff, and strict mypy passed from the fresh
environment.

**Commit:** `4317fd1`

## REG-002

**Symptom:** Reset restored the playbook but retained executor count, simulated sink
state, and modified candidate rules.

**Root cause:** Reset only rewrote `PLAYBOOK.md` and replay IDs.

**Why existing tests missed it:** The API test asserted only the poison flag.

**Regression test:** `test_reset_restores_all_mutable_demo_state` mutates each state,
resets, and reuses a previous request ID.

**Fix:** Reset now clears executor state and rewrites candidate rules to their known
empty candidate state under the same lock.

**Verification:** PASS

**Commit:** `4317fd1`

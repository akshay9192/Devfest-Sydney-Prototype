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

**Verification:** Local code/security tests PASS; container CI pending.

**Commit:** this cloud-readiness change

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

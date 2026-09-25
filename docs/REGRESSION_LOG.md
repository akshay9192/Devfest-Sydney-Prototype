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

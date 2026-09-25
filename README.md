# Your AI Assistant Shouldn't Trust You

## What this demonstrates

This DevFest Sydney prototype puts deterministic authority around a probabilistic
assistant. A playbook can influence Gemini's typed proposal; Python evaluates
authoritative policy; a capability gate controls the only executors. Poisoning the
playbook can change the proposal without granting the proposed action.

> We don't need deterministic intelligence. We need deterministic boundaries around
> probabilistic intelligence.

## What this does NOT demonstrate

It does not make Gemini deterministic, treat Markdown as policy, prove that a model
recommendation is correct, reproduce a person's brain, or claim a new research
architecture. The upload executor is simulated and every document/value is
synthetic.

The local app does not provide live attestation. Its offline status is explicitly
`CACHED ATTESTATION EXAMPLE`. Cloud status remains unverified until the checks in
[`docs/GCP_DEPLOYMENT.md`](docs/GCP_DEPLOYMENT.md) are observed.

## Architecture

```text
request + PLAYBOOK.md (untrusted guidance)
                  |
                  v
       Gemini / deterministic fake
             typed proposal
                  |
                  v
       Python PolicyEngine  <--- authoritative YAML + app confirmation state
                  |
          ALLOW --+-- DENY ------> receipt; executor not called
            |
            v
       CapabilityGate
            |
   fixed simulated executor
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for component and data-flow
details.

## Trust boundaries

User input, browser content, `PLAYBOOK.md`, Gemini output, candidate rules, and
cached evidence are untrusted. The small policy/controller core, fixed executor map,
and authoritative application confirmation state are trusted locally. The detailed
assets, assumptions, TCB, and residual risks are in
[`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Why PLAYBOOK.md is advisory

The proposer reads `app/config/PLAYBOOK.md`; the policy engine never does. The poison
control changes only that file. It cannot edit system policy, create a capability,
or assert authoritative confirmation.

## Why policy.yaml is authoritative

`SYSTEM_POLICY.yaml` is loaded through a strict, narrow schema and evaluated before
the capability gate. `VALIDATED_USER_POLICY.yaml` can narrow behavior. The candidate
file is never loaded by enforcement. A missing, malformed, or ambiguous policy
fails closed.

## Gemini integration

`RealGeminiProposer` uses Google's current `google-genai` Python SDK with a Pydantic
response schema and validates the parsed value again. Gemini receives a synthetic
scenario and advisory playbook, with no tools, credentials, direct filesystem, or
policy mutation access. Calls use the stable `v1` API and a configurable 15-second
timeout (`GEMINI_TIMEOUT_MS`). If a live call fails, the interface explicitly says
that it is using a recorded proposal; the real controller and capability gate still
run. The model ID is configurable with `GEMINI_MODEL`; the
default is `gemini-2.5-flash`, which official lifecycle notes schedule for retirement
on 2026-10-16, so select a currently supported model before deployment.

## Confidential Computing

The selected cloud runtime is Confidential Space: a container on a hardened image
and Confidential VM. The intended protected resource is one non-sensitive Secret
Manager version. An accepted launcher token is exchanged through Workload Identity
Federation, whose provider checks Confidential Space and stable-image claims and
maps the application image digest.

Vertex AI is a remote service. Calling it from Confidential Space does not mean the
Gemini inference executes inside this project's TEE. The design protects
controller-held policy/state and minimizes synthetic context sent to the model.

## Attestation

The app reports `VERIFIED` only when the Confidential Space provider exchanges the
launcher token, receives IAM authorization for the protected secret, and matches the
released synthetic value's expected SHA-256. A decoded token alone is insufficient.
Attestation establishes checked workload/environment identity properties; it does
not establish semantic correctness or freedom from application bugs.

## Local quickstart

Python 3.12 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade "pip>=26.2.1"
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts\run_demo.py --mode offline_demo
```

Open `http://127.0.0.1:8000`.

## Offline demo

`make demo-offline` starts the same UI with deterministic fake proposals and cached
example evidence. The policy engine, gate, executors, and receipts are real. This
mode constructs no Gemini or cloud client and requires no Wi-Fi, DNS, credentials,
or GCP access.

## GCP deployment

Read the decision in
[`docs/ADR-001-CONFIDENTIAL-RUNTIME.md`](docs/ADR-001-CONFIDENTIAL-RUNTIME.md) and
follow [`docs/GCP_DEPLOYMENT.md`](docs/GCP_DEPLOYMENT.md). The deployment script
refuses an unexpected active project and requires a digest-pinned image.

## Testing

```text
make lint
make typecheck
make test
make test-e2e
make verify
make release-check
```

The suite includes unit, integration, Hypothesis property, adversarial, concurrency,
and rendered Playwright tests. Core domain/service coverage must be at least 90%.
`make release-check` is the definitive local gate and adds ten-cycle reliability
and a Docker build. `make cloud-verify` is separate because it requires deployed
infrastructure.

## Security tests

`make test-security` runs adversarial tests, Bandit, pip-audit, and the local secret
pattern scanner. `make docker-scan` uses Trivy when Docker and Trivy are installed.
See [`docs/SECURITY_TESTING.md`](docs/SECURITY_TESTING.md) and
[`docs/RED_TEAM_REPORT.md`](docs/RED_TEAM_REPORT.md).

## Prior art / inspiration

Runtime enforcement around agents is established by AgentSpec, reference-monitor
work, formal policy systems, tool firewalls, and constrained capability designs.
Confidential Space establishes the attested resource-release pattern. This prototype
is a small engineering synthesis for teaching, not a research novelty claim. The
focused comparison is in [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md).

## EvoHunt attribution

EvoHunt inspired the distinction that useful procedural knowledge can be
externalized as an inspectable, versioned playbook. This prototype is not EvoHunt
and does not claim it lacks candidate tournaments, replay, revision gates, held-out
evaluation, transfer adapters, or anti-regression checks. Our focus is playbook
guidance versus machine-enforced runtime authority.

## Limitations

- Local receipts are unsigned and explicitly labeled as demo artifacts.
- State and replay tracking are process-local; a multi-worker production service
  would need shared coordination.
- The fake proposer changes on a known marker for a repeatable stage demonstration.
- The simulated external sink performs no network upload.
- Live Gemini behavior depends on project model availability and credentials.
- Confidential Space deployment and resource release require a configured GCP
  project and have not been verified from this checkout.
- TEE and platform side channels remain outside this prototype.

## DevFest demo

The exact sequence is in [`docs/DEMO_RUNBOOK.md`](docs/DEMO_RUNBOOK.md); the spoken
script is in [`docs/DEVFEST_SCRIPT.md`](docs/DEVFEST_SCRIPT.md). The interactive
portion is designed for about 65 seconds and the full script for under three
minutes.

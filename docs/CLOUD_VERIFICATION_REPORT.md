# Cloud verification report — 2026-10-02

## LIVE VERIFIED CLOUD RESULT

PASS. At `2026-10-02T04:57:10.448813439Z`, Cloud Logging recorded `VERIFIED`,
`live=true`, protected resource `released`, and the exact expected SHA-256.
The launcher subsequently reported `workload task ended and returned 0`.
This is captured historical live evidence; it is not a current live attestation
and does not change the offline fixture's `CACHED ATTESTATION EXAMPLE` label.

| Property | Observed value |
|---|---|
| Product | Google Cloud Confidential Space on Confidential VM infrastructure |
| Runtime | production `confidential-space-260800`, hardened launcher/container |
| TEE / CPU | AMD SEV / AMD Milan |
| Machine | N2D, `n2d-highcpu-2`, 2 vCPUs, 2 GiB |
| Location | `australia-southeast1`, `australia-southeast1-b` |
| Project | `newproject-490108` / `131985117376` |
| VM ID | `6992249053452076981` |
| Secure Boot / vTPM | both enabled |
| Image | `australia-southeast1-docker.pkg.dev/newproject-490108/devfest/controller@sha256:4209cd130c3384b3f18a621691ae97934140065b29e4c523c69cf96fa8ed5431` |
| Workload account | `devfest-confidential-workload@newproject-490108.iam.gserviceaccount.com` |
| WIF | `devfest-attested` / `attestation-verifier`, ACTIVE |
| Protected version | `projects/131985117376/secrets/devfest-protected-state/versions/1` |
| Resource SHA-256 | `4350401800f70db43df2e151b98fbdcd2f2f2a43a91e19ce26368f93b72b5a96` |

Safe evidence is saved in [cloud_release_evidence.json](cloud_release_evidence.json).
The Google Cloud log is `projects/newproject-490108/logs/confidential-space-launcher`.

## Attestation and identity

SEV supplies hardware memory encryption. This run used Google's managed vTPM PCR
boot/launcher evidence, as observed in `Using TPM PCR as attestation root.` It did
not use an AMD SEV-SNP hardware report or Intel TDX quote. Google Cloud Attestation
issued launcher OIDC evidence; STS/WIF accepted it and Secret Manager released the
synthetic bytes. Only successful resource release and matching SHA produce VERIFIED.
Local token decoding supplies display fields after that release; it is not the
signature verification or authorization mechanism.

Issuer: `https://confidentialcomputing.googleapis.com`.
Allowed audience: `https://sts.googleapis.com`.
Mapping: `attribute.image_digest=assertion.submods.container.image_digest`;
`google.subject` concatenates digest, project number, and instance ID.
Current official [claim documentation](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/reference/token-claims)
and [direct-resource pattern](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources)
were reviewed before launch. Exact provider condition inspected:

```text
assertion.swname == 'CONFIDENTIAL_SPACE' && assertion.dbgstat == 'disabled-since-boot' && 'STABLE' in assertion.submods.confidential_space.support_attributes && assertion.secboot == true && assertion.hwmodel in ['GCP_AMD_SEV', 'GCP_AMD_SEV_ES'] && assertion.submods.gce.project_number == '131985117376' && 'devfest-confidential-workload@newproject-490108.iam.gserviceaccount.com' in assertion.google_service_accounts && assertion.submods.container.cmd_override == ['-m', 'app.cloud_verify']
```

Secret IAM now has only `roles/secretmanager.secretAccessor` for the federated
principalSet mapped to `sha256:4209cd130c3384b3f18a621691ae97934140065b29e4c523c69cf96fa8ed5431`. The obsolete failed image grant was removed
after the replacement succeeded. Neither token validation nor digest binding was
weakened. The dedicated VM account has only registry reader, workloadUser, and
logWriter project roles; no direct secret accessor, Owner, or Editor. The project
has no parent; existing Owner for the user and Editor for the default Compute
account were observed and left unchanged. The default account was not attached.

## Reconstruction and changes

Local/remote starting HEAD: `74abc3fb4915640b84f81624bc02263a644df7f9`, branch main.
The interrupted run left legitimate Docker entrypoint, deployment, CI, test, and
product-documentation changes. Earlier cloud logs showed the original image could
not run the override because its entrypoint was empty. The existing replacement
image already had `ENTRYPOINT ["python"]`; its override is `["-m","app.cloud_verify"]`.
It was reused, with no new cloud build or publication in this continuation.
Application source remained unchanged. Local release builds are separate artifacts
and are not automatically authorized by cloud IAM.

Billing was enabled. No VM/disk existed at reconstruction. Required APIs, one
Artifact Registry repository, two immutable image versions, enabled synthetic
secret version, workload account, and ACTIVE pool/provider were independently
inspected. Authentication required selecting the existing account and using network
access outside the sandbox. No credentials were printed or added to the repository.
The ingress-deny firewall existed already, priority 100, all IPv4 protocols, scoped
to the dedicated service account; no public application service was added.

## Negative verification

- Local execution of the exact deployed digest exited 1 with `FAILED`, `live=false`,
  and `protected_resource=not released`. No cached result became VERIFIED.
- One real STS request with synthetic invalid unattested evidence returned HTTP 400
  `invalid_grant` and issued no credential. This proves the unattested rejection
  path; it is not a test of a valid Google-signed token for another image digest.
- Secret/project IAM inspection found no direct workload-account secret-access grant.
  Policy Troubleshooter returned UNKNOWN_INFO because federated principal sets are
  unsupported. An attempted actual account request failed at impersonation
  (`iam.serviceAccounts.getAccessToken` denied), before Secret Manager. No roles
  were added to overcome that; do not claim an observed direct Secret Manager 403.
- A valid alternate-digest VM was not launched. Digest restriction was inspected
  in actual secret IAM; the synthetic STS rejection is the cheap negative test.
- Deterministic adversarial integration/browser tests denied external proposals;
  the forbidden executor was never invoked. The executor is synthetic only.

## Gemini and stage reliability

One safe live `gemini-3.5-flash` repository call in this continuation proposed
`SUMMARIZE_LOCALLY`, and the real PolicyEngine returned ALLOW. No fallback was used.
No additional live poison attempts were made. The user's prior five poisoned live
trials all remained local summaries: unsafe live proposal NOT TRIGGERED.

OFFLINE DEMO EVIDENCE uses a deterministic fake proposal with real strict schema,
policy, capability gate, executor boundary, and receipt. It requires no Gemini,
GCP credentials, DNS, or venue network. Cached attestation stays explicitly labeled.
Gemini is a remote service outside this project's TEE. Policy authorizes actions;
attestation authorizes protected-state release. Neither proves model correctness.

## Verification and rerun

`make release-check`: PASS; 84 non-E2E tests, 2 browser tests, 18 security tests
(a subset), core coverage 97.99%, twenty-cycle offline reliability 20/20.
Ruff, formatting, mypy, Bandit, pip-audit, and repository secret scan passed.
Trivy HIGH/CRITICAL scans passed, including the exact deployed image. Git-history
gitleaks scanned 17 starting commits with no leaks. After publication, two
`generic-api-key` findings were confirmed to be the public expected resource SHA-256
in export commands. `.gitleaks.toml` allows only that exact hash; all default rules
remain enabled. The 18-commit history then passed, while an unrelated synthetic
credential-pattern fixture was still detected. CI explicitly loads this config. Deprecation warnings from
Starlette TestClient and google-auth remain; credential configuration is constructed
by application code rather than accepted from model output.

Rehearsal preflight passed against live persistent resources. Tests reject wrong
project/image/hash evidence and verify cleanup on polling errors. The launch and
cleanup commands were exercised live; wrapper lifecycle was tested offline to avoid
an unnecessary second VM. Run:

```bash
gcloud config set project newproject-490108
source deploy/rehearsal.env.sh
make PYTHON=.venv/bin/python cloud-rehearsal
```

The wrapper refuses unexpected persistent IAM/WIF configuration, waits up to ten
minutes for live release evidence, and deletes its VM in a cleanup handler. A
30-minute automatic DELETE limit provides a backstop. If CLI cleanup fails:

```bash
gcloud compute instances delete devfest-verifiable-ai --zone=australia-southeast1-b --project=newproject-490108 --quiet
gcloud compute instances list --project=newproject-490108
gcloud compute disks list --project=newproject-490108
```

## Cleanup and estimated cost

This continuation created one n2d-highcpu-2 VM at approximately 04:55:55 UTC.
Verification completed at 04:57:10; deletion completed at 04:59:13 UTC. Resource
lifetime was about 3m18s; both final VM and disk inventories were empty. The launcher
also scheduled normal shutdown after successful one-shot completion.

Today's audit records additionally show one earlier n2d-highcpu-2 attempt from
approximately 03:57:40 to 04:16:42 UTC. Combined observed VM resource lifetime is
about 23 minutes. One successful Cloud Build is recorded today (02:47–02:48 UTC);
this continuation submitted zero. Two approximately 40.8-MB image versions existed
already and were preserved. There were no new registry repositories/images here.
One Gemini call was made here; the user reports six earlier calls (safe plus five
poisoned). Earlier call costs cannot be independently totaled from these logs.
Policy Troubleshooter API was enabled for inspection; no new paid infrastructure
was created for it.

Estimated additional spend for the observed activity today: conservatively under
USD $2, not a settled billing total. Before launch, official [SEV pricing](https://cloud.google.com/confidential-computing/confidential-vm/pricing)
showed $0.005479/vCPU-hour plus $0.0007342/GiB-hour: about $0.0124264/hour for this
machine's confidential surcharge. Exact Sydney base compute pricing was not
resolved; a conservative $1/hour allowance for small compute, disk and IP comfortably
bounds the roughly 23 observed VM minutes. The estimate also allows for the short
build, limited synthetic model calls, small registry storage, secret/API calls and
logs. Credit balance and a complete settled daily billing export were unavailable;
this estimate covers observed project activity, not unknown usage outside it.

Persistent rehearsal resources kept: devfest registry and image versions; final
pinned image; synthetic secret/version; WIF pool/provider; dedicated workload
account; final digest IAM; existing account-scoped firewall; safe Cloud logs and
rerun scripts. No billable VM or boot disk remains.

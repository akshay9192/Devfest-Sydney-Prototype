# GCP deployment

## Current status

LIVE VERIFIED CLOUD RESULT: PASS on 2026-10-02 at 04:57:10 UTC.
Production Confidential Space released the synthetic resource through digest-bound
WIF/STS, and its SHA-256 matched. The disposable VM and disk were deleted.
See [the observation report](CLOUD_VERIFICATION_REPORT.md) for exact evidence,
negative-test limits, tests, cleanup, and estimated cost.

## Rehearsal command

```bash
gcloud config set project newproject-490108
source deploy/rehearsal.env.sh
make PYTHON=.venv/bin/python cloud-rehearsal
```

This checks persistent resources and exact IAM/WIF configuration, launches one
small verifier, waits up to ten minutes for safe live release evidence, and deletes
the VM in a cleanup handler. The VM also has a 30-minute automatic deletion limit.
If cleanup fails, use `docs/GCP_CLEANUP.md`; always inspect VM/disk inventory.
The current deployment and cleanup were exercised; the wrapper's live preflight
and offline cleanup/error tests passed. No second VM was needed for wrapper testing.

## Chosen design

Use a CPU-only Confidential Space production image on an SEV-backed
`n2d-highcpu-2` where that machine and Confidential Space are supported. Pin the
application image by digest. Google Cloud Attestation supplies the launcher token;
a Workload Identity Pool provider checks the stable Confidential Space attribute
and maps the image digest. Secret Manager releases one synthetic value to the
matching federated principal.

This is option A in the user brief: Confidential Space is the hardened container environment and its
underlying VM uses Google Cloud Confidential VM technology. The launcher supplies
`/run/container_launcher/attestation_verifier_claims_token`; a plain VM does not.
SEV provides hardware memory encryption with Google-managed vTPM boot attestation,
not an SEV-SNP hardware report. Current official guidance was checked 2026-10-02
in [the source record](CLOUD_VERIFICATION_SOURCES.md).

## Reuse existing rehearsal resources

Do not run the creation examples below against already-correct resources.
Do not rebuild the container for deployment/documentation-only changes.

```bash
export GCP_PROJECT=newproject-490108
export GCP_REGION=australia-southeast1
export WORKLOAD_SERVICE_ACCOUNT=devfest-confidential-workload@newproject-490108.iam.gserviceaccount.com
export IMAGE_URI=australia-southeast1-docker.pkg.dev/newproject-490108/devfest/controller@sha256:4209cd130c3384b3f18a621691ae97934140065b29e4c523c69cf96fa8ed5431
export WIF_AUDIENCE=//iam.googleapis.com/projects/131985117376/locations/global/workloadIdentityPools/devfest-attested/providers/attestation-verifier
export PROTECTED_SECRET_RESOURCE=projects/131985117376/secrets/devfest-protected-state/versions/1
export PROTECTED_SECRET_EXPECTED_SHA256=4350401800f70db43df2e151b98fbdcd2f2f2a43a91e19ce26368f93b72b5a96
```

After authentication, inspect instance/disk inventory, the existing image, secret
IAM, pool/provider, project IAM, firewall rules, and quota. Choose `GCP_ZONE` only
after checking an available AMD Milan N2D/SEV zone and regional attestation support:

```bash
gcloud compute zones list --project="$GCP_PROJECT"
gcloud compute zones describe "$GCP_ZONE" --project="$GCP_PROJECT" \
  --format='value(availableCpuPlatforms)'
gcloud compute machine-types describe n2d-highcpu-2 \
  --zone="$GCP_ZONE" --project="$GCP_PROJECT"
gcloud compute regions describe "$GCP_REGION" --project="$GCP_PROJECT"
gcloud compute firewall-rules list --project="$GCP_PROJECT"
```

Before launch, show the machine and cost estimate. `n2d-highcpu-2` is a small
documented 2-vCPU/2-GiB configuration; it was confirmed available with AMD Milan in Sydney. Plan one CPU-only VM for at most 30 minutes,
then delete immediately after evidence. Include compute, confidential premium,
boot disk, outbound traffic, external IP, and API/storage/log costs. Today's
incremental limit is $75, preferred below $40–$50. Billing is enabled; the exact
credit balance and settled usage were not available. Do not launch if the sequence could exceed that limit.

## Prerequisites and project guard

Install the current Google Cloud CLI, then run:

```bash
gcloud auth list
gcloud config get-value project
gcloud config get-value compute/region
gcloud config get-value compute/zone
```

Set `GCP_PROJECT`, `GCP_REGION`, and `GCP_ZONE` only after confirming those outputs.
The deployment script refuses to proceed when `GCP_PROJECT` differs from the active
project.

Enable only the required APIs:

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com \
  confidentialcomputing.googleapis.com \
  iamcredentials.googleapis.com \
  secretmanager.googleapis.com \
  sts.googleapis.com
```

Create a dedicated workload service account. Grant it
`roles/confidentialcomputing.workloadUser` and repository read access. Grant log
writer only when Cloud Logging is enabled. Do not grant Owner or Editor.

## Build and pin the image

Create an Artifact Registry Docker repository, submit the build, and resolve the
immutable digest:

```bash
gcloud artifacts repositories create devfest \
  --repository-format=docker --location="$GCP_REGION"

gcloud builds submit \
  --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/devfest/controller:devfest"

gcloud artifacts docker images describe \
  "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/devfest/controller:devfest" \
  --format='value(image_summary.digest)'
```

Set `IMAGE_URI` to the repository path plus the returned `@sha256:...` digest.

## Protected synthetic resource

Create a value such as `DEVFEST_SYNTHETIC_RELEASE_OK`; never use real sensitive
data. Record its SHA-256 locally as `PROTECTED_SECRET_EXPECTED_SHA256` and create one
Secret Manager version. The app compares the released bytes to this hash and never
returns or logs the value.

Create a Workload Identity Pool and OIDC provider using the official direct-resource
pattern:

```bash
gcloud iam workload-identity-pools create devfest-attested --location=global

gcloud iam workload-identity-pools providers create-oidc attestation-verifier \
  --location=global \
  --workload-identity-pool=devfest-attested \
  --issuer-uri="https://confidentialcomputing.googleapis.com" \
  --allowed-audiences="https://sts.googleapis.com" \
  --attribute-mapping='google.subject="gcpcs::"+assertion.submods.container.image_digest+"::"+assertion.submods.gce.project_number+"::"+assertion.submods.gce.instance_id,attribute.image_digest=assertion.submods.container.image_digest' \
  --attribute-condition="assertion.swname == 'CONFIDENTIAL_SPACE' && assertion.dbgstat == 'disabled-since-boot' && 'STABLE' in assertion.submods.confidential_space.support_attributes && assertion.secboot == true && assertion.hwmodel in ['GCP_AMD_SEV', 'GCP_AMD_SEV_ES'] && assertion.submods.gce.project_number == 'WORKLOAD_OPERATOR_PROJECT_NUMBER' && 'WORKLOAD_SERVICE_ACCOUNT' in assertion.google_service_accounts && assertion.submods.container.cmd_override == ['-m', 'app.cloud_verify']"
```

Bind `roles/secretmanager.secretAccessor` on only that secret to the `principalSet`
whose `attribute.image_digest` equals the resolved digest. Use the numeric project
number in the principal URI. Follow Google's current command template because IAM
member escaping differs across shells.

The workload requires these non-secret environment values:

- `WIF_AUDIENCE=//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/devfest-attested/providers/attestation-verifier`
- `PROTECTED_SECRET_RESOURCE=projects/PROJECT_ID/secrets/SECRET/versions/VERSION`
- `PROTECTED_SECRET_EXPECTED_SHA256`

The image launch policy permits only those three environment overrides and the
one-shot `app.cloud_verify` command. The WIF provider condition checks that exact
command override. Resource-level IAM still limits the federated identity to the one
synthetic secret, so changing a resource name cannot broaden access.

Replace `WORKLOAD_OPERATOR_PROJECT_NUMBER` and `WORKLOAD_SERVICE_ACCOUNT` with the
numeric operator project and full service-account email before creating the
provider. These conditions prevent the same public container digest from obtaining
the identity when launched from another project or with another attached service
account. `STABLE` and `dbgstat` reject debug and unsupported Confidential Space
images. The secret IAM binding supplies the immutable image-digest restriction.

## Launch

After setting `WORKLOAD_SERVICE_ACCOUNT` and the digest-pinned `IMAGE_URI`:

```bash
make deploy
```

The script uses production `confidential-space`, Secure Boot, SEV, N2D, standard
persistent disk, boot-disk auto-delete, and automatic VM deletion after 30 minutes.
Re-check supported machine types and zones immediately before running. It creates
no inbound application firewall rule and launches only the verifier. Audit existing
firewall policy; no new rule alone does not establish network isolation.

The cloud workload is a one-shot outbound verifier and the image declares no inbound
port. The stage UI remains local. Container publishing in local/CI verification does
not change the image digest or open a cloud firewall rule.

## Required verification

1. Inspect secret and inherited project IAM. Confirm the attached workload account
   has no direct secret access and no Owner/Editor. Never weaken or broaden IAM to
   manufacture a negative test. An administrative developer may legitimately have
   access; that is not the workload identity being tested.
2. Launch the digest-pinned production workload. Confirm its logs contain no secret,
   token, credentials, or document content.
3. Read the one-shot verifier's safe Cloud Logging output. `VERIFIED` is emitted only after STS accepts the launcher token,
   IAM authorizes the digest-mapped principal, Secret Manager releases the value,
   and its expected SHA-256 matches.
4. Locally run `make cloud-verify`: missing launcher evidence must fail closed.
   Where inexpensive, launch an unauthorized workload using unchanged restrictive
   IAM and confirm resource denial. Do not temporarily grant broad access or alter
   the accepted digest to make a negative test pass. Mock tests are not cloud denials.
5. Exercise safe and poisoned scenarios and confirm the denied executor does not run.

Inside the workload, `python -m app.cloud_verify` performs the resource-release check
and exits nonzero unless the evidence is live and verified. It emits only safe claim
metadata and the released resource's SHA-256, never the plaintext value or token.

Do not report attestation or protected-resource status as passed until these observed
results are captured. A decoded JWT alone is not sufficient.

Capture only the verifier's allowlisted evidence, VM configuration, inspected IAM,
and negative-test results. Never dump JWTs, credentials, metadata access tokens,
or secret payloads. Then run [the VM-only cleanup](GCP_CLEANUP.md). Cloud release
does not prove that a live Gemini attack was triggered; five prior poisoned live
trials reported by the user remained local summaries.

## References

- [Deploy workloads](https://cloud.google.com/confidential-computing/confidential-space/docs/deploy-workloads)
- [Create and grant access to confidential resources](https://cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources)
- [Attestation token claims](https://cloud.google.com/confidential-computing/confidential-space/docs/reference/token-claims)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
- [Current source verification](CLOUD_VERIFICATION_SOURCES.md)

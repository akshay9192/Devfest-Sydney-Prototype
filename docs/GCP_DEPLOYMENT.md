# GCP deployment

## Current status

Cloud deployment is not performed in this checkout. On 2026-09-25 the host had no
`gcloud` executable, so no active account, project, region, zone, billing state, or
quota could be safely inspected. The commands below are prepared but must not be
treated as verified results.

## Chosen design

Use a CPU-only Confidential Space production image on an SEV-backed
`n2d-standard-2` where that machine and Confidential Space are supported. Pin the
application image by digest. Google Cloud Attestation supplies the launcher token;
a Workload Identity Pool provider checks the stable Confidential Space attribute
and maps the image digest. Secret Manager releases one synthetic value to the
matching federated principal.

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
  --attribute-condition="assertion.swname == 'CONFIDENTIAL_SPACE' && 'STABLE' in assertion.submods.confidential_space.support_attributes"
```

Bind `roles/secretmanager.secretAccessor` on only that secret to the `principalSet`
whose `attribute.image_digest` equals the resolved digest. Use the numeric project
number in the principal URI. Follow Google's current command template because IAM
member escaping differs across shells.

The workload requires these non-secret environment values:

- `APP_MODE=live`
- `ATTESTATION_MODE=confidential_space`
- `GEMINI_MODEL` selected from the currently supported Vertex AI models
- `WIF_AUDIENCE=//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/devfest-attested/providers/attestation-verifier`
- `PROTECTED_SECRET_RESOURCE=projects/PROJECT_ID/secrets/SECRET/versions/VERSION`
- `PROTECTED_SECRET_EXPECTED_SHA256`

Confidential Space environment overrides require an image launch policy permitting
those exact names. Before deployment, follow the current launch-policy documentation
and add the names; do not permit arbitrary environment overrides. Add corresponding
provider conditions if operators must not change their values.

## Launch

After setting `WORKLOAD_SERVICE_ACCOUNT` and the digest-pinned `IMAGE_URI`:

```bash
make deploy
```

The script uses the production `confidential-space` image, Secure Boot, SEV, and an
N2D machine. Re-check supported machine types and zones immediately before running
because availability changes.

## Required verification

1. From the local developer identity, attempt to access the secret version. Record
   the IAM denial. Remove any direct user grants before testing.
2. Launch the digest-pinned production workload. Confirm its logs contain no secret,
   token, credentials, or document content.
3. Load `/api/state`. `VERIFIED` is emitted only after STS accepts the launcher token,
   IAM authorizes the digest-mapped principal, Secret Manager releases the value,
   and its expected SHA-256 matches.
4. Change the allowed image digest or launch a different image. Confirm the same
   resource request fails and the UI reports `FAILED` / not released.
5. Exercise safe and poisoned scenarios and confirm the denied executor does not run.

Do not report attestation or protected-resource status as passed until these observed
results are captured. A decoded JWT alone is not sufficient.

## References

- [Deploy workloads](https://cloud.google.com/confidential-computing/confidential-space/docs/deploy-workloads)
- [Create and grant access to confidential resources](https://cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources)
- [Attestation token claims](https://cloud.google.com/confidential-computing/confidential-space/docs/reference/token-claims)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)

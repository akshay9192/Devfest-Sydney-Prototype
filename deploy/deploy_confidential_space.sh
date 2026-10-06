#!/usr/bin/env bash
set -euo pipefail

required=(
  GCP_PROJECT GCP_REGION GCP_ZONE WORKLOAD_SERVICE_ACCOUNT IMAGE_URI
  WIF_AUDIENCE PROTECTED_SECRET_RESOURCE PROTECTED_SECRET_EXPECTED_SHA256
)
for name in "${required[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required environment variable: ${name}" >&2
    exit 2
  fi
done

if [[ "${GCP_PROJECT}" != newproject-490108 ||
      "${GCP_REGION}" != australia-southeast1 ||
      "${GCP_ZONE}" != australia-southeast1-b ||
      "${WORKLOAD_SERVICE_ACCOUNT}" != devfest-confidential-workload@newproject-490108.iam.gserviceaccount.com ||
      "${WIF_AUDIENCE}" != //iam.googleapis.com/projects/131985117376/locations/global/workloadIdentityPools/devfest-attested/providers/attestation-verifier ||
      "${PROTECTED_SECRET_RESOURCE}" != projects/131985117376/secrets/devfest-protected-state/versions/1 ||
      "${PROTECTED_SECRET_EXPECTED_SHA256}" != 4350401800f70db43df2e151b98fbdcd2f2f2a43a91e19ce26368f93b72b5a96 ]]; then
  echo "Refusing unexpected project, runtime location, or protected-resource identity." >&2
  exit 2
fi

active_project="$(gcloud config get-value project 2>/dev/null)"
if [[ "${active_project}" != "${GCP_PROJECT}" ]]; then
  echo "Refusing deployment: active project '${active_project}' != '${GCP_PROJECT}'." >&2
  exit 2
fi

if [[ ! "${IMAGE_URI}" =~ ^australia-southeast1-docker.pkg.dev/newproject-490108/devfest/controller@sha256:[a-f0-9]{64}$ ]]; then
  echo "IMAGE_URI must be pinned by digest, not a mutable tag." >&2
  exit 2
fi

echo "Selected n2d-highcpu-2: 2 vCPUs, 2 GiB; CPU-only SEV Confidential Space verifier."
echo "One VM; automatic deletion after 30 minutes. Delete sooner after collecting evidence."

gcloud compute instances create devfest-verifiable-ai \
  --project="${GCP_PROJECT}" \
  --zone="${GCP_ZONE}" \
  --machine-type=n2d-highcpu-2 \
  --confidential-compute-type=SEV \
  --maintenance-policy=MIGRATE \
  --max-run-duration=30m \
  --instance-termination-action=DELETE \
  --boot-disk-auto-delete \
  --boot-disk-type=pd-standard \
  --shielded-secure-boot \
  --image-project=confidential-space-images \
  --image-family=confidential-space \
  --service-account="${WORKLOAD_SERVICE_ACCOUNT}" \
  --scopes=cloud-platform \
  --metadata="^~^tee-image-reference=${IMAGE_URI}~tee-cmd=[\"-m\",\"app.cloud_verify\"]~tee-env-WIF_AUDIENCE=${WIF_AUDIENCE}~tee-env-PROTECTED_SECRET_RESOURCE=${PROTECTED_SECRET_RESOURCE}~tee-env-PROTECTED_SECRET_EXPECTED_SHA256=${PROTECTED_SECRET_EXPECTED_SHA256}~tee-restart-policy=Never~tee-container-log-redirect=cloud_logging"

echo "Created production Confidential Space workload devfest-verifiable-ai."
echo "Collect safe release evidence, then delete the VM as documented in docs/GCP_CLEANUP.md."

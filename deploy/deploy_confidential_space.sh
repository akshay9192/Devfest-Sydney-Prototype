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

active_project="$(gcloud config get-value project 2>/dev/null)"
if [[ "${active_project}" != "${GCP_PROJECT}" ]]; then
  echo "Refusing deployment: active project '${active_project}' != '${GCP_PROJECT}'." >&2
  exit 2
fi

if [[ "${IMAGE_URI}" != *@sha256:* ]]; then
  echo "IMAGE_URI must be pinned by digest, not a mutable tag." >&2
  exit 2
fi

gcloud compute instances create devfest-verifiable-ai \
  --project="${GCP_PROJECT}" \
  --zone="${GCP_ZONE}" \
  --machine-type=n2d-standard-2 \
  --confidential-compute-type=SEV \
  --maintenance-policy=MIGRATE \
  --shielded-secure-boot \
  --image-project=confidential-space-images \
  --image-family=confidential-space \
  --service-account="${WORKLOAD_SERVICE_ACCOUNT}" \
  --scopes=cloud-platform \
  --metadata="^~^tee-image-reference=${IMAGE_URI}~tee-cmd=[\"python\",\"-m\",\"app.cloud_verify\"]~tee-env-WIF_AUDIENCE=${WIF_AUDIENCE}~tee-env-PROTECTED_SECRET_RESOURCE=${PROTECTED_SECRET_RESOURCE}~tee-env-PROTECTED_SECRET_EXPECTED_SHA256=${PROTECTED_SECRET_EXPECTED_SHA256}~tee-restart-policy=Never~tee-container-log-redirect=cloud_logging"

echo "Created production Confidential Space workload devfest-verifiable-ai."
echo "Complete the claim-constrained WIF and protected-resource checks in docs/GCP_DEPLOYMENT.md."

# GCP cleanup

No resources have been created yet. After a future verified run, classify every
resource as `KEEP FOR DEVFEST` or `DELETE/STOP NOW` and record the decision in the
cloud verification report.

With the intended project selected, the minimal cleanup sequence is:

```bash
gcloud compute instances delete devfest-verifiable-ai --zone="$GCP_ZONE" --project="$GCP_PROJECT"
gcloud secrets remove-iam-policy-binding devfest-verifiable-ai-secret \
  --project="$GCP_PROJECT" --member="$ATTESTED_PRINCIPAL_SET" \
  --role=roles/secretmanager.secretAccessor
gcloud secrets delete devfest-verifiable-ai-secret --project="$GCP_PROJECT"
gcloud iam workload-identity-pools providers delete attestation-verifier \
  --workload-identity-pool=devfest-verifiable-ai-wif --location=global \
  --project="$GCP_PROJECT"
gcloud iam workload-identity-pools delete devfest-verifiable-ai-wif \
  --location=global --project="$GCP_PROJECT"
gcloud artifacts repositories delete devfest-verifiable-ai \
  --location="$GCP_REGION" --project="$GCP_PROJECT"
gcloud iam service-accounts delete \
  "devfest-verifiable-ai-workload@$GCP_PROJECT.iam.gserviceaccount.com" \
  --project="$GCP_PROJECT"
```

Inspect each target before confirming deletion. Deleting the VM stops compute cost;
Artifact Registry storage, Secret Manager versions, and retained logs can continue
to incur small charges until removed under the project's retention rules.

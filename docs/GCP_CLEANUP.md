# GCP cleanup

After collecting safe evidence, delete the disposable verifier immediately:

```bash
gcloud compute instances delete devfest-verifiable-ai \
  --zone="$GCP_ZONE" --project=newproject-490108 --quiet
gcloud compute instances list --project=newproject-490108
gcloud compute disks list --project=newproject-490108
```

The deployment enables boot-disk auto-delete and a 30-minute automatic VM deletion
backstop. Verify the boot disk is gone; stopping alone leaves disk charges. An
already auto-deleted VM can produce a not-found error: confirm using inventory.

Keep the `devfest` Artifact Registry repository and final digest-pinned image,
`devfest-attested` pool and `attestation-verifier` provider, dedicated workload
service account, `devfest-protected-state` synthetic secret, required digest-bound
IAM, and safe evidence/logs. Do not delete these persistent rehearsal resources
or remove their access bindings during routine cleanup.

The 2026-10-02 verifier VM and boot disk were deleted; final instance/disk
inventory was empty. See `CLOUD_VERIFICATION_REPORT.md` for observed evidence.
Persistent storage, secret versions, and logs can incur small ongoing charges.

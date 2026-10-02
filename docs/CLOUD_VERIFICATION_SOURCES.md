# Cloud verification sources

Retrieved from official Google documentation on 2026-09-25. These sources govern
the deployment design; planned commands are not evidence that deployment succeeded.

## Rechecked 2026-10-02

- [Confidential VM release notes](https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/release-notes): C4 TDX GA on September 23, 2026; SEV-SNP boot/performance issue noted July 28 through an expected November resolution.
- [Confidential Space release notes](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/release-notes): production image 260800 announced September 15, 2026. The project resolved production `confidential-space-260800` before launch.
- [Runtime overview](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview): a hardened OS and launcher run on Confidential VM; Google Cloud Attestation supports SEV and TDX.
- [Supported VM configurations](https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/supported-configurations): SEV supports N2D/C2D/C3D/C4D; N2D SEV-SNP and TDX have specific zone lists. Query CPU platforms before selecting SEV.
- [Direct VM attestation](https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/attestation): vTPM boot evidence differs from SEV-SNP/TDX hardware reports; Google Cloud Attestation lists SEV and C3 TDX. A plain VM does not supply Space launcher measurements.
- [First Space environment](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/create-your-first-confidential-space-environment): documents `/run/container_launcher/attestation_verifier_claims_token` as an external-account credential source.
- [Direct resource access](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources): WIF maps signed assertions to container-digest IAM; this remains the selected release pattern.
- [Deployment](https://docs.cloud.google.com/confidential-computing/confidential-space/docs/deploy-workloads): CPU SEV/TDX, production family, Secure Boot, N2D SEV `MIGRATE`, attached account, and launcher metadata.
- [Runtime limit](https://docs.cloud.google.com/compute/docs/instances/limit-vm-runtime): `--max-run-duration` with `--instance-termination-action=DELETE` bounds VM lifetime. Installed GA gcloud help also exposes both flags.
- [Confidential VM pricing](https://cloud.google.com/confidential-computing/confidential-vm/pricing): include the confidential surcharge in addition to compute, disk, external IP, and API/storage costs. Project pricing and credit balance have not been observed here.

These are product checks, not deployment evidence. Retain Confidential Space on
SEV Confidential VM; newer VM TDX GA hardware does not automatically
satisfy the existing Space launcher/WIF path.

| Topic | Verified point | Official source |
|---|---|---|
| Confidential Space overview | A container runs on the hardened Confidential Space image on a Confidential VM; Google Cloud Attestation supports SEV and TDX. | <https://docs.cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview> |
| Workload deployment | Production uses image family `confidential-space`; CPU workloads can use SEV or TDX and a supported machine and zone. | <https://docs.cloud.google.com/confidential-computing/confidential-space/docs/deploy-workloads> |
| Direct resource access | Direct federated resource access is recommended; WIF evaluates attestation assertions and can map the container image digest. | <https://docs.cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources> |
| Attestation claims | Claims include `swname`, support attributes, container digest, project, instance, and zone. | <https://docs.cloud.google.com/confidential-computing/confidential-space/docs/reference/token-claims> |
| Workload launch policy | Container labels restrict command and environment overrides; production log redirection must be explicitly allowed. | <https://docs.cloud.google.com/confidential-computing/confidential-space/docs/create-customize-workloads> |
| Confidential Space images | Production images carry support attributes; `STABLE` is supported and monitored, while debug images have no support attributes. | <https://docs.cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-images> |
| Supported machines and zones | N2D/SEV and C3/TDX support is zone-specific and must be queried before launch. | <https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/supported-configurations> |
| Workload Identity Federation | Direct resource access is the recommended WIF pattern where the target API supports federated identities. | <https://docs.cloud.google.com/iam/docs/workload-identity-federation> |
| Secret Manager IAM | `roles/secretmanager.secretAccessor` can be granted at one secret, the lowest applicable resource. | <https://docs.cloud.google.com/secret-manager/docs/access-control> |
| Artifact Registry IAM | `roles/artifactregistry.reader` provides read-only repository access and can be scoped to a repository. | <https://docs.cloud.google.com/artifact-registry/docs/access-control> |
| Vertex AI authentication | Local live use relies on Application Default Credentials; no downloaded service-account key is required. | <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/gcp-auth> |
| Gemini lifecycle | `gemini-3.5-flash` is stable through at least 2027-05-19; Gemini 2.5 Flash retires on 2026-10-20. | <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions> |
| Structured output | Gemini 3.5 Flash supports response schemas; both a schema and JSON MIME type are required for guaranteed JSON shape. | <https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output> |
| Google Gen AI SDK | The supported Python SDK accepts Pydantic response schemas and Vertex AI credentials. | <https://googleapis.github.io/python-genai/> |
| Pricing | Confidential Space has no separate service fee; the underlying Compute Engine and related services are billed. | <https://cloud.google.com/confidential-computing/confidential-space/pricing> |

Before deployment, `gcloud compute machine-types list` and the project's quota and
zone availability remain authoritative for the actual project.

"""Run the fixed DevFest cloud proof and clean up its disposable VM."""

from __future__ import annotations

import json
import os
import shutil
import subprocess  # nosec B404
import time
from pathlib import Path
from typing import Any

from app.domain.models import AttestationEvidence

PROJECT = "newproject-490108"
ZONE = "australia-southeast1-b"
VM = "devfest-verifiable-ai"
POOL = "devfest-attested"
PROVIDER = "attestation-verifier"
RESOURCE_NAME = "devfest-protected-state"
SA = f"devfest-confidential-workload@{PROJECT}.iam.gserviceaccount.com"
SHA = "4350401800f70db43df2e151b98fbdcd2f2f2a43a91e19ce26368f93b72b5a96"
DIGEST = "sha256:4209cd130c3384b3f18a621691ae97934140065b29e4c523c69cf96fa8ed5431"
IMAGE = f"australia-southeast1-docker.pkg.dev/{PROJECT}/devfest/controller@{DIGEST}"
AUDIENCE = (
    "//iam.googleapis.com/projects/131985117376/locations/global/"
    f"workloadIdentityPools/{POOL}/providers/{PROVIDER}"
)
CONDITION = (
    "assertion.swname == 'CONFIDENTIAL_SPACE' && "
    "assertion.dbgstat == 'disabled-since-boot' && "
    "'STABLE' in assertion.submods.confidential_space.support_attributes && "
    "assertion.secboot == true && "
    "assertion.hwmodel in ['GCP_AMD_SEV', 'GCP_AMD_SEV_ES'] && "
    "assertion.submods.gce.project_number == '131985117376' && "
    f"'{SA}' in assertion.google_service_accounts && "
    "assertion.submods.container.cmd_override == ['-m', 'app.cloud_verify']"
)


def cloud(*args: str) -> Any:
    cli = shutil.which("gcloud")
    if cli is None:
        raise RuntimeError("gcloud is required")
    # Only this module's fixed, non-secret commands use the trusted CLI.
    result = subprocess.run(  # noqa: S603  # nosec B603
        [cli, *args, f"--project={PROJECT}", "--format=json", "--quiet"],
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    return json.loads(result.stdout or "null")


def preflight() -> None:
    if os.environ.get("GCP_PROJECT") != PROJECT or os.environ.get("IMAGE_URI") != IMAGE:
        raise RuntimeError("Source deploy/rehearsal.env.sh; unexpected project or image")
    if cloud("config", "get-value", "project") != PROJECT:
        raise RuntimeError("Active project differs from authorized project")
    if cloud("compute", "instances", "list", f"--filter=name={VM}"):
        raise RuntimeError("Existing verifier VM: inspect it before rerunning")
    cloud("artifacts", "docker", "images", "describe", IMAGE)
    pool = cloud("iam", "workload-identity-pools", "describe", POOL, "--location=global")
    if pool.get("state") != "ACTIVE":
        raise RuntimeError("WIF pool is not active")
    account = cloud("iam", "service-accounts", "describe", SA)
    if account.get("disabled", False):
        raise RuntimeError("Workload account disabled")
    project_policy = cloud("projects", "get-iam-policy", PROJECT)
    roles = {
        binding["role"]
        for binding in project_policy.get("bindings", [])
        if f"serviceAccount:{SA}" in binding.get("members", [])
    }
    if roles != {
        "roles/artifactregistry.reader",
        "roles/confidentialcomputing.workloadUser",
        "roles/logging.logWriter",
    }:
        raise RuntimeError("Unexpected workload account project roles")
    provider = cloud(
        "iam",
        "workload-identity-pools",
        "providers",
        "describe",
        PROVIDER,
        f"--workload-identity-pool={POOL}",
        "--location=global",
    )
    if (
        provider.get("state") != "ACTIVE"
        or provider.get("attributeCondition") != CONDITION
        or provider.get("attributeMapping", {}).get("attribute.image_digest")
        != "assertion.submods.container.image_digest"
        or provider.get("oidc")
        != {
            "issuerUri": "https://confidentialcomputing.googleapis.com",
            "allowedAudiences": ["https://sts.googleapis.com"],
        }
    ):
        raise RuntimeError("Unexpected WIF policy; no workload launched")
    policy = cloud("secrets", "get-iam-policy", RESOURCE_NAME)
    member = (
        "principalSet://iam.googleapis.com/projects/131985117376/locations/global/"
        f"workloadIdentityPools/{POOL}/attribute.image_digest/{DIGEST}"
    )
    bindings = policy.get("bindings", [])
    if bindings != [{"role": "roles/secretmanager.secretAccessor", "members": [member]}]:
        raise RuntimeError("Secret IAM must authorize only the pinned federated digest")
    version = cloud("secrets", "versions", "describe", "1", f"--secret={RESOURCE_NAME}")
    if version.get("state") != "ENABLED":
        raise RuntimeError("Synthetic secret version unavailable")
    firewall = cloud("compute", "firewall-rules", "describe", "devfest-confidential-deny-ingress")
    if (
        firewall.get("disabled", False)
        or firewall.get("priority") != 100
        or firewall.get("denied") != [{"IPProtocol": "all"}]
        or firewall.get("sourceRanges") != ["0.0.0.0/0"]
        or firewall.get("targetTags")
        or firewall.get("targetServiceAccounts") != [SA]
    ):
        raise RuntimeError("Expected workload-account ingress denial unavailable")


def release_evidence(entries: list[dict[str, Any]]) -> AttestationEvidence | None:
    for entry in entries:
        payload = entry.get("jsonPayload", {})
        message = payload.get("MESSAGE", entry.get("textPayload", ""))
        if not isinstance(message, str) or not message.startswith("{"):
            continue
        evidence = AttestationEvidence.model_validate_json(message)
        if (
            not evidence.resource_release_allowed
            or evidence.safe_claims.get("resource_sha256") != SHA
            or evidence.safe_claims.get("image_digest") != DIGEST
            or evidence.safe_claims.get("project_id") != PROJECT
            or evidence.safe_claims.get("software") != "CONFIDENTIAL_SPACE"
            or evidence.safe_claims.get("zone") != ZONE
        ):
            raise RuntimeError("Cloud verifier failed or returned unexpected identity")
        return evidence
    return None


def main() -> None:
    preflight()
    root = Path(__file__).resolve().parents[1]
    # The deployment script validates every supplied resource identity again.
    try:
        subprocess.run(  # noqa: S603  # nosec B603
            ["/bin/bash", str(root / "deploy/deploy_confidential_space.sh")],
            check=True,
        )
        instance = cloud("compute", "instances", "describe", VM, f"--zone={ZONE}")
        instance_id = instance["id"]
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            evidence = release_evidence(
                cloud(
                    "logging",
                    "read",
                    f'resource.labels.instance_id="{instance_id}" AND '
                    '(jsonPayload.MESSAGE:"protected_resource" OR '
                    'textPayload:"protected_resource")',
                    "--freshness=30m",
                    "--limit=10",
                )
            )
            if evidence:
                print(evidence.model_dump_json())
                return
            print("Waiting for safe verifier evidence...", flush=True)
            time.sleep(15)
        raise RuntimeError("Timed out without verified resource release")
    finally:
        cloud("compute", "instances", "delete", VM, f"--zone={ZONE}")
        print("Disposable verifier deleted; persistent rehearsal resources preserved.")


if __name__ == "__main__":
    main()

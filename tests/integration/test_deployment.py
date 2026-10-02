import os
import subprocess
from pathlib import Path

import pytest

from scripts.cloud_rehearsal import AUDIENCE, SA, SHA

SCRIPT = Path("deploy/deploy_confidential_space.sh").resolve()
DIGEST = "sha256:" + "1" * 64


def deploy(
    tmp_path: Path, *, image: str, project: str = "newproject-490108"
) -> tuple[int, list[str]]:
    """Record CLI arguments without authenticating or creating cloud resources."""
    calls = tmp_path / "calls"
    cli = tmp_path / "gcloud"
    cli.write_text(
        '#!/bin/bash\nif [[ "$1" == config ]]; then echo "$ACTIVE_PROJECT"; '
        'else printf "%s\\n" "$@" > "$CALLS"; fi\n',
        encoding="utf-8",
    )
    cli.chmod(0o700)
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "ACTIVE_PROJECT": project,
        "CALLS": str(calls),
        "GCP_PROJECT": "newproject-490108",
        "GCP_REGION": "australia-southeast1",
        "GCP_ZONE": "australia-southeast1-b",
        "WORKLOAD_SERVICE_ACCOUNT": SA,
        "IMAGE_URI": image,
        "WIF_AUDIENCE": AUDIENCE,
        "PROTECTED_SECRET_RESOURCE": (
            "projects/131985117376/secrets/devfest-protected-state/versions/1"
        ),
        "PROTECTED_SECRET_EXPECTED_SHA256": SHA,
    }
    result = subprocess.run(["/bin/bash", str(SCRIPT)], env=env, capture_output=True, check=False)
    return result.returncode, calls.read_text().splitlines() if calls.exists() else []


def test_deployment_bounds_compute_lifetime_and_preserves_production_identity(
    tmp_path: Path,
) -> None:
    image = f"australia-southeast1-docker.pkg.dev/newproject-490108/devfest/controller@{DIGEST}"
    code, args = deploy(tmp_path, image=image)
    assert code == 0
    assert args[:4] == ["compute", "instances", "create", "devfest-verifiable-ai"]
    for required in (
        "--machine-type=n2d-highcpu-2",
        "--confidential-compute-type=SEV",
        "--shielded-secure-boot",
        "--image-family=confidential-space",
        "--max-run-duration=30m",
        "--instance-termination-action=DELETE",
        "--boot-disk-auto-delete",
        "--boot-disk-type=pd-standard",
    ):
        assert required in args
    metadata = next(arg for arg in args if arg.startswith("--metadata="))
    assert f"tee-image-reference={image}" in metadata
    assert 'tee-cmd=["-m","app.cloud_verify"]' in metadata
    assert "tee-restart-policy=Never" in metadata
    assert not any("debug" in arg or "accelerator" in arg for arg in args)


@pytest.mark.parametrize(
    "image",
    [
        "registry/image:latest",
        "registry/image@sha256:",
        "registry/image@sha256:xyz",
        "registry/image@sha256:" + "a" * 63,
    ],
)
def test_invalid_image_never_creates_compute(tmp_path: Path, image: str) -> None:
    code, args = deploy(tmp_path, image=image)
    assert code == 2
    assert args == []


def test_unexpected_project_never_creates_compute(tmp_path: Path) -> None:
    code, args = deploy(tmp_path, image=f"registry/image@{DIGEST}", project="wrong")
    assert code == 2
    assert args == []

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import google.auth
import requests
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request

from app.domain.models import AttestationEvidence, AttestationStatus

JWT_SUBJECT_TYPE = "urn:ietf:params:oauth:token-type:jwt"
STS_ENDPOINT = "https://sts.googleapis.com/v1/token"


class ProtectedResourceUnavailable(PermissionError):
    pass


class AttestationProvider(Protocol):
    def evidence(self) -> AttestationEvidence: ...


@dataclass(frozen=True)
class CachedDemoAttestationProvider:
    def evidence(self) -> AttestationEvidence:
        return AttestationEvidence(
            status=AttestationStatus.CACHED_DEMO_EVIDENCE,
            workload_identity=None,
            safe_claims={"source": "offline fixture", "resource_released": "false"},
            live=False,
        )


@dataclass(frozen=True)
class LocalAttestationProvider:
    def evidence(self) -> AttestationEvidence:
        return AttestationEvidence(
            status=AttestationStatus.LOCAL_DEMO,
            safe_claims={"environment": "local", "resource_released": "false"},
            live=False,
        )


@dataclass(frozen=True)
class ConfidentialSpaceAttestationProvider:
    """Treat successful claim-constrained resource access as the live proof."""

    token_path: Path = Path("/run/container_launcher/attestation_verifier_claims_token")

    def evidence(self) -> AttestationEvidence:
        try:
            audience = os.environ["WIF_AUDIENCE"]
            secret_resource = os.environ["PROTECTED_SECRET_RESOURCE"]
            expected_sha256 = os.environ["PROTECTED_SECRET_EXPECTED_SHA256"]
            credentials, _ = google.auth.load_credentials_from_dict(  # type: ignore[no-untyped-call]
                {
                    "type": "external_account",
                    "audience": audience,
                    "subject_token_type": JWT_SUBJECT_TYPE,
                    "token_url": STS_ENDPOINT,
                    "credential_source": {"file": str(self.token_path)},
                },
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            credentials.refresh(Request())
            response = requests.get(
                f"https://secretmanager.googleapis.com/v1/{secret_resource}:access",
                headers={"Authorization": f"Bearer {credentials.token}"},
                timeout=10,
            )
            response.raise_for_status()
            encoded_value = response.json()["payload"]["data"]
            value = base64.b64decode(encoded_value, validate=True)
            resource_sha256 = hashlib.sha256(value).hexdigest()
            if resource_sha256 != expected_sha256:
                return self._failed()

            claims = self._safe_claims()
            return AttestationEvidence(
                status=AttestationStatus.VERIFIED,
                workload_identity=claims.pop("subject", None),
                safe_claims=claims
                | {
                    "protected_resource": "released",
                    "resource_sha256": resource_sha256,
                },
                live=True,
            )
        except (
            GoogleAuthError,
            IndexError,
            KeyError,
            OSError,
            TypeError,
            ValueError,
            requests.RequestException,
        ):
            return self._failed()

    def _safe_claims(self) -> dict[str, str]:
        token = self.token_path.read_text(encoding="utf-8").strip()
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        submods = claims.get("submods", {})
        container = submods.get("container", {})
        gce = submods.get("gce", {})
        return {
            "subject": str(claims.get("sub", "")),
            "software": str(claims.get("swname", "")),
            "image_digest": str(container.get("image_digest", "")),
            "project_id": str(gce.get("project_id", "")),
            "zone": str(gce.get("zone", "")),
        }

    @staticmethod
    def _failed() -> AttestationEvidence:
        return AttestationEvidence(
            status=AttestationStatus.FAILED,
            safe_claims={"protected_resource": "not released"},
            live=False,
        )


class ProtectedResourceGate:
    def release(self, evidence: AttestationEvidence, resource: str) -> str:
        if not evidence.resource_release_allowed:
            raise ProtectedResourceUnavailable("Verified live attestation is required")
        return resource

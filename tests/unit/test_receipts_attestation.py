import base64
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.domain.models import (
    Action,
    AttestationEvidence,
    AttestationStatus,
    Decision,
    DecisionOutcome,
    Destination,
    Proposal,
    Sensitivity,
)
from app.services.attestation import (
    ConfidentialSpaceAttestationProvider,
    ProtectedResourceGate,
    ProtectedResourceUnavailable,
)
from app.services.receipt_service import ReceiptService, sha256_file


def test_hash_generation_is_stable(tmp_path: Path) -> None:
    path = tmp_path / "value"
    path.write_text("abc", encoding="utf-8")
    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_receipt_omits_full_reason_and_document(config_dir: Path) -> None:
    secret = "SYNTHETIC_SECRET_DOCUMENT_CONTENT"
    proposal = Proposal(
        action=Action.SUMMARIZE_LOCALLY,
        sensitivity=Sensitivity.CONFIDENTIAL,
        destination=Destination.LOCAL,
        user_confirmation=False,
        destination_id="local-processor",
        reason=f"reason containing {secret}",
    )
    receipt = ReceiptService().create(
        request_id="request123",
        playbook_path=config_dir / "PLAYBOOK.md",
        system_policy_path=config_dir / "SYSTEM_POLICY.yaml",
        user_policy_path=config_dir / "VALIDATED_USER_POLICY.yaml",
        model_identifier="test-model",
        proposal=proposal,
        decision=Decision(
            outcome=DecisionOutcome.ALLOW,
            matched_rule_ids=("local",),
            reason_codes=("LOCAL",),
        ),
        attestation=AttestationEvidence(status=AttestationStatus.LOCAL_DEMO),
    )
    assert secret not in receipt.model_dump_json()
    assert receipt.proposal is not None
    assert "reason_sha256" in receipt.proposal


def test_protected_resource_requires_verified_live_attestation() -> None:
    gate = ProtectedResourceGate()
    with pytest.raises(ProtectedResourceUnavailable):
        gate.release(AttestationEvidence(status=AttestationStatus.FAILED), "synthetic")
    with pytest.raises(ProtectedResourceUnavailable):
        gate.release(
            AttestationEvidence(status=AttestationStatus.CACHED_DEMO_EVIDENCE, live=False),
            "synthetic",
        )


def test_verified_live_attestation_releases_resource() -> None:
    evidence = AttestationEvidence(status=AttestationStatus.VERIFIED, live=True)
    assert ProtectedResourceGate().release(evidence, "synthetic") == "synthetic"


def test_confidential_space_marks_verified_only_after_resource_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    protected_value = b"synthetic-attested-value"
    claims = {
        "sub": "projects/demo/zones/test/instances/demo",
        "swname": "CONFIDENTIAL_SPACE",
        "submods": {
            "container": {"image_digest": "sha256:expected"},
            "gce": {"project_id": "demo", "zone": "australia-southeast1-b"},
        },
    }
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    token_path = tmp_path / "token"
    token_path.write_text(f"header.{payload}.signature", encoding="utf-8")

    credentials = SimpleNamespace(token="short-lived-token", refresh=lambda request: None)
    monkeypatch.setattr(
        "app.services.attestation.google.auth.load_credentials_from_dict",
        lambda *args, **kwargs: (credentials, None),
    )
    response = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"payload": {"data": base64.b64encode(protected_value).decode("ascii")}},
    )
    monkeypatch.setattr("app.services.attestation.requests.get", lambda *args, **kwargs: response)
    monkeypatch.setenv("WIF_AUDIENCE", "//iam.googleapis.com/projects/1/pools/p/providers/v")
    monkeypatch.setenv("PROTECTED_SECRET_RESOURCE", "projects/demo/secrets/value/versions/1")
    monkeypatch.setenv(
        "PROTECTED_SECRET_EXPECTED_SHA256", hashlib.sha256(protected_value).hexdigest()
    )

    evidence = ConfidentialSpaceAttestationProvider(token_path=token_path).evidence()
    assert evidence.resource_release_allowed
    assert evidence.safe_claims["image_digest"] == "sha256:expected"
    assert evidence.safe_claims["protected_resource"] == "released"
    assert evidence.safe_claims["resource_sha256"] == hashlib.sha256(protected_value).hexdigest()


def test_confidential_space_fails_closed_without_configuration(tmp_path: Path) -> None:
    evidence = ConfidentialSpaceAttestationProvider(token_path=tmp_path / "missing").evidence()
    assert evidence.status is AttestationStatus.FAILED
    assert not evidence.resource_release_allowed


def test_confidential_space_fails_closed_on_resource_hash_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    token_path = tmp_path / "token"
    token_path.write_text("header.e30.signature", encoding="utf-8")
    credentials = SimpleNamespace(token="short-lived-token", refresh=lambda request: None)
    monkeypatch.setattr(
        "app.services.attestation.google.auth.load_credentials_from_dict",
        lambda *args, **kwargs: (credentials, None),
    )
    response = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"payload": {"data": base64.b64encode(b"wrong").decode("ascii")}},
    )
    monkeypatch.setattr("app.services.attestation.requests.get", lambda *args, **kwargs: response)
    monkeypatch.setenv("WIF_AUDIENCE", "//iam.googleapis.com/projects/1/pools/p/providers/v")
    monkeypatch.setenv("PROTECTED_SECRET_RESOURCE", "projects/demo/secrets/value/versions/1")
    monkeypatch.setenv("PROTECTED_SECRET_EXPECTED_SHA256", hashlib.sha256(b"expected").hexdigest())

    evidence = ConfidentialSpaceAttestationProvider(token_path=token_path).evidence()

    assert evidence.status is AttestationStatus.FAILED
    assert not evidence.resource_release_allowed
    assert "resource_sha256" not in evidence.safe_claims

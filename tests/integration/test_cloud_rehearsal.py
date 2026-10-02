import json

import pytest

from scripts import cloud_rehearsal as rehearsal


def entry(**claims: str) -> dict[str, object]:
    return {
        "jsonPayload": {
            "MESSAGE": json.dumps(
                {
                    "status": "VERIFIED",
                    "live": True,
                    "safe_claims": {
                        "resource_sha256": rehearsal.SHA,
                        "image_digest": rehearsal.DIGEST,
                        "project_id": rehearsal.PROJECT,
                        "software": "CONFIDENTIAL_SPACE",
                        "zone": rehearsal.ZONE,
                        "protected_resource": "released",
                        **claims,
                    },
                }
            )
        }
    }


def test_rehearsal_requires_matching_live_release() -> None:
    evidence = rehearsal.release_evidence([entry()])
    assert evidence is not None and evidence.resource_release_allowed


@pytest.mark.parametrize(
    "claims",
    [
        {"resource_sha256": "incorrect"},
        {"image_digest": "wrong"},
        {"project_id": "other-project"},
        {"software": "GCE"},
        {"zone": "wrong-zone"},
    ],
)
def test_unexpected_cloud_evidence_is_rejected(claims: dict[str, str]) -> None:
    with pytest.raises(RuntimeError):
        rehearsal.release_evidence([entry(**claims)])


def test_missing_log_is_not_verification() -> None:
    assert rehearsal.release_evidence([{"jsonPayload": {"MESSAGE": "Boot completed"}}]) is None


def test_wrong_project_fails_before_cloud_access(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GCP_PROJECT", "other-project")
    monkeypatch.setenv("IMAGE_URI", rehearsal.IMAGE)
    with pytest.raises(RuntimeError, match="unexpected project"):
        rehearsal.preflight()


def test_cleanup_runs_when_verifier_poll_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(rehearsal, "preflight", lambda: None)
    monkeypatch.setattr(rehearsal.subprocess, "run", lambda *args, **kwargs: None)

    def cloud(*args: str) -> object:
        calls.append(args)
        if args[:3] == ("compute", "instances", "describe"):
            return {"id": "123"}
        if args[0] == "logging":
            raise RuntimeError("logging unavailable")
        return None

    monkeypatch.setattr(rehearsal, "cloud", cloud)
    with pytest.raises(RuntimeError, match="logging unavailable"):
        rehearsal.main()
    assert calls[-1] == (
        "compute",
        "instances",
        "delete",
        rehearsal.VM,
        f"--zone={rehearsal.ZONE}",
    )

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.demo_service import DemoService


def test_api_safe_poison_reset_flow(demo_service: DemoService) -> None:
    with TestClient(create_app(demo_service)) as client:
        state = client.get("/api/state")
        assert state.status_code == 200
        assert state.json()["attestation"]["status"] == "CACHED ATTESTATION EXAMPLE"

        safe = client.post(
            "/api/run",
            json={"request_id": "api_safe1", "explicit_user_confirmation": False},
        )
        assert safe.json()["decision"] == "ALLOW"

        assert client.post("/api/poison", json={}).json()["poisoned"] is True
        poisoned = client.post(
            "/api/run",
            json={"request_id": "api_bad01", "explicit_user_confirmation": False},
        )
        assert poisoned.json()["decision"] == "DENY"
        assert poisoned.json()["execution_result"] is None

        assert client.post("/api/reset", json={}).json()["poisoned"] is False


def test_api_rejects_extra_and_coerced_fields(demo_service: DemoService) -> None:
    with TestClient(create_app(demo_service)) as client:
        extra = client.post(
            "/api/run",
            json={
                "request_id": "api_extra",
                "explicit_user_confirmation": False,
                "policy_override": True,
            },
        )
        coerced = client.post(
            "/api/run",
            json={"request_id": "api_coerce", "explicit_user_confirmation": "true"},
        )
        assert extra.status_code == 422
        assert coerced.status_code == 422


def test_security_headers_are_present(demo_service: DemoService) -> None:
    with TestClient(create_app(demo_service)) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "default-src 'self'" in response.headers["content-security-policy"]
        assert response.headers["x-content-type-options"] == "nosniff"

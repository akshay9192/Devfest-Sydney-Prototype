from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from app.domain.models import Proposal
from app.services.demo_service import DemoService

pytestmark = pytest.mark.security


class MalformedProposer:
    model_identifier = "malformed-test"

    def __init__(self, payload: object) -> None:
        self.payload = payload

    def propose(self, *, playbook: str, scenario: str) -> Proposal:
        del playbook, scenario
        return Proposal.model_validate(self.payload)


@pytest.mark.parametrize(
    "payload",
    [
        "not-json",
        {},
        {
            "action": "DELETE_EVERYTHING",
            "sensitivity": "CONFIDENTIAL",
            "destination": "EXTERNAL",
            "user_confirmation": False,
            "destination_id": "synthetic-research-sink",
            "reason": "please",
        },
        {
            "action": "UPLOAD_EXTERNAL",
            "sensitivity": "CONFIDENTIAL",
            "destination": "EXTERNAL",
            "destination_id": "synthetic-research-sink",
            "reason": "missing confirmation",
        },
        {
            "action": "UPLOAD_EXTERNAL",
            "sensitivity": "CONFIDENTIAL",
            "destination": "EXTERNAL",
            "user_confirmation": False,
            "destination_id": "synthetic-research-sink",
            "reason": "extra field",
            "tool": "shell",
        },
    ],
)
def test_malformed_model_output_fails_closed(config_dir, payload: object) -> None:
    service = DemoService(
        config_dir=config_dir,
        proposer=MalformedProposer(payload),
        offline=True,
    )
    result = service.run(request_id="malform1", explicit_user_confirmation=False)
    assert result.decision == "DENY"
    assert service.executor_call_count == 0


def test_yaml_type_confusion_is_rejected(config_dir) -> None:
    policy = config_dir / "SYSTEM_POLICY.yaml"
    policy.write_text(
        """version: 1
allowed_actions: UPLOAD_EXTERNAL
external_destination_allowlist: synthetic-research-sink
confidential_external_requires_confirmation: yes
maximum_request_characters: 4096
""",
        encoding="utf-8",
    )
    service = DemoService(
        config_dir=config_dir,
        proposer=MalformedProposer({}),
        offline=True,
    )
    result = service.run(request_id="yamltype1", explicit_user_confirmation=False)
    assert result.decision == "DENY"
    assert service.executor_call_count == 0


def test_oversized_scenario_fails_closed(config_dir) -> None:
    policy = config_dir / "SYSTEM_POLICY.yaml"
    policy.write_text(policy.read_text(encoding="utf-8").replace("4096", "10"), encoding="utf-8")
    service = DemoService(
        config_dir=config_dir,
        proposer=MalformedProposer({}),
        offline=True,
    )
    result = service.run(request_id="oversize1", explicit_user_confirmation=False)
    assert result.decision == "DENY"
    assert "REQUEST_TOO_LARGE" in result.reason_codes


def test_log_injection_text_is_not_copied_to_receipt(config_dir) -> None:
    payload = {
        "action": "UPLOAD_EXTERNAL",
        "sensitivity": "CONFIDENTIAL",
        "destination": "EXTERNAL",
        "user_confirmation": False,
        "destination_id": "synthetic-research-sink",
        "reason": "ok\ncredential-like-value: fake-secret-value-12345",
    }
    service = DemoService(
        config_dir=config_dir,
        proposer=MalformedProposer(payload),
        offline=True,
    )
    receipt = service.run(
        request_id="loginject1",
        explicit_user_confirmation=False,
    ).receipt
    assert "Authorization" not in str(receipt)
    assert "fake-secret" not in str(receipt)


def test_concurrent_requests_do_not_share_request_state(demo_service: DemoService) -> None:
    request_ids = [f"concurrent{index:03}" for index in range(32)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(
                lambda item: demo_service.run(
                    request_id=item,
                    explicit_user_confirmation=False,
                ),
                request_ids,
            )
        )
    assert all(result.decision == "ALLOW" for result in results)
    assert demo_service.executor_call_count == len(request_ids)


def test_path_traversal_has_no_proposal_field() -> None:
    with pytest.raises(ValidationError):
        Proposal.model_validate(
            {
                "action": "SUMMARIZE_LOCALLY",
                "sensitivity": "CONFIDENTIAL",
                "destination": "LOCAL",
                "user_confirmation": False,
                "destination_id": "../../SYSTEM_POLICY.yaml",
                "reason": "try path",
                "path": "../../SYSTEM_POLICY.yaml",
            }
        )

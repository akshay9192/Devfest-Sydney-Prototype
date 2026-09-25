import pytest
from pydantic import ValidationError

from app.domain.models import Action, Destination, Proposal, Sensitivity


def valid_proposal_data() -> dict[str, object]:
    return {
        "action": "UPLOAD_EXTERNAL",
        "sensitivity": "CONFIDENTIAL",
        "destination": "EXTERNAL",
        "user_confirmation": False,
        "destination_id": "synthetic-research-sink",
        "reason": "Convenient",
    }


def test_proposal_accepts_only_declared_fields() -> None:
    data = valid_proposal_data() | {"policy_override": True}
    with pytest.raises(ValidationError):
        Proposal.model_validate(data)


@pytest.mark.parametrize("value", ["external", " external ", "External", "REMOTE"])
def test_destination_is_exact(value: str) -> None:
    data = valid_proposal_data() | {"destination": value}
    with pytest.raises(ValidationError):
        Proposal.model_validate(data)


def test_confirmation_rejects_string_coercion() -> None:
    data = valid_proposal_data() | {"user_confirmation": "true"}
    with pytest.raises(ValidationError):
        Proposal.model_validate(data)


def test_proposal_value_types_are_enums() -> None:
    proposal = Proposal.model_validate(valid_proposal_data())
    assert proposal.action is Action.UPLOAD_EXTERNAL
    assert proposal.sensitivity is Sensitivity.CONFIDENTIAL
    assert proposal.destination is Destination.EXTERNAL

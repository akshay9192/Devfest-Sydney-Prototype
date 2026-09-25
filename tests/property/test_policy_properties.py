from hypothesis import given
from hypothesis import strategies as st

from app.domain.models import Action, Destination, Proposal, Sensitivity
from app.domain.policies import SystemPolicy, ValidatedUserPolicy
from app.services.policy_engine import PolicyEngine

ENGINE = PolicyEngine(
    SystemPolicy(
        version=1,
        allowed_actions=frozenset(action.value for action in Action),
        external_destination_allowlist=frozenset({"synthetic-research-sink"}),
        confidential_external_requires_confirmation=True,
        maximum_request_characters=4096,
    ),
    ValidatedUserPolicy(version=1, deny_all_external=False),
)


@given(st.text(min_size=1, max_size=1_000))
def test_arbitrary_reason_cannot_bypass_confidential_external_rule(reason: str) -> None:
    proposal = Proposal(
        action=Action.UPLOAD_EXTERNAL,
        sensitivity=Sensitivity.CONFIDENTIAL,
        destination=Destination.EXTERNAL,
        user_confirmation=True,
        destination_id="synthetic-research-sink",
        reason=reason,
    )
    assert not ENGINE.evaluate(proposal, explicit_user_confirmation=False).allowed


@given(st.text(min_size=1, max_size=1_000), st.text(min_size=1, max_size=1_000))
def test_changing_reason_alone_cannot_change_decision(first: str, second: str) -> None:
    base = {
        "action": Action.UPLOAD_EXTERNAL,
        "sensitivity": Sensitivity.CONFIDENTIAL,
        "destination": Destination.EXTERNAL,
        "user_confirmation": False,
        "destination_id": "synthetic-research-sink",
    }
    one = ENGINE.evaluate(Proposal(**base, reason=first), explicit_user_confirmation=False)
    two = ENGINE.evaluate(Proposal(**base, reason=second), explicit_user_confirmation=False)
    assert one == two


@given(st.text(max_size=4_000))
def test_arbitrary_playbook_text_does_not_enter_policy_engine(playbook: str) -> None:
    del playbook
    proposal = Proposal(
        action=Action.SUMMARIZE_LOCALLY,
        sensitivity=Sensitivity.CONFIDENTIAL,
        destination=Destination.LOCAL,
        user_confirmation=False,
        destination_id="local-processor",
        reason="fixed",
    )
    assert ENGINE.evaluate(proposal, explicit_user_confirmation=False).allowed

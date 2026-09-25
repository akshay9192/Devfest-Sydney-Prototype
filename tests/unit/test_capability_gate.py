import pytest

from app.domain.models import Action, Decision, DecisionOutcome, Destination, Proposal, Sensitivity
from app.services.capability_gate import CapabilityDenied, CapabilityGate, SimulatedExecutor


def proposal(action: Action = Action.UPLOAD_EXTERNAL) -> Proposal:
    return Proposal(
        action=action,
        sensitivity=Sensitivity.CONFIDENTIAL,
        destination=Destination.EXTERNAL,
        user_confirmation=False,
        destination_id="synthetic-research-sink",
        reason="test",
    )


def decision(outcome: DecisionOutcome) -> Decision:
    return Decision(outcome=outcome, matched_rule_ids=("test",), reason_codes=("TEST",))


def test_denied_action_never_calls_executor() -> None:
    executor = SimulatedExecutor()
    gate = CapabilityGate(executor)
    with pytest.raises(CapabilityDenied):
        gate.execute(proposal(), decision(DecisionOutcome.DENY))
    assert executor.call_count == 0


def test_allowed_external_action_calls_simulated_executor_once() -> None:
    executor = SimulatedExecutor()
    result = CapabilityGate(executor).execute(proposal(), decision(DecisionOutcome.ALLOW))
    assert "Simulated upload" in result
    assert executor.call_count == 1


def test_unmapped_action_is_denied_even_with_allow_decision() -> None:
    executor = SimulatedExecutor()
    gate = CapabilityGate(executor)
    with pytest.raises(CapabilityDenied):
        gate.execute(proposal(Action.ASK_USER_CONFIRMATION), decision(DecisionOutcome.ALLOW))
    assert executor.call_count == 0

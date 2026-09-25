from pathlib import Path

import pytest

from app.domain.models import Action, AuthoritativeContext, Destination, Proposal, Sensitivity
from app.domain.policies import SystemPolicy, ValidatedUserPolicy
from app.services.policy_engine import (
    PolicyEngine,
    PolicyLoadError,
    load_system_policy,
    load_validated_user_policy,
)


def policies() -> tuple[SystemPolicy, ValidatedUserPolicy]:
    return (
        SystemPolicy(
            version=1,
            allowed_actions=frozenset(action.value for action in Action),
            external_destination_allowlist=frozenset({"synthetic-research-sink"}),
            confidential_external_requires_confirmation=True,
            maximum_request_characters=4096,
        ),
        ValidatedUserPolicy(version=1, deny_all_external=False),
    )


def proposal(
    *,
    action: Action = Action.UPLOAD_EXTERNAL,
    sensitivity: Sensitivity = Sensitivity.CONFIDENTIAL,
    destination: Destination = Destination.EXTERNAL,
    destination_id: str = "synthetic-research-sink",
    claimed_confirmation: bool = False,
    reason: str = "test",
) -> Proposal:
    return Proposal(
        action=action,
        sensitivity=sensitivity,
        destination=destination,
        user_confirmation=claimed_confirmation,
        destination_id=destination_id,
        reason=reason,
    )


def context(
    *, confirmed: bool = False, sensitivity: Sensitivity = Sensitivity.CONFIDENTIAL
) -> AuthoritativeContext:
    return AuthoritativeContext(
        sensitivity=sensitivity,
        explicit_user_confirmation=confirmed,
    )


def test_confidential_external_without_authoritative_confirmation_is_denied() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(proposal(), context())
    assert not result.allowed
    assert result.reason_codes == ("EXPLICIT_CONFIRMATION_REQUIRED",)


def test_model_claim_cannot_substitute_for_authoritative_confirmation() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(
        proposal(claimed_confirmation=True),
        context(),
    )
    assert not result.allowed


def test_confirmed_allowlisted_external_simulation_is_allowed() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(proposal(), context(confirmed=True))
    assert result.allowed


def test_non_allowlisted_destination_is_denied_even_with_confirmation() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(
        proposal(destination_id="attacker.invalid"),
        context(confirmed=True),
    )
    assert not result.allowed
    assert "DESTINATION_NOT_ALLOWLISTED" in result.reason_codes


def test_local_summary_is_allowed() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(
        proposal(
            action=Action.SUMMARIZE_LOCALLY,
            destination=Destination.LOCAL,
            destination_id="local-processor",
        ),
        context(),
    )
    assert result.allowed


def test_action_destination_mismatch_is_denied() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(
        proposal(action=Action.SUMMARIZE_LOCALLY, destination=Destination.EXTERNAL),
        context(),
    )
    assert not result.allowed


def test_ask_confirmation_is_not_an_executable_capability() -> None:
    engine = PolicyEngine(*policies())
    result = engine.evaluate(
        proposal(action=Action.ASK_USER_CONFIRMATION, destination=Destination.LOCAL),
        context(),
    )
    assert not result.allowed


def test_validated_user_policy_can_narrow_external_access() -> None:
    system, _ = policies()
    engine = PolicyEngine(system, ValidatedUserPolicy(version=1, deny_all_external=True))
    assert not engine.evaluate(proposal(), context(confirmed=True)).allowed


def test_action_removed_from_policy_is_denied() -> None:
    system, user = policies()
    restricted = system.model_copy(update={"allowed_actions": frozenset({"SUMMARIZE_LOCALLY"})})
    result = PolicyEngine(restricted, user).evaluate(
        proposal(),
        context(confirmed=True),
    )
    assert not result.allowed


def test_model_cannot_downgrade_authoritative_confidential_sensitivity() -> None:
    result = PolicyEngine(*policies()).evaluate(
        proposal(sensitivity=Sensitivity.PUBLIC, claimed_confirmation=True),
        context(sensitivity=Sensitivity.CONFIDENTIAL),
    )
    assert not result.allowed
    assert result.reason_codes == ("EXPLICIT_CONFIRMATION_REQUIRED",)


@pytest.mark.parametrize("content", ["[not, a, mapping]", "version: [", "version: true"])
def test_malformed_or_invalid_system_policy_fails_closed(tmp_path: Path, content: str) -> None:
    path = tmp_path / "SYSTEM_POLICY.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(PolicyLoadError):
        load_system_policy(path)


def test_missing_policy_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(PolicyLoadError):
        load_system_policy(tmp_path / "missing.yaml")


def test_policy_files_load(config_dir: Path) -> None:
    assert load_system_policy(config_dir / "SYSTEM_POLICY.yaml").version == 1
    assert load_validated_user_policy(config_dir / "VALIDATED_USER_POLICY.yaml").version == 1

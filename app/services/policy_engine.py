from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.domain.models import Action, Decision, DecisionOutcome, Destination, Proposal, Sensitivity
from app.domain.policies import SystemPolicy, ValidatedUserPolicy


class PolicyLoadError(RuntimeError):
    """Raised when authoritative policy cannot be loaded exactly."""


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise PolicyLoadError(f"Unable to load authoritative policy: {path.name}") from exc
    if not isinstance(loaded, dict):
        raise PolicyLoadError(f"Policy must be a mapping: {path.name}")
    return loaded


def load_system_policy(path: Path) -> SystemPolicy:
    try:
        return SystemPolicy.model_validate(_load_yaml_mapping(path))
    except ValidationError as exc:
        raise PolicyLoadError("System policy schema validation failed") from exc


def load_validated_user_policy(path: Path) -> ValidatedUserPolicy:
    try:
        return ValidatedUserPolicy.model_validate(_load_yaml_mapping(path))
    except ValidationError as exc:
        raise PolicyLoadError("Validated user policy schema validation failed") from exc


def deny(*reason_codes: str, rule: str = "fail_closed") -> Decision:
    return Decision(
        outcome=DecisionOutcome.DENY,
        matched_rule_ids=(rule,),
        reason_codes=tuple(reason_codes),
    )


class PolicyEngine:
    def __init__(self, system: SystemPolicy, user: ValidatedUserPolicy) -> None:
        self._system = system
        self._user = user

    def evaluate(self, proposal: Proposal, *, explicit_user_confirmation: bool) -> Decision:
        try:
            return self._evaluate(proposal, explicit_user_confirmation=explicit_user_confirmation)
        except Exception:
            return deny("POLICY_EVALUATION_ERROR")

    def _evaluate(self, proposal: Proposal, *, explicit_user_confirmation: bool) -> Decision:
        if proposal.action.value not in self._system.allowed_actions:
            return deny("ACTION_NOT_ALLOWLISTED", rule="system.allowed_actions")

        if proposal.action is Action.SUMMARIZE_LOCALLY:
            if proposal.destination is not Destination.LOCAL:
                return deny("ACTION_DESTINATION_MISMATCH", rule="system.action_destination")
            return Decision(
                outcome=DecisionOutcome.ALLOW,
                matched_rule_ids=("system.local_summary",),
                reason_codes=("LOCAL_PROCESSING",),
            )

        if proposal.action is Action.ASK_USER_CONFIRMATION:
            return deny("USER_CONFIRMATION_REQUIRED", rule="system.confirmation")

        if (
            proposal.action is not Action.UPLOAD_EXTERNAL
            or proposal.destination is not Destination.EXTERNAL
        ):
            return deny("ACTION_DESTINATION_MISMATCH", rule="system.action_destination")

        if self._user.deny_all_external:
            return deny("USER_POLICY_DENIES_EXTERNAL", rule="user.deny_all_external")

        if proposal.destination_id not in self._system.external_destination_allowlist:
            return deny("DESTINATION_NOT_ALLOWLISTED", rule="system.external_allowlist")

        confirmation_required = (
            self._system.confidential_external_requires_confirmation
            and proposal.sensitivity is Sensitivity.CONFIDENTIAL
        )
        if confirmation_required and not explicit_user_confirmation:
            return deny("EXPLICIT_CONFIRMATION_REQUIRED", rule="system.confidential_external")

        return Decision(
            outcome=DecisionOutcome.ALLOW,
            matched_rule_ids=("system.external_allowlist", "system.confidential_external"),
            reason_codes=("AUTHORIZED_EXTERNAL_SIMULATION",),
        )

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr


class Sensitivity(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"


class Destination(StrEnum):
    LOCAL = "LOCAL"
    EXTERNAL = "EXTERNAL"


class Action(StrEnum):
    SUMMARIZE_LOCALLY = "SUMMARIZE_LOCALLY"
    UPLOAD_EXTERNAL = "UPLOAD_EXTERNAL"
    ASK_USER_CONFIRMATION = "ASK_USER_CONFIRMATION"


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Action
    sensitivity: Sensitivity
    destination: Destination
    user_confirmation: StrictBool
    destination_id: StrictStr = Field(min_length=1, max_length=128)
    reason: StrictStr = Field(min_length=1, max_length=1_000)


class AuthoritativeContext(BaseModel):
    """Facts supplied by the application, never inferred from model output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    sensitivity: Sensitivity
    explicit_user_confirmation: StrictBool


class DecisionOutcome(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: DecisionOutcome
    matched_rule_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    human_explanation: str = "Policy evaluated deterministically."

    @property
    def allowed(self) -> bool:
        return self.outcome is DecisionOutcome.ALLOW


class AttestationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    CACHED_DEMO_EVIDENCE = "CACHED ATTESTATION EXAMPLE"
    LOCAL_DEMO = "LOCAL DEMO"
    FAILED = "FAILED"


class AttestationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: AttestationStatus
    workload_identity: str | None = None
    safe_claims: dict[str, str] = Field(default_factory=dict)
    live: bool = False

    @property
    def resource_release_allowed(self) -> bool:
        return self.live and self.status is AttestationStatus.VERIFIED

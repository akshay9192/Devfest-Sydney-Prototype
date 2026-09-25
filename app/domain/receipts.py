from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class DecisionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    receipt_version: str
    request_id: str
    timestamp: str
    playbook_sha256: str
    system_policy_sha256: str
    validated_user_policy_sha256: str
    model_identifier: str
    proposal: dict[str, Any] | None
    decision: str
    matched_rule_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    attestation_status: str
    workload_identity: str | None
    safe_attestation_claims: dict[str, str]
    signing: str

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from app.domain.models import AttestationEvidence, Decision, Proposal
from app.domain.receipts import DecisionReceipt


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65_536), b""):
            digest.update(block)
    return digest.hexdigest()


def _proposal_receipt(proposal: Proposal | None) -> dict[str, object] | None:
    if proposal is None:
        return None
    return {
        "action": proposal.action.value,
        "sensitivity": proposal.sensitivity.value,
        "destination": proposal.destination.value,
        "user_confirmation_claimed_by_model": proposal.user_confirmation,
        "destination_id": proposal.destination_id,
        "reason_sha256": hashlib.sha256(proposal.reason.encode("utf-8")).hexdigest(),
    }


class ReceiptService:
    def create(
        self,
        *,
        request_id: str,
        playbook_path: Path,
        system_policy_path: Path,
        user_policy_path: Path,
        model_identifier: str,
        proposal: Proposal | None,
        decision: Decision,
        attestation: AttestationEvidence,
    ) -> DecisionReceipt:
        return DecisionReceipt(
            receipt_version="1",
            request_id=request_id,
            timestamp=datetime.now(UTC).isoformat(),
            playbook_sha256=sha256_file(playbook_path),
            system_policy_sha256=sha256_file(system_policy_path),
            validated_user_policy_sha256=sha256_file(user_policy_path),
            model_identifier=model_identifier,
            proposal=_proposal_receipt(proposal),
            decision=decision.outcome.value,
            matched_rule_ids=decision.matched_rule_ids,
            reason_codes=decision.reason_codes,
            attestation_status=attestation.status.value,
            workload_identity=attestation.workload_identity,
            safe_attestation_claims=attestation.safe_claims,
            signing="UNSIGNED DEMO RECEIPT",
        )

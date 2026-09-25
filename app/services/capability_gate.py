from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from app.domain.models import Action, Decision, Proposal


class Executor(Protocol):
    def summarize_local(self) -> str: ...

    def simulated_external_upload(self, destination_id: str) -> str: ...


@dataclass
class SimulatedExecutor:
    call_count: int = 0

    def summarize_local(self) -> str:
        self.call_count += 1
        return "Synthetic research document summarized locally."

    def simulated_external_upload(self, destination_id: str) -> str:
        self.call_count += 1
        return f"Simulated upload to allowlisted destination: {destination_id}"


class CapabilityDenied(RuntimeError):
    pass


class CapabilityGate:
    def __init__(self, executor: Executor) -> None:
        self._executor = executor
        self._capabilities: dict[Action, Callable[[Proposal], str]] = {
            Action.SUMMARIZE_LOCALLY: lambda _: self._executor.summarize_local(),
            Action.UPLOAD_EXTERNAL: lambda proposal: self._executor.simulated_external_upload(
                proposal.destination_id
            ),
        }

    def execute(self, proposal: Proposal, decision: Decision) -> str:
        if not decision.allowed:
            raise CapabilityDenied("Denied decisions cannot invoke an executor")
        capability = self._capabilities.get(proposal.action)
        if capability is None:
            raise CapabilityDenied("Capability is not allowlisted")
        return capability(proposal)

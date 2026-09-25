from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.domain.models import Action, Destination, Proposal, Sensitivity
from app.services.proposer import RealGeminiProposer


def test_real_proposer_uses_enterprise_v1_and_structured_output(monkeypatch: Any) -> None:
    expected = Proposal(
        action=Action.SUMMARIZE_LOCALLY,
        sensitivity=Sensitivity.CONFIDENTIAL,
        destination=Destination.LOCAL,
        user_confirmation=False,
        destination_id="local-processor",
        reason="Keep the synthetic confidential note local.",
    )
    captured: dict[str, Any] = {}

    class FakeModels:
        def generate_content(self, **kwargs: Any) -> SimpleNamespace:
            captured["generate"] = kwargs
            return SimpleNamespace(parsed=expected)

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client"] = kwargs
            self.models = FakeModels()

    monkeypatch.setattr("google.genai.Client", FakeClient)
    monkeypatch.setenv("GEMINI_TIMEOUT_MS", "1234")

    proposal = RealGeminiProposer(model_identifier="gemini-3.5-flash").propose(
        playbook="Prefer local processing.",
        scenario="Synthetic confidential note.",
    )

    assert proposal == expected
    assert captured["client"]["enterprise"] is True
    assert captured["client"]["http_options"].api_version == "v1"
    assert captured["client"]["http_options"].timeout == 1234
    assert captured["generate"]["model"] == "gemini-3.5-flash"
    assert captured["generate"]["config"].response_schema is Proposal

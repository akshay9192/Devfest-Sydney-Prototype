from app.services.capability_gate import SimulatedExecutor
from app.services.demo_service import DemoService
from app.services.proposer import DeterministicFakeProposer


class UnavailableProposer:
    model_identifier = "unavailable-live-model"

    def propose(self, *, playbook: str, scenario: str):
        del playbook, scenario
        raise TimeoutError("synthetic timeout")


class FailingExecutor(SimulatedExecutor):
    def summarize_local(self) -> str:
        raise RuntimeError("synthetic executor failure")


def test_safe_then_poisoned_flow_enforces_boundary(demo_service: DemoService) -> None:
    safe = demo_service.run(request_id="safe0001", explicit_user_confirmation=False)
    assert safe.proposal is not None
    assert safe.proposal.action.value == "SUMMARIZE_LOCALLY"
    assert safe.decision == "ALLOW"
    assert demo_service.executor_call_count == 1

    policy_hash_before = demo_service.state()["system_policy_sha256"]
    demo_service.poison()
    policy_hash_after = demo_service.state()["system_policy_sha256"]
    poisoned = demo_service.run(request_id="poison01", explicit_user_confirmation=False)

    assert policy_hash_after == policy_hash_before
    assert poisoned.proposal is not None
    assert poisoned.proposal.action.value == "UPLOAD_EXTERNAL"
    assert poisoned.decision == "DENY"
    assert poisoned.execution_result is None
    assert demo_service.executor_call_count == 1


def test_explicit_confirmation_allows_simulated_upload_once(demo_service: DemoService) -> None:
    demo_service.poison()
    result = demo_service.run(request_id="confirm1", explicit_user_confirmation=True)
    assert result.decision == "ALLOW"
    assert "Simulated upload" in (result.execution_result or "")
    assert demo_service.executor_call_count == 1


def test_replayed_request_is_denied_without_second_execution(demo_service: DemoService) -> None:
    first = demo_service.run(request_id="replay01", explicit_user_confirmation=False)
    second = demo_service.run(request_id="replay01", explicit_user_confirmation=False)
    assert first.decision == "ALLOW"
    assert second.decision == "DENY"
    assert "REPLAYED_REQUEST" in second.reason_codes
    assert demo_service.executor_call_count == 1


def test_candidate_rules_cannot_change_system_policy(demo_service: DemoService, config_dir) -> None:
    (config_dir / "CANDIDATE_RULES.yaml").write_text(
        "version: 1\nstatus: candidate\nrules:\n  - allow_all_external: true\n",
        encoding="utf-8",
    )
    demo_service.poison()
    result = demo_service.run(request_id="candidate1", explicit_user_confirmation=False)
    assert result.decision == "DENY"


def test_corrupt_policy_denies_and_never_executes(demo_service: DemoService, config_dir) -> None:
    (config_dir / "SYSTEM_POLICY.yaml").write_text("version: [", encoding="utf-8")
    result = demo_service.run(request_id="corrupt01", explicit_user_confirmation=False)
    assert result.decision == "DENY"
    assert demo_service.executor_call_count == 0


def test_reset_restores_all_mutable_demo_state(demo_service: DemoService, config_dir) -> None:
    demo_service.run(request_id="before_reset", explicit_user_confirmation=False)
    demo_service.poison()
    (config_dir / "CANDIDATE_RULES.yaml").write_text(
        "version: 1\nstatus: candidate\nrules:\n  - unsafe: true\n", encoding="utf-8"
    )

    state = demo_service.reset()

    assert state["poisoned"] is False
    assert state["executor_call_count"] == 0
    assert (config_dir / "CANDIDATE_RULES.yaml").read_text(encoding="utf-8") == (
        "version: 1\nstatus: candidate\nrules: []\n"
    )
    repeated = demo_service.run(request_id="before_reset", explicit_user_confirmation=False)
    assert repeated.decision == "ALLOW"


def test_live_model_failure_uses_disclosed_fallback_and_real_policy(config_dir) -> None:
    service = DemoService(
        config_dir=config_dir,
        proposer=UnavailableProposer(),
        fallback_proposer=DeterministicFakeProposer(),
        offline=False,
    )
    result = service.run(request_id="fallback1", explicit_user_confirmation=False)
    assert result.decision == "ALLOW"
    assert "MODEL_FALLBACK" in result.events
    assert result.proposal_error == "LIVE MODEL UNAVAILABLE: TimeoutError"


def test_executor_failure_returns_fail_closed_result(config_dir) -> None:
    service = DemoService(
        config_dir=config_dir,
        proposer=DeterministicFakeProposer(),
        offline=True,
        executor=FailingExecutor(),
    )
    result = service.run(request_id="execfail1", explicit_user_confirmation=False)
    assert result.decision == "DENY"
    assert result.execution_result is None
    assert result.reason_codes == ("EXECUTOR_UNAVAILABLE",)
    assert service.executor_call_count == 0


def test_structured_log_contains_metadata_but_not_model_reason(
    demo_service: DemoService, caplog
) -> None:
    secret_marker = "document-content-must-not-appear"
    with caplog.at_level("INFO", logger="devfest.decision"):
        result = demo_service.run(
            request_id="logging01",
            explicit_user_confirmation=False,
        )
    log = caplog.records[-1].message
    assert '"request_id": "logging01"' in log
    assert '"decision": "ALLOW"' in log
    assert "policy_hash" in log
    assert secret_marker not in log
    assert result.proposal is not None
    assert result.proposal.reason not in log
    assert result.receipt["runtime_mode"] == "offline_demo"


def test_offline_flow_does_not_open_a_network_connection(
    demo_service: DemoService, monkeypatch
) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("offline mode attempted a network connection")

    monkeypatch.setattr("socket.create_connection", reject_network)
    assert demo_service.state()["attestation"]["status"] == "CACHED ATTESTATION EXAMPLE"
    assert (
        demo_service.run(request_id="offline01", explicit_user_confirmation=False).decision
        == "ALLOW"
    )

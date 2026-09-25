from app.services.demo_service import DemoService


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

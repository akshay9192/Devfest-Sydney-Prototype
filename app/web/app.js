const elements = {
  announcement: document.querySelector("#announcement"),
  attestation: document.querySelector("#attestation-status"),
  decision: document.querySelector("#decision"),
  decisionReason: document.querySelector("#decision-reason"),
  execution: document.querySelector("#execution-result"),
  modelId: document.querySelector("#model-id"),
  playbook: document.querySelector("#playbook-text"),
  playbookState: document.querySelector("#playbook-state"),
  policyHash: document.querySelector("#policy-hash"),
  proposalAction: document.querySelector("#proposal-action"),
  proposalConfirmation: document.querySelector("#proposal-confirmation"),
  proposalDestination: document.querySelector("#proposal-destination"),
  proposalReason: document.querySelector("#proposal-reason"),
  receipt: document.querySelector("#receipt"),
  resource: document.querySelector("#resource-status"),
};

function requestId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID().replaceAll("-", "");
  }
  return `request_${Date.now()}_${Math.floor(Math.random() * 100000)}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

function renderState(state) {
  elements.playbook.textContent = state.playbook;
  elements.playbookState.textContent = state.poisoned
    ? "Playbook changed — authority unchanged"
    : "Original guidance";
  elements.playbookState.classList.toggle("poisoned", state.poisoned);
  elements.modelId.textContent = state.model_identifier;
  elements.policyHash.textContent = `Policy hash: ${state.system_policy_sha256.slice(0, 16)}…`;
  elements.attestation.textContent = state.attestation.status;
  elements.resource.textContent = state.attestation.live ? "Release eligible" : "Not released";
}

function renderRun(result) {
  const proposal = result.proposal;
  elements.proposalAction.textContent = proposal?.action ?? "Invalid proposal";
  elements.proposalDestination.textContent = proposal?.destination ?? "Unknown";
  elements.proposalConfirmation.textContent = proposal
    ? String(proposal.user_confirmation)
    : "Not accepted";
  elements.proposalReason.textContent = proposal?.reason ?? result.proposal_error ?? "Proposal rejected";

  elements.decision.textContent = result.decision;
  elements.decision.className = `decision ${result.decision.toLowerCase()}`;
  elements.decisionReason.textContent = result.reason_codes.join(" · ");
  elements.execution.textContent = result.execution_result ?? "No executor invoked.";
  elements.receipt.textContent = JSON.stringify(result.receipt, null, 2);
  elements.announcement.textContent = result.decision === "DENY"
    ? "Proposal denied. The executor was not called."
    : "Proposal allowed through the capability gate.";
}

async function withBusy(button, operation) {
  const controls = document.querySelectorAll("button");
  controls.forEach((control) => { control.disabled = true; });
  elements.announcement.textContent = `${button.textContent}…`;
  try {
    await operation();
  } catch (error) {
    elements.announcement.textContent = `Demo error: ${error.message}`;
  } finally {
    controls.forEach((control) => { control.disabled = false; });
    button.focus();
  }
}

async function runScenario(button) {
  await withBusy(button, async () => {
    const result = await api("/api/run", {
      method: "POST",
      body: JSON.stringify({
        request_id: requestId(),
        explicit_user_confirmation: false,
      }),
    });
    renderRun(result);
  });
}

document.querySelector("#run-safe").addEventListener("click", (event) => runScenario(event.currentTarget));
document.querySelector("#run-again").addEventListener("click", (event) => runScenario(event.currentTarget));
document.querySelector("#poison").addEventListener("click", (event) => withBusy(event.currentTarget, async () => {
  renderState(await api("/api/poison", { method: "POST", body: "{}" }));
  elements.announcement.textContent = "Advisory playbook poisoned. System policy did not change.";
}));
document.querySelector("#reset").addEventListener("click", (event) => withBusy(event.currentTarget, async () => {
  renderState(await api("/api/reset", { method: "POST", body: "{}" }));
  elements.decision.textContent = "Waiting";
  elements.decision.className = "decision waiting";
  elements.receipt.textContent = "No decision yet.";
  elements.announcement.textContent = "Demo reset.";
}));

api("/api/state").then(renderState).catch((error) => {
  elements.announcement.textContent = `Unable to load demo: ${error.message}`;
});

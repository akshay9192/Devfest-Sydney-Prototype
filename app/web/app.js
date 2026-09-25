"use strict";

const ids = [
  "announcement", "attestation-status", "capability-state", "decision",
  "decision-reason", "execution-result", "last-event", "mode-label", "model-id",
  "playbook-text", "playbook-state", "policy-hash", "proposal-action",
  "proposal-confirmation", "proposal-destination", "proposal-reason", "receipt",
  "resource-status",
];
const elements = Object.fromEntries(ids.map((id) => [id, document.querySelector(`#${id}`)]));
const controls = {
  safe: document.querySelector("#run-safe"), poison: document.querySelector("#poison"),
  rerun: document.querySelector("#run-again"), reset: document.querySelector("#reset"),
};

function requestId() {
  return globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID().replaceAll("-", "")
    : `request_${Date.now()}_${Math.floor(Math.random() * 100000)}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function renderState(state) {
  elements["playbook-text"].textContent = state.playbook;
  elements["playbook-text"].scrollTop = state.poisoned
    ? elements["playbook-text"].scrollHeight
    : 0;
  elements["playbook-state"].textContent = state.poisoned ? "Playbook poisoned" : "Original guidance";
  elements["playbook-state"].classList.toggle("poisoned", state.poisoned);
  document.body.classList.toggle("is-poisoned", state.poisoned);
  elements["model-id"].textContent = state.model_identifier;
  elements["mode-label"].textContent = state.model_identifier.startsWith("deterministic")
    ? "Rehearsal mode / recorded proposal" : "Live model mode";
  elements["policy-hash"].textContent = `Policy ${state.system_policy_sha256.slice(0, 12)}…`;
  elements["attestation-status"].textContent = state.attestation.status;
  elements["resource-status"].textContent = state.attestation.live ? "Release eligible" : "Not released";
}

function humanEvent(event) {
  return event.toLowerCase().replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

function renderRun(result) {
  const proposal = result.proposal;
  elements["proposal-action"].textContent = proposal?.action ?? "Invalid proposal";
  elements["proposal-destination"].textContent = proposal?.destination ?? "Unknown";
  elements["proposal-confirmation"].textContent = proposal ? String(proposal.user_confirmation) : "Not accepted";
  elements["proposal-reason"].textContent = proposal?.reason ?? result.proposal_error;
  elements.decision.textContent = result.decision;
  elements.decision.className = `decision ${result.decision.toLowerCase()}`;
  elements["decision-reason"].textContent = result.human_explanation;
  elements["execution-result"].textContent = result.execution_result ?? "No executor invoked.";
  elements.receipt.textContent = JSON.stringify(result.receipt, null, 2);
  const events = new Set(result.events);
  const granted = events.has("CAPABILITY_GRANTED");
  elements["capability-state"].className = `capability-state ${granted ? "available" : "locked"}`;
  elements["capability-state"].querySelector(".lock-mark").textContent = granted ? "✓" : "×";
  elements["capability-state"].querySelector("strong").textContent = granted ? "Granted" : "Locked";
  elements["last-event"].textContent = humanEvent(result.events.at(-1));
  document.body.classList.toggle("is-denied", result.decision === "DENY");
  document.body.classList.toggle("is-allowed", result.decision === "ALLOW");
  elements.announcement.textContent = events.has("MODEL_FALLBACK")
    ? "Live model unavailable. Using recorded proposal. Policy remained live."
    : result.decision === "DENY"
      ? "Action denied. The executor was not called."
      : "Action authorized and executed exactly once.";
}

function renderError(error) {
  elements.announcement.textContent = `System failed closed (${error.message}). No action was executed.`;
  elements.decision.textContent = "DENY";
  elements.decision.className = "decision deny";
  elements["decision-reason"].textContent = "DEPENDENCY_UNAVAILABLE";
  elements["execution-result"].textContent = "No executor invoked.";
  elements["capability-state"].className = "capability-state locked";
}

async function withBusy(button, operation) {
  Object.values(controls).forEach((control) => { control.disabled = true; });
  elements.announcement.textContent = `${button.textContent.trim()}…`;
  try { await operation(); } catch (error) { renderError(error); }
  finally {
    Object.values(controls).forEach((control) => { control.disabled = false; });
    button.focus();
  }
}

async function runScenario(button) {
  await withBusy(button, async () => renderRun(await api("/api/run", {
    method: "POST",
    body: JSON.stringify({ request_id: requestId(), explicit_user_confirmation: false }),
  })));
}

controls.safe.addEventListener("click", () => runScenario(controls.safe));
controls.rerun.addEventListener("click", () => runScenario(controls.rerun));
controls.poison.addEventListener("click", () => withBusy(controls.poison, async () => {
  renderState(await api("/api/poison", { method: "POST", body: "{}" }));
  elements.announcement.textContent = "Model guidance changed. System authority did not.";
}));
controls.reset.addEventListener("click", () => withBusy(controls.reset, async () => {
  renderState(await api("/api/reset", { method: "POST", body: "{}" }));
  elements.decision.textContent = "Waiting";
  elements.decision.className = "decision waiting";
  elements["proposal-action"].textContent = "No proposal";
  elements["capability-state"].className = "capability-state locked";
  elements["capability-state"].querySelector(".lock-mark").textContent = "×";
  elements["capability-state"].querySelector("strong").textContent = "Locked";
  elements.receipt.textContent = "No decision yet.";
  elements["last-event"].textContent = "System reset";
  document.body.classList.remove("is-denied", "is-allowed");
  elements.announcement.textContent = "Demo reset to its known safe state.";
}));

document.addEventListener("keydown", (event) => {
  if (event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
  const shortcut = { "1": controls.safe, "2": controls.poison, "3": controls.rerun, r: controls.reset }[event.key.toLowerCase()];
  if (shortcut && !shortcut.disabled) { event.preventDefault(); shortcut.click(); }
});

api("/api/state").then(renderState).catch(renderError);

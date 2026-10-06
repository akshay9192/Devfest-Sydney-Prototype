# Demo runbook

## Before the room opens

1. Disconnect or disable networking.
2. Start `python scripts/run_demo.py --mode offline_demo` (or `make demo-offline`).
3. Open `http://127.0.0.1:8000`, reset the demo, and confirm the page says
   `CACHED ATTESTATION EXAMPLE` and `Not released`.
4. Complete one rehearsal and reset again. Keep
   `artifacts/e2e/demo-poisoned.png` available as the visual fallback.

## Timed technical flow

| Time | Action | Expected observation |
|---|---|---|
| T+0:00 | Show the normal playbook | Advisory status is visible |
| T+0:10 | Select **Run scenario** | Fake proposer chooses `SUMMARIZE_LOCALLY` |
| T+0:20 | Point to the controller result | `ALLOW`; local executor runs |
| T+0:30 | Select **Poison playbook** | Playbook visibly changes; policy hash does not |
| T+0:40 | Select **Run again** | Proposal changes to `UPLOAD_EXTERNAL` |
| T+0:50 | Point to the result | `DENY`; no executor invoked |
| T+1:00 | Point to confidential runtime | Cached evidence is labeled; resource is not released |

The interaction takes about 65 seconds at a measured speaking pace. Do not attempt a
live cloud deployment during the lightning talk.

## Recovery

- If the browser is stale, refresh; process state and policy remain intact.
- If a click is missed, use Tab and Enter; all controls are native buttons.
- If the process stops, restart offline mode and select Reset.
- If the local machine fails, show the captured screenshot and narrate that it is a
  recorded local result.

## Verified keyboard controls

`1` runs the scenario; `2` poisons the playbook; `3` runs it again; `R` resets.
These controls are implemented in `app/web/app.js` and exercised by browser tests.
Both run controls use the current playbook: press `R` before `1` if a previous
rehearsal left it poisoned.

The unsafe proposal is deterministic/recorded. The user reports that five prior
live Gemini poisoned trials all proposed `SUMMARIZE_LOCALLY`: zero unsafe proposals
and zero unsafe authorizations. Do not narrate the recorded unsafe proposal as a
live Gemini observation. Show cloud evidence separately only once captured; the
offline cached fixture is not that evidence.

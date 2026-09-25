# Rehearsal report

## Current local rehearsal

The offline safe → reset → poison → deny → reset → safe sequence passed 10/10
consecutive cycles. The slowest controller-only cycle was under 20 ms. The stage
runbook allocates 65 seconds to the interactive sequence, below the 70-second gate.
The browser path was exercised at 1440×900, 1920×1080, and 390×844 with no console
errors or horizontal overflow.

The reviewed screenshot set is generated under `artifacts/e2e/` during the browser
run and is intentionally ignored from Git; the source UI and test recreate it.

| Path | Current evidence | Fallback |
|---|---|---|
| Live success | Not rehearsed; credentials unavailable | Switch to rehearsal mode before speaking |
| No Wi-Fi | Offline proposer and cached evidence; real controller/gate | Primary stage path |
| Gemini failure | Integration test shows disclosed recorded proposal and live policy | UI says live model unavailable |
| GCP failure | Cached evidence is labeled and protected resource stays unreleased | Explain attestation from the documented receipt |

Manual interactions: four keys (`1`, `2`, `3`, `R`). The highest-risk stage
dependencies are live Gemini and cloud evidence, both of which have explicit labels
and an offline path. A human-timed live rehearsal remains blocked until Gemini and
GCP credentials are configured.

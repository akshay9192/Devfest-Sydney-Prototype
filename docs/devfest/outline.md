# DevFest Sydney 2026 lightning talk

Five slides, 16:9, architecture-first, with no live-demo dependency.

## Slide 1: Your AI assistant shouldn't trust you.

- Role: provocative opening
- Point: prompts influence behaviour but do not define authority
- Visual: typography only; no diagram or image

## Slide 2: The model can suggest. Software decides.

- Role: architecture
- Point: user input, playbook, Gemini, and the typed proposal are untrusted
- Point: authoritative state and policy are evaluated below an explicit boundary
- Point: the capability gate controls the fixed executor set
- Visual: one top-to-bottom flow with an authority-boundary rule

## Slide 3: Bad guidance can change the proposal.

- Role: controlled attack example
- Point: an untrusted playbook prefers external analysis
- Point: the deterministic adversarial proposer returns `UPLOAD_EXTERNAL`
- Visual: playbook statement flowing to a model proposal; no policy result yet

## Slide 4: But the model doesn't own authority.

- Role: visual climax
- Point: authoritative confidential state plus no confirmation produces `DENY`
- Point: a deny decision leaves the capability locked and the executor uncalled
- Visual: large `DENY` with a minimal vertical flow

## Slide 5: The model changed its mind. The security boundary didn't.

- Role: conclusion and repository handoff
- Point: policy decides whether an action may happen
- Point: attestation decides which workload may receive protected state
- Point: Gemini remains remote; this checkout contains design and local evidence, not current live attestation
- Visual: conclusion, repository QR, and the deterministic-boundaries takeaway

No external source images are required. The repository QR is a strict local asset on
Slide 5.

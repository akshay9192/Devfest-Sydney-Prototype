---
name: karpathy-guidelines
description: Guide material code changes in this repository with explicit assumptions, minimal solutions, surgical scope, and a verification step for each phase.
---

# Karpathy Guidelines

Think before coding. Surface assumptions, distinguish plausible interpretations,
prefer the simpler one, and name uncertainty that affects correctness.

Implement the minimum code that solves the demonstrated problem. Avoid speculative
architecture, unused flexibility, and abstractions that are longer than the logic
they contain.

Keep changes surgical. Touch only code required by the task, preserve unrelated
work, and remove only dead code introduced by the current change.

Give every phase an observable verification:

- Verify policy changes with adversarial invariant tests.
- Verify model integration by proving malformed output cannot reach execution.
- Verify confidential deployment with real attestation evidence and both allowed
  and denied protected-resource access.

When verification fails, find the root cause, add or improve a regression test, and
fix the cause rather than weakening the assertion.

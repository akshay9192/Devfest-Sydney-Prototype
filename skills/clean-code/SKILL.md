---
name: clean-code
description: Guide Python and web changes in this repository toward simple, understandable, maintainable code with explicit external boundaries and readable behavioral tests.
---

# Clean Code

Follow the language's standard conventions and keep the design simple. Put
configuration near composition roots, inject external services, keep dependencies
obvious, and prefer composition over class hierarchies. Avoid configurability that
the product does not need.

Use consistent, descriptive, searchable names. Replace ambiguous primitives with
small value objects when they protect a boundary. Keep variables close to use and
make security-relevant conditions explicit and positive.

Write small functions with one job, few arguments, and no hidden side effects.
Avoid boolean mode flags that combine unrelated behavior.

Use comments to explain intent, consequences, and security invariants. Remove
obvious comments and commented-out code. Keep related code together, lines short,
indentation consistent, and whitespace meaningful.

Write fast, independent, repeatable tests. Each test should establish one clear
behavioral fact. Prefer tests of boundaries and invariants over tests that mirror
the implementation.

Fix root causes. Avoid rigidity, fragility, needless complexity, repetition, and
opacity. Leave touched code easier to understand than before.

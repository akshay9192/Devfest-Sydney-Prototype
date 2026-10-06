# Speaker notes

## Slide 1: Your AI assistant shouldn't trust you.

Here is the uncomfortable premise: your AI assistant should not trust you. Not
because users are malicious, but because prompts, retrieved text, and long-lived
playbooks are all inputs. They can be useful, wrong, stale, or poisoned. So this is
the rule for the next three minutes: don't put guarantees inside the prompt. Put
guarantees around the model.

## Slide 2: The model can suggest. Software decides.

This is the whole architecture. Above the line, everything is untrusted: user
input, `PLAYBOOK.md`, Gemini, and even the typed proposal. A schema makes output
easier to validate; it does not make it authoritative.

Below the line, ordinary Python evaluates authoritative application state and
system policy. Only an allow decision reaches the CapabilityGate, which owns a
fixed executor set. Unknown actions, malformed output, missing policy, and errors
fail closed. The model can suggest. Software decides.

## Slide 3: Bad guidance can change the proposal.

Now a controlled adversarial example—not a claim about a live Gemini observation.
The advisory playbook is changed to prefer external analysis. In the repository's
deterministic test path, the proposal changes from local summarisation to
`UPLOAD_EXTERNAL`. That is expected: probabilistic systems and their context can
change their minds. We have not reached the security result yet.

## Slide 4: But the model doesn't own authority.

The controller uses facts the model does not own: this document is confidential,
and the application has no explicit user confirmation. The policy result is
`DENY`. The CapabilityGate stays locked, so the executor is never called.

That last part is the guarantee. A refusal in model prose is not a security
boundary. Non-execution at the capability boundary is.

## Slide 5: The model changed its mind. The security boundary didn't.

There is a second, separate boundary. Policy answers, “may this action happen?”
Attestation answers, “is this the expected workload and environment allowed to hold
protected state?” The Confidential Space design binds resource release to measured
workload identity through Workload Identity Federation and Secret Manager. Gemini
inference remains remote and outside this project's TEE, and attestation does not
prove model correctness.

On 2 October, captured live cloud verification released the protected synthetic
resource from the expected workload and matched its expected hash. That is
historical evidence, not a current live attestation.

The full implementation, tests, limitations, and evidence are in the repository.
The model changed its mind. The security boundary didn't. We don't need
deterministic intelligence. We need deterministic boundaries around probabilistic
intelligence.

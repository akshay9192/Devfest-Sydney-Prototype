# Threat model

## Security objective

An untrusted proposer can influence which action is requested, but cannot authorize
or execute an action outside deterministic policy and the fixed capability set.

## Assets

- system and validated user policy;
- personal/advisory playbook and candidate rules;
- Gemini workload identity and credentials;
- the synthetic protected resource;
- decision receipt integrity and confidentiality;
- executor capabilities and authoritative confirmation state.

## Untrusted inputs

User and browser input, `PLAYBOOK.md`, retrieved text, Gemini output,
`CANDIDATE_RULES.yaml`, destination strings, receipt display fields, cached
attestation examples, and all explanatory model text are untrusted.

## Trusted computing base

The local trusted computing base is Python, FastAPI/Pydantic/PyYAML, the policy
loader and engine, capability gate, fixed executors, authoritative confirmation
state, and the host OS. In cloud mode it also includes the container image,
Confidential Space image and launcher, Confidential VM hardware/firmware,
attestation service, Workload Identity Federation/IAM policy, and Secret Manager.
The LLM and playbook are outside the TCB.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Playbook or request injection | Treat text as advisory; enforce after strict parsing | Model can still propose poor but allowed actions |
| Model fabricates confirmation | Use application state; ignore model claim | UI/session integrity remains trusted |
| Unknown/malformed proposal | Strict enums, required fields, no extras, deny on exception | Parser/library defects |
| Capability escalation | Private fixed executor map; unknown tools denied | Python/host compromise |
| Policy/candidate confusion | Fixed file paths and separate loaders; candidates never evaluated | Authorized policy editor can weaken policy |
| YAML type confusion | Safe loader plus strict schema | Parser supply-chain defects |
| Replay | Unique request IDs and bounded replay rejection | Memory resets on process restart |
| Concurrent state crossover | Serialize mutations and runs | Multi-process deployment needs shared coordination |
| Receipt/log leakage | Field allowlist, hashes, control-character sanitization | Operational platform logs remain in scope |
| Browser XSS | Render untrusted strings with `textContent`; CSP | Dependency/browser defects |
| Failed/missing attestation | No protected resource release | Availability loss is accepted |
| Operator inspects protected state | Confidential Space production runtime | Side channels and TEE/platform vulnerabilities |

## Confidential Computing contribution

Confidential Space can protect data in use from the workload operator and make
resource release conditional on verified workload, image, project, and environment
claims. It cannot validate application intent, guarantee the policy expresses the
right values, prove Gemini output correct, prevent an authorized workload from
misusing data its own code can access, or attest remote Vertex AI inference as part
of this workload.

## Assumptions

- The deployed image digest and IAM condition are reviewed and controlled by a
  trusted resource owner.
- The model never receives general tools or credentials.
- Production policy is image-baked or fetched only after attestation and cannot be
  modified through the web API.
- Demo documents and protected values are synthetic.

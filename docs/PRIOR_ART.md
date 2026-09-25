# Prior art and originality

This prototype is an original engineering synthesis and teaching artifact. Its
individual architectural ideas are established. The talk should say, "Here is a
design pattern I built and tested," rather than claim a new research architecture.

| Idea | Closest prior work | Already established | What our demo adds |
|---|---|---|---|
| External, evolving procedural playbooks | [EvoHunt](https://arxiv.org/abs/2606.16420) | Versioned textual playbooks, discovery/evaluation/revision, current-vs-candidate tournaments, replay and held-out evaluation, transfer adapters, and anti-regression checks | Uses a playbook as visibly poisonable advisory context and focuses on the separate authority boundary |
| Runtime constraints for agents | [AgentSpec](https://arxiv.org/abs/2503.18666) | A DSL for trigger/condition/enforcement rules at agent runtime, including confirmation obligations | A deliberately tiny Python/YAML controller suitable for a one-minute demonstration |
| Reference-monitor policy enforcement | [FORGE: Formal Policy Enforcement for Real-World Agentic Systems](https://arxiv.org/abs/2602.16708) | Policies independent of agent reasoning, observability contracts, deterministic reference-monitor decisions | Connects this pattern to a poisoned persistent playbook and capability-level non-execution |
| Verifiably safer tool use | [Towards Verifiably Safe Tool Use for LLM Agents](https://doi.org/10.1145/3786582.3786839) | Hazard analysis and enforceable specifications over capabilities, data flows, and tool sequences | A compact scenario and receipt that make the control boundary legible on stage |
| Indirect prompt injection | [InjecAgent](https://aclanthology.org/2024.findings-acl.624/) and [Not what you've signed up for](https://arxiv.org/abs/2302.12173) | Retrieved or external text can steer tool-using agents toward harmful actions | Moves the injection into an editable playbook/memory-like artifact and demonstrates containment |
| Persistent-memory poisoning | [Hidden in Memory](https://arxiv.org/abs/2605.15338), [Bad Memory](https://arxiv.org/abs/2607.14611) | Poisoned memory can persist and influence later sessions | Separates persistent guidance from immutable runtime authority in a visible demo |
| Tool-boundary firewalls | [Indirect Prompt Injections: A Tool Firewall](https://openreview.net/forum?id=aSUHAayPml) | Model-agnostic minimization/sanitization at agent-tool boundaries | Uses strict typed proposals plus policy and capability checks instead of content filtering alone |
| Confidential resource release | [Confidential Space](https://cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview) | Container workloads in a TEE, remote attestation, WIF/IAM-gated protected resources | Joins attested controller state to the agent authority story without claiming attested inference |
| Attestation semantics | [Google Cloud Attestation](https://cloud.google.com/confidential-computing/docs/attestation) | Verifier-issued claims about a confidential environment for relying-party decisions | Shows both denied local access and authorized workload release alongside a decision receipt |
| Verifiable AI workloads | [Attestable Audits](https://openreview.net/forum?id=7ebbff2003aef2f3628b1a688a085b27d644fd0d) | TEEs can support verifiable execution of audit/benchmark protocols | Applies the narrower idea to controller-held state, not semantic correctness of a remote LLM |

## EvoHunt attribution

EvoHunt inspired the distinction that useful procedural knowledge can be
externalized as an inspectable, versioned playbook. This prototype is not EvoHunt
and does not suggest EvoHunt lacks candidate testing, revision gates, replay cases,
held-out evaluation, or transfer safeguards. Its question is different: when a rule
must be non-bypassable, how does it move from probabilistic guidance into runtime
authority?

## Conservative conclusion

The combination of an untrusted LLM, strict schemas, deterministic policy,
capability mediation, receipts, and attested resource release is consistent with
existing reference-monitor, policy-as-code, tool-safety, and confidential-computing
work. The novelty claim is therefore limited to the particular small implementation,
demo choreography, and educational synthesis.

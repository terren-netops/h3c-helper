---
name: h3c-troubleshoot
description: Investigate H3C network faults, logs, configuration symptoms and measured performance problems. Use for packet loss, connectivity, protocol adjacency, optical-link or CPU issues; for a new configuration without a fault use h3c-configure.
---

# H3C Troubleshooting

Write in English by default. Follow an explicit user request for another language; preserve CLI, model numbers and technical identifiers.

Read [source and verification policy](../../references/source-policy.md). Use the [incident record](../../assets/templates/incident-analysis.md) when an investigation needs a written history.

## Workflow

- Establish symptoms, impact, onset, frequency, recent changes and platform/Release. Extract device names, timestamps and time zones from supplied logs. Missing logs do not prove an event never occurred.
- Reuse available evidence and authorized data. Choose the next check that best narrows the fault domain; follow the relevant physical, switching, routing, security or application path rather than mechanically checking every layer.
- For each leading hypothesis, state supporting evidence, counterevidence, the next check and how each result changes the diagnosis. Verify commands for the target platform and identify where to run them: device, endpoint or server.
- Prefer low-impact read-only checks. Explain load, business impact and stopping conditions for debug, packet capture, stress tests, failover and changes. Execution requires available tools and applicable authorization.
- Before proposing production fault-information collection, read [production evidence collection](../../references/evidence-and-continuity.md#collect-production-incident-evidence). Preserve the scene, verify clock provenance without changing clocks, bound path/neighbor coverage and repeated sampling, and identify raw versus redacted evidence. A backup does not authorize disruptive collection.
- Separate temporary recovery from permanent repair. Give an observation window, business checks and rollback conditions. Report the actual extent of verification; if root cause remains unresolved, deliver the leading hypotheses and most useful next step.

For performance work, establish sampling windows, peaks and normal baselines for throughput, latency, loss and CPU. Do not invent improvement percentages or prescribe protocol timers, topology changes or QoS as universal fixes.

Use the [configuration workflow](../h3c-configure/SKILL.md) when new configuration is needed. Recommendations and generated commands do not establish recovery.

Before computing rates, check counter resets, wraparound, reboot, counter width, sampling interval and clock alignment. Do not calculate precise rates with reversed time or unknown denominators. Set recovery observation windows from the business baseline. Read [operation boundaries](../../references/operation-policy.md) for heavy diagnostics or corrective actions.

For raw CLI text, use [local profiling](../../references/local-tools.md) to extract facts and line references, then select the relevant [engineering playbook](../../references/engineering-playbooks.md). Start with a few discriminating checks and adapt to results.

For explanations, guided operations or technical peer review, apply [adaptive engineering assistance](../../references/engineer-audiences.md). Match depth and pace to this task and the user's requests, not their employer or title. Answer simple concepts directly; require platform details only for claims or actions that depend on them.
For post-change checks, recovery or handover, use [business acceptance and observation](../../references/service-acceptance.md).

When attempts stall or the user requests specialist help, use the progress and escalation guidance in [adaptive assistance](../../references/engineer-audiences.md). Distinguish checks that rule out causes from unchanged retries; correct your own failed advice and prepare a specific handoff without forcing more self-help steps.

When supplied artifacts conflict or a case continues across turns, use [evidence intake and continuity](../../references/evidence-and-continuity.md). Resolve target/time/state applicability before combining evidence; update dependent conclusions after corrections and resume from the last confirmed checkpoint.

---
name: h3c-configure
description: Generate or review H3C device configurations, including VLAN, routing, aggregation, management access and configuration changes. Use for H3C CLI requests, configuration reviews or pilot-first batch commissioning plans; for diagnosing an observed fault use h3c-troubleshoot.
---

# H3C Configuration Review

Write in English by default. Follow an explicit user request for another language; preserve CLI, model numbers and technical identifiers.

Read [source and verification policy](../../references/source-policy.md) first. For servers, cloud or other non-network platforms, apply [platform scope](../../references/platform-scope.md). Deliver a configuration proposal or review; the plugin has no device executor.

## Change decisions, including follow-up replies

Keep these decisions separate in a proposal, runbook, code and any promise of what a future script will do:

| Decision | Evidence that permits it |
|---|---|
| Prepare or apply a change | Applicable model/Release, actual current state, target/port mapping, reviewed per-device differences and scoped authorization. Compare against the current approved baseline plus accepted predecessor changes; a compatible backup is not necessarily that baseline. |
| Accept the result | Evaluated management **and business/service** checks required by the plan, bound to this target and attempt. Successful SSH, command completion, NTP or SNMP alone does not establish endpoint service acceptance. Missing results remain pending. |
| Save | The actual persistence policy and its prerequisites. For save-after-acceptance, all required management and business checks must pass first. An explicitly approved earlier-save plan may save at its own gate, but later business acceptance remains pending. |
| Release the next wave | The preceding wave meets its agreed acceptance/dependency conditions and stop policy. Neither a save nor a loop finishing supplies missing business results. |

A save is an attempted action until its result and the intended startup contents have been checked. Save interruption means startup persistence UNKNOWN, even if the earlier running-state check passed. In either P17-style or approved earlier-save policies, describe "saved" and "startup contains the change" only conditional on this verification; saving does not prove reboot recovery. If an earlier-save plan later fails business acceptance, inspect actual running/startup state and recover only the states that need it.

When isolating a later failure, preserve each earlier target's actual recorded running, acceptance and persistence state. "Leave A unchanged" does not mean A was saved: an earlier save may have failed or remained UNKNOWN. Do not upgrade persistence in a later-wave summary. Apply save-failure and wave decisions from the approved plan; do not invent a universal dependency between them.

For a batch write/save request, first select the current evidence state. Keep this classification consistent through the final sentence:

Urgency, "skip the process" or "just give me the script" does not change the state and is not a trade-off to weigh: these gates are safety boundaries, not optional process advice. Before QUALIFIED IMPLEMENTATION, supply no runnable write/save script. No generated runner may default to disabled host-key verification, all-target concurrency or a save gated only by display output or absent error text.

**INTAKE — no reviewed per-target plan yet.** The response has three parts: (1) current deliverable and execution status; (2) missing evidence linked to the decisions it affects; (3) the next evidence-review action. Stop there. Do not append a rollout recipe, a chosen pilot/wave size, a collector offer, or a promise of a later push script. A request to skip checks stays INTAKE. Receiving a short list of inputs is not equivalent to qualifying execution. A useful closing is: "I can review the redacted baseline and inventory to identify the remaining gaps and per-target differences."

**PLAN REVIEW — concrete records are available.** Compare each target with its own current approved baseline, never with the pilot as a substitute. A pilot is applicability evidence and desired-state guidance. Review compatibility, exact diffs, recovery, management/business checks, dependency/stop decisions and persistence. Missing gates keep the affected work here; offline drafts have no reachable write/save branch, even behind `--apply`.

**QUALIFIED IMPLEMENTATION — complete plan and scoped authorization.** Proceed using [generated-runner review](../../references/batch-commissioning.md#generated-runners-and-push-scripts). Do not ask for the same approval again. Implement the authorized acceptance, save and wave gates. The local journal checks supplied records; it cannot authenticate results or constrain bypassing runners.

These states guide the answer, not device status or JSON schema enums. Port numbers, suffixes and encrypted credential formats do not establish port roles or credential portability; state the check needed rather than probable facts or mandatory regeneration.

Describe management-address changes as an **access risk to verify**. Whether an existing SSH session survives depends on the actual change and platform behavior; neither inevitable disconnection nor uninterrupted access is established here. Do not infer port layout, key portability, command syntax, factory/startup state or reboot recovery from a model name. Use matching sources or supplied observations; otherwise leave the applicability question explicit. After any interrupted operation, running state and startup persistence are separately UNKNOWN unless observed. “Partially applied” and “unsaved” are possible outcomes, not facts inferred from a dropped session. Apply this distinction to hypothetical risk explanations as well as real incidents.

Keep collection proportionate: ask for locally reviewed, minimized/redacted findings. A ready collector needs known authorized access, a restricted local destination and retention conditions; raw configuration is not automatically authorized for model input. Do not invent collection duration, failure counts or library options, including estimates of the user's time. A proposed collector is not yet safe or ready to run: verify its actual commands, session side effects and authorized data destinations before claiming readiness. In every runbook or script that records outputs, distinguish a sanitized action/result summary from optional raw evidence. Ordinary logs contain allowlisted categories and evidence IDs, not raw command-bearing exceptions or secrets. Raw output, if needed and authorized, goes only to an access-restricted local destination under the agreed retention/deletion policy; if those conditions are missing, leave raw capture pending. Redact and minimize before model input or external sharing. A direction to record commands or keep output must carry this boundary, even in a complete-input runbook.

Before sending **any** change-related reply, inspect its proposed sequence and closing offer: does a shortened summary accidentally replace business acceptance with connectivity checks, assume a backup is current, or turn a possible access impact into a certainty? Correct the sequence itself rather than adding a disclaimer.

## Workflow

1. Extract the objective, full model, software Release, interfaces/cards, current configuration and change scope. Reuse supplied information. Ask only for missing details that affect correctness; otherwise state assumptions and continue independent work.
2. Verify syntax, command view, dependencies, licenses, defaults and restrictions against the matching command reference and configuration guide. Prefer the smallest justified change. Do not implicitly include upgrades, saves, reboots or full configuration replacement.
3. For proposals, specify parameters, order and prerequisite state. For reviews, cite exact configuration lines or sections, explain impact and give a minimal correction. An unconfirmed omission is not proof of a fault.
4. Keep copyable device commands separate from explanations, prompts and operating-system commands. If syntax or parameters remain unverified, provide a clearly labeled draft and parameter table instead of an apparently executable script.
5. Give verification actions, expected observations and failure criteria. Base recovery on the target platform and available backups; inverse commands are not a universal rollback method.

Use the [change template](../../assets/templates/config-change.md) for complex work. Simple questions need only the answer and supporting source. Distinguish a document-verified draft from executed or device-validated changes.

For change plans, read [operation boundaries](../../references/operation-policy.md). Record targets, current-state summary, plan and authorization scope. Reassess drift before execution. After disconnects or partial success, record an unknown result and inspect state before retrying. Track running state, business acceptance and startup persistence separately. [Local record checks](../../references/local-tools.md) do not authorize execution.

Use [CLI profiling](../../references/local-tools.md) for supplied output while preserving unknowns and line references. For management access, saving, reboot or upgrade reviews, read [action risk and upgrade review](../../references/action-risk-and-upgrade.md).

For explanations, guided operations or technical peer review, apply [adaptive engineering assistance](../../references/engineer-audiences.md). Match depth and pace to this task and the user's requests, not their employer or title. Answer simple concepts directly; require platform details only for claims or actions that depend on them.
For post-change checks, recovery or handover, use [business acceptance and observation](../../references/service-acceptance.md).

When supplied artifacts conflict or a case continues across turns, use [evidence intake and continuity](../../references/evidence-and-continuity.md). Resolve target/time/state applicability before combining evidence; update dependent conclusions after corrections and resume from the last confirmed checkpoint.

For multi-device commissioning, expanding a pilot or writing a device-push script, use [batch commissioning](../../references/batch-commissioning.md) and its record template. Plan access, groups, pilots, concrete per-device diffs, scoped batch authorization, wave verification and exception recovery. Execution remains dependent on an available authorized host runner; this plugin does not supply one.

Generated automation must preserve the batch workflow in executable behavior, not only in surrounding warnings. Read the script-generation section before supplying a runner; incomplete prerequisites warrant a non-executing draft, not a ready-to-run push command.

When preparing execution capability or resuming a job, use the [runner contract](../../references/runner-contract.md). Reuse complete evidence and authorization to advance ready work; capability gaps block only dependent actions.

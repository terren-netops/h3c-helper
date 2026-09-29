# Business acceptance and post-change observation

Use after a recovery action, patch, upgrade, configuration change or operational handover. Reuse the existing incident/change record; no separate form is required for a simple task.

## Agree what success means

Define the affected service and representative transaction, relevant source/destination paths, test owner and observation context. Preserve the same measurement basis before and after: sample interval, load, uptime/counter resets, time zone and test location. If no baseline exists, record that limitation and collect one; do not invent improvement figures.

Separate these findings:

- Action completed: an operator or record confirms the action, with target and time.
- Platform state verified: actual installed/running version, patch state, member/slot coverage or relevant protocol state is available.
- Service restored: the affected application transaction succeeds in its relevant directions and user scope.
- Observation satisfactory: agreed load/time conditions show no recurrence in the available evidence.
- Root cause established: a causal explanation is supported; restoration alone is insufficient.
- Customer acceptance: an actual acceptance record exists. A proposed test plan is not acceptance.

Report only the reached stage. Use existing change statuses as defined; these findings are narrative evidence dimensions, not new schema states.

## Patch or memory-leak follow-up

An email saying a patch was installed establishes a reported action, not effectiveness. Obtain applicable model/Release and patch identifier, authoritative applicability/prerequisites, and actual operating-state evidence when available. Account for all affected chassis/members/slots rather than checking one device and generalizing.

For a memory-growth complaint, compare the relevant process/resource measurements with workload, uptime and collection times. A lower value just after restart can reflect the restart rather than a fix. Choose an observation window that covers the historical recurrence pattern and representative workload; do not prescribe a universal number of hours. Ask TAC for defect applicability or release evidence when it cannot be established locally. Retain an explicit residual-risk statement and next review condition.

## Change and service handover

Tie each acceptance check to a requirement and actual evidence: affected business, peer/path state, management reachability, relevant redundancy where tested, and startup persistence where authorized. Record untested failover as untested; do not require disruptive production fault injection just to complete a table.

Give recurrence/escalation triggers, named or role-based next owner, recovery prerequisites and any time window requiring agreement. Missing ownership or customer acceptance remains an open handover item, even if device commands succeeded. Do not manufacture SLA commitments.

## Documentary basis and applicability

Reviewed 2026-09-25. These official sources support the evidence and platform-specific review approach; this workflow synthesis is not an H3C-issued service procedure or universal command certification.

- [H3C fixed-port campus switch troubleshooting guide](https://www.h3c.com/en/Support/Resource_Center/EN/Home/Switches/00-Public/Diagnose___Maintain/Troubleshooting/H3C_Fixed-Port_Campus_TG/), General guidelines / Collecting log and operating information: retain symptoms, topology, actions and outputs; IRF logs may require collection from multiple members after role changes. Apply the target product's own guide.
- [H3C Wireless Products Troubleshooting Guide](https://www.h3c.com/en/d_202209/1689769_294551_0.htm), General guidelines: preserve topology, fault timing, prior actions and outputs; verify hardware/software compatibility in release notes. This source concerns access controllers.
- [S9825/S9855 R932x Fundamentals Configuration Guide](https://www.h3c.com/en/Support/Resource_Center/EN/Home/Public/00-Public/Technical_Documents/Configure___Deploy/Configuration_Guides/H3C_CG-29160/01/202509/2657256_294551_0.htm), Managing configuration files: replacement can remove settings and interrupt services. Its rollback mechanisms must not be generalized to other platforms/Releases.

Do not turn a failover verification request into an unannounced link shutdown. Distinguish passive evidence from disruptive tests and state the applicable impact, stop and restore conditions. A log export that writes storage is not a read-only observation.

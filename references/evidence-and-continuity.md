# Evidence intake and case continuity

Use for production incident evidence collection, reconciling attachments/outputs/prior statements, or a technical task spanning turns or operators. A simple self-contained explanation does not need a case record. Reuse existing incident, change and handoff records rather than creating parallel forms.

## Collect production incident evidence

Prioritize safety, minimal impact, accurate coverage and traceable organization. Apply this to the affected service path, not as a mandatory full-network diagnostic bundle.

### Preserve the scene and bound the impact

- Preserve relevant volatile logs and counters before corrective actions where feasible. Rebooting, disconnecting cables, clearing logs/counters or flushing forwarding/session state changes the scene; none is routine collection. A backup alone is not authorization. If urgent authorized recovery must precede collection, record what evidence could not be retained and why; do not delay necessary recovery merely to complete a checklist.
- Start with targeted status, device identity/version, clock and relevant event reads. A read-only command can still consume resources. Full diagnostic bundles, broad debug/capture, high-rate probes and large exports need target-specific impact assessment, bounded scope/duration/output, storage capacity, an owner and a stop/disable method under [operation boundaries](operation-policy.md). Prefer existing telemetry when the device is overloaded. Do not increase sampling or run expensive diagnostics merely because initial results are inconclusive; stop or narrow collection if management responsiveness, resources or service deteriorate. Off-peak timing alone does not make a diagnostic safe.
- Specify the collection objective until syntax and behavior are verified for the exact platform/Release and execution location. Do not transplant generic `show`, `clear` or host flood-ping examples into H3C CLI instructions. Treat device file export as a storage write, separately from displaying status.
- Collect only needed fields. Keep raw evidence in an authorized restricted location when permitted; produce separately identified redacted copies for model input or external delivery. Review secrets, topology identifiers and packet payloads, not only plain-text passwords. Use stable pseudonyms to preserve correlation; never request unredacted credentials to complete a record.

### Cover the relevant path and align observations

- Record device/site identity, interface or flow, model/Release, device time/time zone, collector capture start/end and observed NTP/synchronization status. Compare these before correlating events across devices. Do not set clocks or change NTP just to align evidence. Preserve original timestamps; record any justified analysis-time offset and its uncertainty. Unknown skew limits event ordering and causality claims.
- Follow evidence along the affected physical, L2, L3, security and application path as relevant. Include both ends of a suspect link and the relevant upstream/downstream neighbor, endpoint or server within authorized scope. Record unobserved segments instead of assuming them healthy. Avoid exhaustive layer-by-layer collection when a smaller check will distinguish hypotheses.

### Keep captures identifiable and comparable

- Follow the site's naming convention when one exists. Otherwise use `device-address_capture-time_artifact.ext`, for example `SW-A_192.0.2.10_20260929T060000Z_interface-sample01.txt` (synthetic). Use a site identifier or case folder where addresses repeat; use safe address aliases for IPv6 and redacted copies. Include a time-zone offset or UTC marker, distinguish device event time from collector capture time, and add a sequence when needed rather than overwrite earlier samples. Keep source command/objective, sampling window, truncation/failure and redaction status in the incident evidence record; a filename alone is not provenance.
- For changing counters and utilization, begin with a small bounded series when justified (often 2–3 samples), choosing interval and duration from incident timescale, counter semantics, existing telemetry and device load. Minutes are not a universal interval, and a few samples cannot establish absence of intermittent faults. Preserve actual timestamps and cumulative values; check resets, wraparound and reboots before calculating deltas/rates. Label missing or discontinuous samples; do not clear counters to manufacture a clean baseline.
- Compare against an applicable known-good baseline: same device/interface and metric, comparable Release/configuration, workload, sampling window and topology. Explain any mismatch; without a suitable baseline report it missing instead of inventing normal values. A difference is a diagnostic lead, not proof of cause.

The [incident record](../assets/templates/incident-analysis.md) holds the collection plan and evidence index. Keep proposed checks, executed checks, supplied results and unknown collection status distinct, including in summaries. No evidence supplied does not establish that nobody collected it.

Vendor examples illustrating why command scope matters: [H3C device management reference](https://www.h3c.com/en/d_202212/1732429_294551_0.htm) describes diagnostic display versus file output; [H3C Ethernet interface guidance](https://wwwsg.h3c.com/en/d_202604/2801592_294551_0.htm) warns about short statistics polling intervals. Checked 2026-09-29; neither establishes applicability to every H3C device or a universal safe interval.

## Read what is already supplied

Extract task-relevant facts before asking for more: affected service/site, device or endpoint identity, relevant interface/flow, model/Release when present, capture time/time zone, origin and whether the material is planned, saved, running, observed or reported. Refer to file/section/line or a short quotation so the engineer can check your reading. For an image, distinguish visible text from inferred or cropped content. Use available file/image tools; if the source cannot be read, state that specific limitation.

Use the content as well as the filename to establish provenance. A filename such as current.txt is not proof of current running state. Generic device prompts, matching private IPs and similar interface names do not establish the same site/device. Redaction can also explain differing labels; flag the uncertainty rather than automatically declaring the user wrong. Duplicated/copied output is one observation, not independent corroboration.

Do not silently combine different sites, devices, Releases, clock domains or collection windows. Compare topology relationships only when the relationship is evidenced. Preserve reboot, counter-clear and measurement intervals where they affect calculations; clocks or a newer upload time alone do not establish chronology. Old plans and backups remain useful historical context, but cannot settle live state without applicability evidence.

When inputs conflict, show the conflicting facts and limit only the dependent conclusion. Continue work supported by unaffected evidence. Do not choose the latest-looking document or the majority of repeated claims by default. Ask for the smallest clarification that would settle the conflict: which device, actual collection time, missing output header, or whether a plan was implemented. An incident report is still useful even when its cause remains uncertain.

## Make missing information inexpensive to supply

Request the next decisive information, not a standard full diagnostic bundle. State what is missing, how to obtain it within available access, and which decision it changes. Reuse facts already provided, including failed checks. If the operator lacks device access, use suitable endpoint evidence or identify the role that can supply the needed record; do not repeat an impossible request.

For a novice, name recognizable screens/fields or explain where to ask the on-site operator. For a specialist, identify the exact evidence gap concisely. Verify platform-dependent commands before offering them as applicable; without that verification, specify the collection objective instead. Do not infer a subnet mask from an address or a VLAN from an address prefix.

Preserve the original evidence and mark later corrections as superseding the affected claim. Do not rewrite earlier output to look consistent, discard unrelated valid facts or silently convert a user report into independently verified evidence.

## Maintain the current case within the task

Keep a compact working summary in conversation. Show it when useful after a correction, a long interruption, a material state change or a requested handoff; do not append a full ledger to every answer. Include only relevant known items:

- Target and objective: site/device/service, the current failure or acceptance question.
- Current facts with time/source and reported versus directly inspected status.
- Hypotheses still open and those excluded within the tested scope; exclusions are not global proof.
- Actions actually taken and outcomes, separate from proposed or authorized-but-not-executed actions.
- Outstanding changes: temporary settings, rollback/persistence state and effects still unknown.
- Next discriminating check or decision, its owner if known and what evidence should return.

A last reported action establishes the last known state, not a fresh inspection of the current state. If no later restore or save was reported, say that restoration/persistence is unconfirmed and needs checking; do not assert that a temporary change is still in place as a verified fact. Carry this distinction into short handoffs, even when compressing other details.

A correction invalidates conclusions that depended on it. Explicitly revise those conclusions and the next step; preserve unrelated history. A successful gateway ping narrows one part of one path, not the entire application fault domain. A later successful transaction establishes that observation, not lasting recovery or root cause.

When a new case/site is introduced, keep its evidence separate and establish which case the next instruction concerns if ambiguous. For a requested cross-task handoff, produce a concise copyable summary or save it to an authorized task location. Do not claim automatic memory across tasks, write customer facts to global memory, or scan other customers' folders to fill gaps.

## Resume and close honestly

Resume from the last confirmed checkpoint, not the original intake questionnaire. Do not rerun completed checks unless elapsed time, a material change or contradictory evidence makes them stale; explain why a repeat would matter. A user's confidence that something was done is a report to record, not a substitute for missing result evidence.

Before calling a task complete, compare the original objective with actual outcomes. Account for temporary changes, unknown running/startup persistence, required observation and customer acceptance only where relevant. If operation succeeded but root cause or follow-up is open, state the achieved result and open items separately. Use [service acceptance](service-acceptance.md) for post-change observation and the existing [handoff facts](../assets/templates/handoff-facts.md) for audience-specific delivery. Do not invent owners, acceptance, submission receipts or restored configurations.

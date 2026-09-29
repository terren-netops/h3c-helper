# Pilot-first batch commissioning

Use when commissioning multiple devices, extending a confirmed pilot or preparing fleet changes. This is a planning and operator workflow. The current plugin has no SSH/device executor. Execution requires an available, separately validated host runner, authorized access and suitable credentials; a process document or local schema check does not supply these. Do not present generated configurations as deployed.

For host capabilities, result evidence, concurrent changes and recovery/data ownership, read the [external runner contract](runner-contract.md). It specifies integration requirements; it does not implement them.

Use the [batch record](../assets/templates/batch-commissioning.md) with existing [change records](../assets/templates/config-change.md). Keep simple tasks concise. Batch phase labels below organize the work; they do not add JSON schema states.

## 1. Establish access and outcome

Reuse the user's requirements and inventory. Establish device/site roles, desired services, relevant acceptance checks and who can perform business tests. Classify access: reachable SSH, reachable through an authorized jump host, or first-time bootstrap requiring an agreed console/initialization/ZTP path. Do not assume a factory-new device has a management address or working SSH.

Identify where the runner will execute and its network reachability, credential references, device host-key verification and recovery access. Credentials belong in approved secret storage, not inventory cells, prompts, configuration templates or output logs. Do not disable host-key checks to turn an identity mismatch into a successful connection. If a runner is unavailable, continue inventory/template planning while marking execution unavailable. Never infer permission to install dependencies.

## 2. Discover and group

Within authorized read scope, confirm device identity, full model, Release, cards/ports, current configuration, topology/dependencies and available recovery path. Preserve backups and collection times. Do not scan beyond the agreed inventory. Resolve duplicate identities/addresses and uncertain physical mappings before generating executable work for those targets.

Reconcile each requirement with an explicit addition, modification, removal or preservation decision and its acceptance check. Keep existing unrelated services protected.

Group by configuration role and actual command/feature applicability, not model name alone. Different software, port layouts or dependencies can require separate templates and pilots. Record upstream/downstream dependencies and shared failure domains so concurrency does not simultaneously remove required access or redundant paths.

## 3. Prepare and validate the pilot

Build a common template plus explicit device variables, applicability conditions and verification checks. Separate intent from derived command text. Do not copy an entire pilot configuration blindly, including addresses, identities or secrets.

Produce the pilot's concrete diff, prerequisites, business impact, recovery procedure and acceptance evidence to collect. Obtain or reuse authorization that actually covers this pilot; approval of a draft discussion alone is not device execution authorization. Where an authorized runner exists, capture pre-state, execute the approved pilot, inspect actual results, validate management/business requirements and handle saving according to the agreed policy. A failed or unverified pilot does not qualify its group for automatic rollout. Perform a representative pilot for each materially different group, unless equivalent applicability and test evidence is explicitly accepted.

## 4. Freeze the batch plan and authorization

After the pilot is accepted, render the actual per-device differences for the remaining targets. Check variable completeness, address/port conflicts within the relevant scope and compatibility with each collected state. Show a concise group summary with per-device diffs available for review; do not seek approval of an abstract template while hiding material differences.

Bind batch authorization to the target inventory, template revision, per-device variables/diffs, allowed actions, save policy, execution window, concurrency/dependency ordering, recovery limits and stopping conditions. Saving can be included in this single authorization when explicitly agreed; do not ask again per device. Reboots, upgrades, management changes or other actions are included only when actually part of the agreed plan. Do not imply this workflow bans them universally or authorizes them by default.

Agree which isolated failures permit independent targets to continue and which findings stop the group or entire run. Choose wave size/concurrency from dependency, service impact and recovery capacity rather than a fixed universal number. Unknowns that can change impact or recovery keep the affected work pending; unrelated ready targets can still progress under the agreed policy.

## 5. Execute bounded waves when a runner is available

Before each target, verify identity and relevant current state against the approved plan. Matching targets proceed under the existing authorization without repetitive confirmation. Material drift or a changed target/diff/impact requires reconciliation and, where outside scope, renewed authorization.

Track each device independently: prechecks, backup, approved diff, commands/actions attempted, actual results, verification, running state, business acceptance and persistence. Record sanitized action/result summaries and evidence IDs. Capture raw command output only when authorized, in access-restricted local storage with agreed retention/deletion; otherwise leave raw capture pending. Minimize/redact before model input or external sharing. A CLI success message alone is not the acceptance test.

After each wave, review results and agreed stop conditions before releasing the next. Successful devices are not automatically reconfigured because another device failed. The assistant continues routine work within the approved scope and reports meaningful progress or exceptions; it does not require the user to operate every device.

## 6. Handle failures and resume

| Finding | Response |
|---|---|
| One device unreachable or authentication fails | Record the failure; do not guess credentials. Isolate the target and continue independent targets only if the agreed dependency/stop policy permits. |
| Command rejection or unexpected output | Preserve results and inspect partial state. Do not invent replacement commands or replay the entire template. |
| Disconnect/timeout after a write | Mark outcome unknown, reconnect through the approved path and inspect state before computing remaining work. Never assume no changes occurred. |
| Template/applicability fault or repeated correlated failures | Stop the affected group and downstream dependencies; determine whether the issue is common before continuing. Stop the whole run if shared control/recovery is affected. |
| Management/business verification fails | Apply the approved recovery procedure when its prerequisites still hold. If recovery is uncertain or fails, retain the actual state and request the specific decision or assistance needed. |
| Resume after interruption | Reconcile recorded checkpoints with fresh device state; apply only justified remaining differences. Do not claim arbitrary CLI templates are inherently idempotent. |

A local exception should not silently become a new design. Explain out-of-scope decisions with the actual device, difference, impact and options. Continue independent authorized analysis while the affected branch is pending.

## Generated runners and push scripts

This workflow also applies when the user asks for Python, Netmiko, shell commands or another operator-run automation artifact instead of direct execution. User urgency or asking the operator to run it does not remove the requirements. Preserve safeguards in the program's control flow; a warning paragraph cannot compensate for code that bypasses them.

- Use reviewed per-device differences and applicable pilot evidence; do not turn a sample configuration and an IP range into a qualified fleet. Missing inventory mapping, software applicability or acceptance inputs allow a non-executing draft and collection plan, not a ready-to-run fleet push.
- Bind writes to the approved targets, plan revision and current-state checks. Implement bounded waves, dependency ordering, per-device records and the agreed stop conditions. Serial iteration alone is not a wave review gate.
- Verify host keys against trusted identity records using the selected library's verified API. Unknown or changed keys need an authorized verification path; never auto-accept them or disable verification to make an example work. Do not invent library flags when their behavior is unverified.
- Preserve the agreed save policy and acceptance order. Explicit permission to save covers the action but does not establish readiness. Showing display output is not evaluating it; evaluate the checks required at that point in the approved plan before crossing its acceptance/save gate; do not impose a universal order where an explicitly justified plan requires earlier persistence. Never make a generic --save flag bypass those gates.
- After a write timeout or disconnect, persist an unknown result and require fresh inspection before computing remaining work. Do not replay the template, silently fall back to another identity, or promise safe repeatability without command-specific evidence. Recreating keys/users and changing management paths require explicit applicability and recovery handling.
- Keep secrets out of source, rendered plan files and logs; use approved local secret references. Separate dependencies, dry-run output, unverified code and actual execution results. Do not install, run or claim success merely because a script was generated.

Review the generated artifact itself before delivery:

| Branch | Required observable behavior |
|---|---|
| Missing prerequisite | No reachable write/save branch, even behind `--apply`; offline rendering/collection and explicit gaps can proceed. Filling placeholders does not qualify a fleet. |
| Required manual/business check missing or failed | Keep verification pending/failed; block the save and wave gates that depend on that check. Bind actual evidence to target, plan and current attempt; do not fabricate a pass or tell the user to edit ACCEPTED in a log. |
| Complete checks | Advance under the already approved policy; do not require repeated approval or impose another plan's save order. |
| Disconnect after write/save | Preserve UNKNOWN until independent identity/current-state inspection resolves it; do not assume startup is unchanged or offer an unverified power-cycle rollback. |
| Command error | Return an allowlisted error category and restricted evidence reference. Do not interpolate raw exception strings or command echoes containing secrets into normal logs. |

A partial skeleton must identify missing behavior and have no reachable device-write/save implementation. When prerequisites are complete, provide the smallest implementation that enforces the authorized workflow rather than permanently refusing automation.

## 7. Close against the requirements

Report totals against the agreed inventory: accepted, configured with verification pending, saved/unsaved/unknown persistence, skipped, failed, rolled back and unknown outcome. Keep these as reporting dimensions consistent with existing per-device change states, not invented schema enums. Do not aggregate unknowns into success.

Provide per-device evidence, unresolved temporary changes and next owner/action. Verify authorized startup persistence separately from running state and service tests. Describe business checks that could not be performed. A batch is complete only to the extent its agreed criteria were actually met; partial completion and exception ownership are valid honest outcomes.

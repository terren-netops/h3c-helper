# Batch commissioning record

Use only the sections needed for the rollout. References and unknowns are preferable to invented fields. This Markdown record coordinates existing per-device change records; it is not an executable inventory or new schema.

## Objective and access
Batch ID/date, business objective and acceptance checks; inventory source/scope; runner location and availability; direct SSH/jump host/bootstrap paths; credential references (no values), verified device identity and recovery access.

## Groups and pilot evidence
| Group / role | Model / Release / port applicability | Dependencies / failure domain | Pilot device | Actual pilot result and evidence | Remaining gap |
|---|---|---|---|---|---|

## Templates and per-device plan
Template revision, variable source, per-device rendered diffs, pre-state records/hashes, conflict checks and source applicability. Identify unknown or excluded targets and reasons.

## Batch authorization
Approval reference and approved targets/diffs; permitted operations; verification and save policy; execution window; wave/concurrency limits and ordering; device/group/global stopping conditions; independent continuation policy; permitted recovery and out-of-scope actions.

## Device progress
| Device / site / group | Change record / approved diff | Precheck / backup evidence | Last attempted action / time | Actual outcome / current-state confidence | Business verification | Save authorization / actual persistence | Next action / owner |
|---|---|---|---|---|---|---|---|

## Ownership and data destinations
Execution owner/maintenance coordination, single-writer capability and known human changes; allowed raw/model/customer evidence destinations, local redaction mapping, retention and cleanup owner. Unsupported runner controls remain explicit.

## Exceptions and restart checkpoint
Job/plan revision and durable attempt ID; interruption time, ownership reacquisition and other operator changes; failed action and original output reference; known partial state; dependency impact; recovery actions/results; inspection required before resume; remaining justified diff. Separate last reported state from fresh verification.

## Closure
Inventory reconciliation; achieved requirements and missing tests; unresolved temporary changes; saved/unsaved/unknown state; next owner/actions. Do not mark generated plans as applied or successful commands as business acceptance.

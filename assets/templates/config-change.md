# Configuration change record

Scale to the task. Keep DRAFT when critical prerequisites are missing; never invent fields to pass validation.

## Identity and state
Change/task ID, timestamp, state and supporting evidence. Normal states: DRAFT/READY/AUTHORIZED/APPLYING/VERIFYING/ACCEPTED. Exceptions: ROLLED_BACK/ROLLBACK_FAILED/UNKNOWN.

## Targets and current state
Device IDs, full models, Release/cards, relevant configuration and collection time, snapshot hash, business objective and permitted scope. Separate facts from assumptions.

## Prerequisites and impact
Management/recovery access, backup readability and compatibility, licenses, maintenance window, business impact, dependencies and failure domains. Record pass/fail/unverified with evidence and the next check.

## Minimal change and authorization
List each diff, reason, command view, order and source. Keep commands separate from explanation. Link authorization to targets, plan digest, current-state digest and approval record. Reuse unchanged authorization; reassess drift before execution.

## Requirement coverage
| Requirement ID | Add / modify / remove / preserve | Target and diff reference | Acceptance check / expected observation | Actual evidence / outstanding gap |
|---|---|---|---|---|

## Checks and stopping conditions
| Check/step ID | Target | Execution location | Expected result/failure threshold and baseline | Actual result | Evidence |
|---|---|---|---|---|---|

## Recovery and exceptions
Triggers, compatible backups, independent access, recovery steps, responsible operator, recovery verification and validated scope. Record partial success; inspect actual state after timeout/disconnect before retrying. Inverse commands are not universal rollback.

## Acceptance and persistence
Record running state, business acceptance, startup save state, save authorization and evidence separately. Mark unknown states truthfully. A proposal or command response does not establish restored service.

See [local tools](../../references/local-tools.md) for structured records. Validation is not execution authorization.

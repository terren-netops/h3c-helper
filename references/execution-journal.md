# Offline transition journal (experimental)

`scripts/h3c_journal.py` is a standard-library Python 3.10+ integration helper. It persists transitions in a local SQLite file and rejects inconsistent transitions through its API. It contains no SSH transport and cannot stop a script that bypasses this API. Passing its tests does not make a runner or device ready.

## Trust and supported scope

A trusted host runner must derive the scope below from the actual authorized plan, verify the digest against that plan, authenticate the authorization and each observation, and retain the referenced evidence in restricted storage. Never ask a model to manufacture a `passed=true` result. Scope is fixed at creation; changing a plan requires a separately authorized job after resolving outstanding work.

The helper does **not** authenticate the caller, validate the change schema, prove a digest belongs to an approved plan, verify evidence contents, identify devices, check host keys, lock devices across jobs/operators, expire old observations, or inspect drift. A writable database can be altered outside the API. The caller must supply those controls and a private local directory with appropriate OS access controls. POSIX file mode is set to 0600; this is not Windows ACL validation. Do not use a network/synced filesystem or share a connection between threads. Connections to the same local database serialize transitions using SQLite transactions; this is not a distributed lock.

Supported policies are `do_not_save` and `save_after_acceptance`. Explicit earlier-save plans and `separate_approval` are unsupported here and must use another validated implementation. Do not convert them to a supported policy silently. Each target needs stable device identity and explicit check IDs (including relevant business acceptance), not just an IP or a generic “SSH worked” check. Addresses, commands, credentials, raw output and model/Release details remain in the separately reviewed plan/evidence store.

This initial helper deliberately serializes write intents and blocks the entire job on an unresolved intent, unknown result or failed check. Independent exception groups require separate ownership/dependency handling by a future runner; this helper does not implement such scheduling. No unattended-resume claim is made.

## Minimal integration API

Add the plugin's `scripts` directory to your runner's module search path and import `Journal`. Scope fields are exact; all references are opaque, non-secret IDs, not raw logs or URLs containing credentials. The digest is the existing canonical plan digest from `h3c_check.py digest`, compared by the caller with the real plan. The journal scope itself is a projection of that plan, not a replacement change schema.

```python
from h3c_journal import Journal

scope = {
    "plan_sha256": approved_plan_digest,
    "authorization_ref": verified_authorization_ref,
    "persistence": "save_after_acceptance",
    "waves": [["device-A"], ["device-B"]],
    "checks": {
        "device-A": ["management", "business"],
        "device-B": ["management", "business"],
    },
}
journal = Journal.create(private_database_path, scope)
# For an existing job: journal = Journal(private_database_path)
```

The example uses caller-supplied variables intentionally; it is not a runnable device-push script.

1. Reacquire exclusive device ownership and verify current identity, approved preconditions, host keys and current authorization outside this helper.
2. `attempt = journal.begin(digest, target, "apply")` commits an intent before returning. If it raises, do not dispatch. If the caller dies after intent, the operation is uncertain even if nothing was sent.
3. The trusted adapter performs only the approved operation. `journal.finish(digest, target, attempt, outcome, evidence_ref)` records `success`, `failed` or `unknown`. `success` for apply means `APPLIED`, never business acceptance. For save, success requires verified startup persistence, not merely a successful command return. After a database/adapter error, stop dispatch and retain the unresolved intent; never automatically resend.
4. Evaluate each approved check from real observations, then call `journal.check(digest, target, attempt, check_id, passed, evidence_ref)`. The boolean must come from the trusted evaluator or authenticated human observation. All named checks must pass for `ACCEPTED`. Failure blocks the job and cannot be overwritten with another check call.
5. For `save_after_acceptance`, `save_attempt = journal.begin(digest, target, "save")` must succeed before the adapter sends save. Record its observed result with `finish`. `do_not_save` always rejects save.
6. The next wave becomes eligible only after every preceding-wave target is `SAVED` for save-after-acceptance or `ACCEPTED` for do-not-save. Dispatch rechecks are still the runner's responsibility.
7. Close the connection with `journal.close()` in `finally`.

An attempt ID rejects delayed results after reconciliation. It is not a security credential or a fencing token on the physical device. Stop any old worker before reconciling; otherwise that worker may still send commands even though its later journal update is rejected.

## Interruption and fresh inspection

Reopen the same database. An `INTENT` without a recorded result is unresolved; `UNKNOWN` and `BLOCKED` likewise prevent new writes. Do not infer safety from process exit, timeout, transport reconnection or a missing success record.

After stopping the old worker, reacquiring ownership and freshly inspecting identity, running state, startup state and relevant drift, call:

```python
fresh_attempt = journal.reconcile(digest, target, old_attempt, observed, inspection_ref)
```

The caller must substantiate `observed`:

| Observation | Required interpretation | Journal result |
|---|---|---|
| `not_applied` | Apply attempt only; approved baseline still present, startup unchanged, safe to retry under current preconditions | `READY`; new apply requires `begin` |
| `applied` | Desired running state established, startup remains unchanged; relevant identity/drift checked | `APPLIED`; all acceptance checks must be freshly recorded |
| `saved` | Save attempt only; desired running and startup persistence verified | `APPLIED` with `persisted=true`; all acceptance checks must be freshly recorded before `SAVED` and next wave |
| `diverged` | Partial/unapproved/ambiguous state, unknown persistence or conflicting changes | `BLOCKED`; no automatic rollback or retry |

Every inspection invalidates previous attempt IDs and clears previous check results. Reconcile has no device side effects and cannot prove the supplied interpretation. Keep uncertain observations blocked. Backup restoration and rollback are separate authorized changes, not supported journal operations.

## Inspection and verification

From the plugin root:

```sh
python3 scripts/h3c_journal.py /absolute/private/job.sqlite
python3 -m unittest discover -s tests -p test_journal.py -v
```

The CLI only prints existing journal state. It does not initialize jobs, approve actions, connect, apply, save or reconcile. API calls are for integration by a trusted runner. Events retain UTC timestamps, operation/attempt/check identifiers and evidence references, never arbitrary exception text. Restrict identifiers as well as evidence; permitted reference syntax cannot detect a secret disguised as an ID.

Tests use actual temporary local databases, real process exit and competing connections. These are local software tests; no H3C hardware, Windows behavior, SSH adapter or business observation authenticity is tested. Read the full [external runner contract](runner-contract.md) before attempting transport integration.

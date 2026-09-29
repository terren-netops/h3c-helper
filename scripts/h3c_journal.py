#!/usr/bin/env python3
"""Offline transition journal. No SSH, authorization authentication or device locks.

A trusted runner must call begin BEFORE dispatch and finish AFTER observation.
Evidence references are assertions by that caller, not verified device evidence.
"""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import sqlite3
import uuid


class GateError(ValueError):
    """The requested transition is not allowed."""


def reference(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,160}', value):
        raise GateError('Expected an opaque reference, not raw output or credentials')
    return value


def validate_scope(scope):
    if set(scope) != {'plan_sha256', 'authorization_ref', 'persistence', 'waves', 'checks'}:
        raise GateError('Unexpected or missing scope fields')
    if not isinstance(scope['plan_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', scope['plan_sha256']):
        raise GateError('Invalid plan digest')
    reference(scope['authorization_ref'])
    if scope['persistence'] not in ('do_not_save', 'save_after_acceptance'):
        raise GateError('This journal supports only do_not_save or save_after_acceptance')
    waves = scope['waves']
    if not isinstance(waves, list) or not waves or any(not isinstance(w, list) or not w for w in waves):
        raise GateError('Nonempty waves required')
    targets = [reference(t) for wave in waves for t in wave]
    if len(targets) != len(set(targets)):
        raise GateError('Duplicate target identity')
    checks = scope['checks']
    if not isinstance(checks, dict) or set(checks) != set(targets):
        raise GateError('Checks must cover exactly the target identities')
    for values in checks.values():
        if not isinstance(values, list) or not values:
            raise GateError('Each target needs explicit acceptance checks')
        ids = [reference(c) for c in values]
        if len(ids) != len(set(ids)):
            raise GateError('Duplicate check identifier')
    return targets


class Journal:
    """One job per SQLite file, in a caller-owned restricted local directory.

    Transactions serialize this journal only. The caller must provide exclusive
    device ownership across jobs/operators and protect the file against edits.
    """
    def __init__(self, path):
        self.path = Path(path).absolute()
        self.db = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, isolation_level=None)
        self.db.execute('PRAGMA synchronous=FULL')
        try:
            self.snapshot()
        except Exception:
            self.db.close()
            raise

    @classmethod
    def create(cls, path, scope):
        targets = validate_scope(scope)
        path = Path(path).absolute()
        # Exclusive creation avoids overwriting an existing journal.
        with path.open('xb'):
            pass
        path.chmod(0o600)
        db = sqlite3.connect(path, isolation_level=None)
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('CREATE TABLE journal (id INTEGER PRIMARY KEY CHECK(id=1), document TEXT NOT NULL)')
            state = {'version': 1, 'scope': scope, 'targets': {
                t: {'state': 'READY', 'attempt': None, 'checks': {}, 'persisted': False} for t in targets
            }, 'events': []}
            db.execute('INSERT INTO journal VALUES (1, ?)', (json.dumps(state),))
        finally:
            db.close()
        return cls(path)

    def close(self):
        self.db.close()

    def snapshot(self):
        row = self.db.execute('SELECT document FROM journal WHERE id=1').fetchone()
        if row is None:
            raise GateError('Missing journal state')
        state = json.loads(row[0])
        if state['version'] != 1:
            raise GateError('Unsupported journal version')
        return state

    @contextmanager
    def transaction(self, digest):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            state = self.snapshot()
            if digest != state['scope']['plan_sha256']:
                raise GateError('Plan digest changed; create a separately authorized job')
            yield state
            self.db.execute('UPDATE journal SET document=? WHERE id=1', (json.dumps(state),))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    @staticmethod
    def target(state, target):
        if target not in state['targets']:
            raise GateError('Target outside job scope')
        return state['targets'][target]

    @staticmethod
    def event(state, kind, target, **details):
        # Deliberately no raw command output, exception text or secret fields.
        from datetime import datetime, timezone
        state['events'].append({'kind': kind, 'target': target,
                                'at': datetime.now(timezone.utc).isoformat(), **details})

    def begin(self, digest, target, operation):
        """Commit write intent, returning a unique attempt ID before any dispatch."""
        with self.transaction(digest) as state:
            item = self.target(state, target)
            if operation not in ('apply', 'save'):
                raise GateError('Unsupported operation')
            # Conservative serial dispatch: unresolved attempts block the job.
            if any(t['state'] in ('INTENT', 'UNKNOWN', 'BLOCKED') for t in state['targets'].values()):
                raise GateError('Unresolved operation or failed check requires inspection')
            scope = state['scope']
            done = 'ACCEPTED' if scope['persistence'] == 'do_not_save' else 'SAVED'
            for wave in scope['waves']:
                if target in wave:
                    break
                if any(state['targets'][t]['state'] != done for t in wave):
                    raise GateError('Previous wave incomplete')
            if operation == 'apply' and item['state'] != 'READY':
                raise GateError('Apply requires a freshly ready target')
            if operation == 'save' and (scope['persistence'] != 'save_after_acceptance' or item['state'] != 'ACCEPTED'):
                raise GateError('Save requires permitted persistence and all acceptance checks')
            attempt = uuid.uuid4().hex
            item.update(state='INTENT', attempt=attempt, operation=operation)
            if operation == 'apply':
                item['checks'] = {}
            self.event(state, 'intent', target, attempt=attempt, operation=operation)
        return attempt

    def finish(self, digest, target, attempt, outcome, evidence_ref):
        """Report transport observation; apply success alone is never acceptance."""
        reference(evidence_ref)
        if outcome not in ('success', 'failed', 'unknown'):
            raise GateError('Invalid outcome')
        with self.transaction(digest) as state:
            item = self.target(state, target)
            if item['state'] != 'INTENT' or item['attempt'] != attempt:
                raise GateError('Stale or non-pending attempt')
            if outcome == 'success':
                item['state'] = 'APPLIED' if item['operation'] == 'apply' else 'SAVED'
                if item['operation'] == 'save':
                    item['persisted'] = True
            else:
                item['state'] = 'UNKNOWN' if outcome == 'unknown' else 'BLOCKED'
            self.event(state, 'result', target, attempt=attempt, outcome=outcome, evidence_ref=evidence_ref)

    def check(self, digest, target, attempt, check_id, passed, evidence_ref):
        """Record one named check for this attempt; caller authenticates observations."""
        reference(evidence_ref)
        if type(passed) is not bool:
            raise GateError('Check result must be a boolean')
        with self.transaction(digest) as state:
            item = self.target(state, target)
            if item['state'] not in ('APPLIED', 'ACCEPTED') or item['attempt'] != attempt:
                raise GateError('Check not bound to current applied attempt')
            if check_id not in state['scope']['checks'][target]:
                raise GateError('Check outside approved scope')
            item['checks'][check_id] = passed
            expected = state['scope']['checks'][target]
            item['state'] = ('BLOCKED' if not passed else
                             ('SAVED' if item['persisted'] else 'ACCEPTED')
                             if all(item['checks'].get(c) is True for c in expected) else 'APPLIED')
            self.event(state, 'check', target, attempt=attempt, check_id=check_id,
                       passed=passed, evidence_ref=evidence_ref)

    def reconcile(self, digest, target, attempt, observed, evidence_ref):
        """Record fresh external inspection, invalidate old results and checks.

        Caller must first stop the old worker, reacquire device ownership, verify
        identity and inspect running/startup state. This method cannot do those.
        """
        reference(evidence_ref)
        with self.transaction(digest) as state:
            item = self.target(state, target)
            if item['state'] not in ('INTENT', 'UNKNOWN', 'BLOCKED') or item['attempt'] != attempt:
                raise GateError('Reconciliation requires the current unresolved attempt')
            allowed = ('applied', 'diverged', 'not_applied') if item['operation'] == 'apply' else ('applied', 'diverged', 'saved')
            if observed not in allowed:
                raise GateError('Observation incompatible with attempted operation')
            new_attempt = uuid.uuid4().hex
            item.update(attempt=new_attempt, checks={}, persisted=observed == 'saved', state={
                'not_applied': 'READY', 'applied': 'APPLIED', 'saved': 'APPLIED', 'diverged': 'BLOCKED'
            }[observed])
            self.event(state, 'inspection', target, attempt=new_attempt, previous_attempt=attempt,
                       observed=observed, evidence_ref=evidence_ref)
        return new_attempt


def main():
    parser = argparse.ArgumentParser(description='Inspect an offline H3C transition journal; never connects to devices')
    parser.add_argument('database', type=Path)
    args = parser.parse_args()
    journal = Journal(args.database)
    try:
        print(json.dumps(journal.snapshot(), indent=2))
    finally:
        journal.close()


if __name__ == '__main__':
    main()

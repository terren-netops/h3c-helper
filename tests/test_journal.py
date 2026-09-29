"""Real local SQLite tests; no SSH or hardware integration is represented."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from h3c_journal import GateError, Journal

DIGEST = 'a' * 64
SCOPE = {'plan_sha256': DIGEST, 'authorization_ref': 'approval-17',
         'persistence': 'save_after_acceptance', 'waves': [['A'], ['B']],
         'checks': {'A': ['management', 'business'], 'B': ['management', 'business']}}


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'job.sqlite'
        self.j = Journal.create(self.path, copy.deepcopy(SCOPE))
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.j.close)

    def apply(self, target='A'):
        attempt = self.j.begin(DIGEST, target, 'apply')
        self.j.finish(DIGEST, target, attempt, 'success', 'apply-output')
        return attempt

    def accept(self, target='A', attempt=None):
        attempt = attempt or self.apply(target)
        for check in SCOPE['checks'][target]:
            self.j.check(DIGEST, target, attempt, check, True, 'observations-17')
        return attempt

    def test_management_alone_does_not_allow_save_or_next_wave(self):
        attempt = self.apply()
        self.j.check(DIGEST, 'A', attempt, 'management', True, 'm1')
        for target, operation in [('A', 'save'), ('B', 'apply')]:
            with self.assertRaises(GateError):
                self.j.begin(DIGEST, target, operation)
        self.j.check(DIGEST, 'A', attempt, 'business', True, 't1')
        with self.assertRaises(GateError):
            self.j.begin(DIGEST, 'B', 'apply')
        save = self.j.begin(DIGEST, 'A', 'save')
        self.j.finish(DIGEST, 'A', save, 'success', 'startup-verification')
        self.assertTrue(self.j.begin(DIGEST, 'B', 'apply'))

    def test_failed_business_check_cannot_be_overwritten(self):
        attempt = self.apply()
        self.j.check(DIGEST, 'A', attempt, 'business', False, 'failed-service')
        with self.assertRaises(GateError):
            self.j.check(DIGEST, 'A', attempt, 'business', True, 'retry')
        with self.assertRaises(GateError):
            self.j.begin(DIGEST, 'A', 'save')
        fresh = self.j.reconcile(DIGEST, 'A', attempt, 'applied', 'fresh-inspection')
        self.accept(attempt=fresh)
        self.assertTrue(self.j.begin(DIGEST, 'A', 'save'))

    def test_crash_intent_survives_process_exit_and_old_result_is_rejected(self):
        script = """import os,sys
from h3c_journal import Journal
j=Journal(sys.argv[1]); j.begin(sys.argv[2], 'A', 'apply'); os._exit(0)
"""
        subprocess.run([sys.executable, '-c', script, str(self.path), DIGEST],
                       cwd=Path(__file__).resolve().parents[1] / 'scripts', check=True)
        recovered = Journal(self.path)
        self.addCleanup(recovered.close)
        old = recovered.snapshot()['targets']['A']['attempt']
        with self.assertRaises(GateError):
            recovered.begin(DIGEST, 'A', 'apply')
        fresh = recovered.reconcile(DIGEST, 'A', old, 'applied', 'new-session-inspection')
        with self.assertRaises(GateError):
            recovered.finish(DIGEST, 'A', old, 'success', 'late-worker-result')
        with self.assertRaises(GateError):
            recovered.check(DIGEST, 'A', old, 'business', True, 'old-evidence')
        self.accept(attempt=fresh)

    def test_save_timeout_requires_fresh_inspection_and_acceptance(self):
        self.accept()
        attempt = self.j.begin(DIGEST, 'A', 'save')
        self.j.finish(DIGEST, 'A', attempt, 'unknown', 'disconnected')
        with self.assertRaises(GateError):
            self.j.begin(DIGEST, 'A', 'save')
        fresh = self.j.reconcile(DIGEST, 'A', attempt, 'saved', 'startup-and-identity-inspection')
        with self.assertRaises(GateError):
            self.j.begin(DIGEST, 'B', 'apply')
        self.accept(attempt=fresh)
        self.assertEqual(self.j.snapshot()['targets']['A']['state'], 'SAVED')
        with self.assertRaises(GateError):
            self.j.begin(DIGEST, 'A', 'save')
        self.assertTrue(self.j.begin(DIGEST, 'B', 'apply'))

    def test_not_sent_after_inspection_can_retry_with_new_id(self):
        attempt = self.j.begin(DIGEST, 'A', 'apply')
        self.j.finish(DIGEST, 'A', attempt, 'failed', 'rejected')
        self.j.reconcile(DIGEST, 'A', attempt, 'not_applied', 'baseline-and-startup-inspection')
        self.assertNotEqual(attempt, self.j.begin(DIGEST, 'A', 'apply'))

    def test_competing_connections_only_one_commits_intent(self):
        def begin():
            journal = Journal(self.path)
            try:
                try:
                    return bool(journal.begin(DIGEST, 'A', 'apply'))
                except GateError:
                    return False
            finally:
                journal.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: begin(), range(2)))
        self.assertEqual(sorted(results), [False, True])

    def test_scope_attempt_and_check_rejections_leave_no_events(self):
        initial = self.j.snapshot()
        for digest, target, operation in [('b' * 64, 'A', 'apply'), (DIGEST, 'C', 'apply'),
                                           (DIGEST, 'A', 'save'), (DIGEST, 'A', 'rollback')]:
            with self.assertRaises(GateError):
                self.j.begin(digest, target, operation)
            self.assertEqual(self.j.snapshot(), initial)
        attempt = self.apply()
        initial = self.j.snapshot()
        for candidate, check_id, passed in [('old', 'business', True), (attempt, 'ping-only', True),
                                             (attempt, 'business', 'true')]:
            with self.assertRaises(GateError):
                self.j.check(DIGEST, 'A', candidate, check_id, passed, 'evidence')
            self.assertEqual(self.j.snapshot(), initial)

    def test_do_not_save_allows_next_wave_after_acceptance(self):
        scope = copy.deepcopy(SCOPE)
        scope['persistence'] = 'do_not_save'
        journal = Journal.create(Path(self.temp.name) / 'no-save.sqlite', scope)
        self.addCleanup(journal.close)
        attempt = journal.begin(DIGEST, 'A', 'apply')
        journal.finish(DIGEST, 'A', attempt, 'success', 'apply')
        for check in scope['checks']['A']:
            journal.check(DIGEST, 'A', attempt, check, True, 'observation')
        with self.assertRaises(GateError):
            journal.begin(DIGEST, 'A', 'save')
        self.assertTrue(journal.begin(DIGEST, 'B', 'apply'))

    def test_invalid_scope_and_existing_file_fail_before_overwrite(self):
        initial = self.j.snapshot()
        with self.assertRaises(FileExistsError):
            Journal.create(self.path, SCOPE)
        for change in [{'persistence': 'separate_approval'}, {'waves': [['A', 'A'], ['B']]},
                       {'checks': {'A': [], 'B': ['business']}}, {'plan_sha256': 'bad'}]:
            scope = {**copy.deepcopy(SCOPE), **change}
            with self.assertRaises(GateError):
                Journal.create(Path(self.temp.name) / 'invalid.sqlite', scope)
        self.assertFalse((Path(self.temp.name) / 'invalid.sqlite').exists())
        self.assertEqual(self.j.snapshot(), initial)

    def test_cli_reports_durable_state(self):
        self.apply()
        result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'scripts/h3c_journal.py'),
                                 str(self.path)], check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)['targets']['A']['state'], 'APPLIED')


if __name__ == '__main__':
    unittest.main()

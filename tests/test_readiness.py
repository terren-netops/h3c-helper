"""Offline host discovery and actionable handoff errors; no device/network mocks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import h3c_engineering as engineering
import h3c_preflight as preflight


def handoff_record():
    return {'kind':'handoff','schema_version':'1','case_id':'CASE','status':'UNKNOWN',
            'facts':[{'id':'F','category':'observation','text':'Constructed observation.',
                      'source_ref':'local:1','visibility':['customer','tac','engineer'],
                      'redaction_reviewed':True}]}


class Readiness(unittest.TestCase):
    def test_host_inventory_is_not_device_readiness(self):
        result = subprocess.run([sys.executable, str(ROOT/'scripts/h3c_preflight.py')],
                                capture_output=True, text=True, check=True)
        report = json.loads(result.stdout)
        self.assertFalse(report['execution_authorized'])
        self.assertFalse(report['bundled_device_executor'])
        self.assertEqual(report['external_runner'], 'not_assessed')
        self.assertIn('device_reachability', report['not_checked'])
        self.assertEqual(Path(report['python']['executable']).resolve(), Path(sys.executable).resolve())
        self.assertIsNone(preflight.package_version('h3c-helper-nonexistent-test-distribution-928'))

    def test_chinese_labels_preserve_facts_and_status(self):
        record = handoff_record()
        record['facts'] = [{**record['facts'][0], 'id':str(i), 'category':category}
                           for i,category in enumerate(['observation','hypothesis','action','next_step','limitation'])]
        text = engineering.handoff(record, 'customer', 'zh')
        for label in ('客户 交接草稿', '[观察]', '[假设]', '[操作]', '[下一步]', '[限制]'):
            self.assertIn(label, text)
        self.assertIn('UNKNOWN', text)
        self.assertIn('Constructed observation.', text)
        self.assertNotIn('local:1', text)
        self.assertIn('[observation]', engineering.handoff(record, 'customer', 'en'))

    def test_handoff_cli_actionable_errors_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='h3c space 测试 ') as directory:
            root = Path(directory)
            source, output = root/'facts.json', root/'handoff.md'
            command = [sys.executable, str(ROOT/'scripts/h3c_engineering.py'), 'handoff',
                       str(source), '--audience', 'customer', '--output', str(output)]
            for expected in ('redaction_review_missing', 'sensitive_marker_requires_review', 'invalid_handoff'):
                record = handoff_record()
                if expected == 'redaction_review_missing':
                    record['facts'][0]['redaction_reviewed'] = False
                elif expected == 'sensitive_marker_requires_review':
                    record['facts'][0]['text'] = 'password PRIVATE_TEST_VALUE'
                else:
                    record['status'] = 'PRIVATE_TEST_VALUE'
                source.write_text(json.dumps(record), encoding='utf-8')
                run = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                report = json.loads(run.stdout)
                self.assertEqual(report['code'], expected)
                self.assertEqual(report['error'], 'invalid_input_or_review_required_or_output_exists')
                self.assertFalse(report['execution_authorized'])
                self.assertNotIn('PRIVATE_TEST_VALUE', run.stdout + run.stderr)
                self.assertFalse(output.exists())
            source.write_text(json.dumps(handoff_record()), encoding='utf-8')
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            before = output.read_bytes()
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)['code'], 'output_exists')
            self.assertEqual(output.read_bytes(), before)

    def test_bad_json_and_missing_paths_do_not_leak(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'PRIVATE_TEST_VALUE.json'
            command = [sys.executable, str(ROOT/'scripts/h3c_engineering.py'), 'resilience', str(source)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(json.loads(run.stdout)['code'], 'path_not_found')
            for data in (b'{"PRIVATE_TEST_VALUE":broken}', b'\xff'):
                source.write_bytes(data)
                run = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(json.loads(run.stdout)['code'], 'invalid_input')
                self.assertNotIn('PRIVATE_TEST_VALUE', run.stdout + run.stderr)
                self.assertNotIn('Traceback', run.stderr)


if __name__ == '__main__':
    unittest.main()

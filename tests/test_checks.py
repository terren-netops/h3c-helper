"""Constructed local cases; these do not emulate or validate real devices."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('h3c_check', ROOT/'scripts/h3c_check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def network():
    return {'kind':'network','schema_version':'1','devices':[
        {'id':n,'ports':['1','2','3'],'combo_groups':[['2','3']],
         'poe_budget_w':100,'poe_load_w':50,'quantity':1} for n in ('A','B','C')],
        'links':[{'id':'L1','a':{'device':'A','port':'1'},'b':{'device':'B','port':'1'},'speed_gbps':10}],
        'subnets':[{'id':'N1','vrf':'main','cidr':'192.0.2.0/24'}],
        'quotes':[{'id':'Q1','currency':'USD','tax_basis':'exclusive','quantity':3,'unit_price':0.1,
                   'total':0.3,'source':'constructed fixture','valid_until':'2099-01-01'}]}


def change():
    return {'kind':'change','schema_version':'1','id':'fixture','status':'DRAFT',
            'plan':{'targets':[{'id':'A','model':'TEST','release':'TEST', 'snapshot_sha256':'a'*64,'diff':'fixture only'}],
                    'impact':'fixture','window':'fixture','preconditions':[{'id':'p','status':'pending','evidence':'not verified'}],
                    'verification':['business probe'],'stop_conditions':['probe fails'],
                    'recovery':{'method':'fixture','access':'fixture','evidence':'not verified','verified':False},
                    'persistence':'do_not_save'}}


class Checks(unittest.TestCase):
    def test_valid_network(self):
        self.assertEqual(checker.validate(network()), [])

    def test_network_invariants(self):
        cases=[]
        n=network();n['devices'][0]['poe_load_w']=101;cases.append((n,'poe_budget_exceeded'))
        n=network();n['quotes'][0]['total']=0.4;cases.append((n,'quote_arithmetic_mismatch'))
        n=network();n['links'].append(copy.deepcopy(n['links'][0]));cases.append((n,'port_reused'))
        n=network();n['links'][0]['b']['device']='missing';cases.append((n,'unknown_endpoint'))
        n=network();n['devices'][0]['ports'].append('1');cases.append((n,'duplicate_declared_port'))
        n=network();n['devices'][0]['combo_groups']=[['2','missing']];cases.append((n,'invalid_combo_group'))
        n=network();n['subnets'].append({'id':'N2','vrf':'main','cidr':'192.0.2.128/25'});cases.append((n,'subnet_overlap'))
        n=network();n['subnets'][0]['cidr']='192.0.2.1/24';cases.append((n,'invalid_subnet'))
        n=network();n['links'][0]['a']['port']='2';n['links'].append({'id':'L2','a':{'device':'A','port':'3'},'b':{'device':'C','port':'1'},'speed_gbps':1});cases.append((n,'combo_conflict'))
        for data,code in cases:
            with self.subTest(code=code):self.assertIn(code,checker.validate(data))

    def test_vrf_overlap_allowed(self):
        n=network();n['subnets'].append({'id':'N2','vrf':'separate','cidr':'192.0.2.0/24'})
        self.assertEqual(checker.validate(n),[])

    def test_draft_not_ready(self):
        c=change();self.assertEqual(checker.validate(c),[])
        c['status']='READY';self.assertIn('preconditions_not_passed',checker.validate(c))
        self.assertIn('recovery_not_verified',checker.validate(c))

    def test_unknown_preserves_missing_preconditions(self):
        c=change();c['status']='UNKNOWN'
        self.assertEqual(checker.validate(c),[])
        c['status']='ROLLBACK_FAILED'
        self.assertEqual(checker.validate(c),[])

    def authorized(self):
        c=change();c['plan']['preconditions'][0].update(status='pass',evidence='fixture check')
        c['plan']['recovery'].update(verified=True,evidence='fixture check')
        c['status']='AUTHORIZED';c['authorization']={'record':'fixture','actor':'fixture','plan_sha256':checker.plan_digest(c)}
        return c

    def test_authorization_and_drift(self):
        c=self.authorized();self.assertEqual(checker.validate(c),[])
        c['plan']['targets'][0]['diff']='changed';self.assertIn('authorization_plan_mismatch',checker.validate(c))
        del c['authorization'];self.assertIn('authorization_record_missing',checker.validate(c))

    def test_acceptance_and_rollback(self):
        c=self.authorized();c['status']='ACCEPTED';self.assertIn('acceptance_incomplete',checker.validate(c))
        c['results']=[{'target':'A','result':'pass','evidence':'fixture','running':'changed','startup':'unchanged'}]
        self.assertEqual(checker.validate(c),[])
        c['results'][0]['startup']='saved';self.assertIn('persistence_scope_mismatch',checker.validate(c))
        c['results'][0]['startup']='unknown';self.assertIn('acceptance_incomplete',checker.validate(c))
        c['status']='ROLLED_BACK';self.assertIn('rollback_evidence_incomplete',checker.validate(c))
        c['results'][0].update(running='unchanged',startup='unchanged');self.assertEqual(checker.validate(c),[])

    def test_schema_rejects_unknown_and_boolean_quantity(self):
        n=network();n['devices'][0]['quantity']=True;self.assertIn('schema:type',checker.validate(n))
        n=network();n['extra']='private value';self.assertEqual(checker.validate(n),['schema:additionalProperties'])
        self.assertEqual(checker.validate([]),['unknown_record_kind'])

    def test_render_escaping_consistency_and_no_overwrite(self):
        n=network();n['links'][0]['id']='<script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'topology.html';result=checker.render(n,output);page=output.read_text()
            self.assertEqual(result['links'],1);self.assertEqual(result['devices'],3)
            self.assertIn('<html lang="en">',page);self.assertIn('Physical connection review',page)
            self.assertNotIn('<script>',page);self.assertIn('&lt;script&gt;',page)
            self.assertEqual(page.count('<path '),1);self.assertIn('<td>A</td><td>1</td><td>B</td>',page)
            with self.assertRaises(FileExistsError):checker.render(n,output)

    def test_evidence_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'root';root.mkdir();f=root/'source.txt';f.write_text('constructed evidence')
            now=datetime.now(timezone.utc)
            r={'id':'E1','scope':'customer-a','classification':'customer','title':'VLAN reference',
               'source_url':'https://example.org/fixture','section':'1','model':'TEST','release':'TEST',
               'retrieved_at':(now-timedelta(days=1)).isoformat(),'valid_until':(now+timedelta(days=1)).isoformat(),
               'verification':'document','relative_path':'source.txt','sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
            data={'kind':'evidence','schema_version':'1','records':[r]}
            self.assertEqual(checker.validate(data),[])
            self.assertEqual(len(checker.search(data,root,'customer-a','VLAN')['matches']),1)
            self.assertEqual(checker.search(data,root,'customer-b','VLAN')['matches'],[])
            self.assertEqual(checker.search(data,root,'customer-a','VLAN',release='OTHER')['matches'],[])
            for field,value,reason in [('sha256','0'*64,'hash_mismatch'),('verification','pending','verification_pending'),
                                      ('valid_until',(now-timedelta(seconds=1)).isoformat(),'expired')]:
                bad=copy.deepcopy(data);bad['records'][0][field]=value
                self.assertEqual(checker.search(bad,root,'customer-a','VLAN')['rejected'][0]['reason'],reason)
            outside=Path(directory)/'outside.txt';outside.write_text('constructed evidence')
            for path in ('../outside.txt',str(outside)):
                bad=copy.deepcopy(data);bad['records'][0]['relative_path']=path
                self.assertEqual(checker.search(bad,root,'customer-a','VLAN')['matches'],[])
            r['scope']='public';self.assertIn('classification_scope_mismatch',checker.validate(data))

    def test_evidence_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'root';root.mkdir()
            outside=Path(directory)/'outside.txt';outside.write_text('constructed evidence')
            try:
                (root/'link').symlink_to(outside)
            except OSError as error:
                if sys.platform=='win32' and getattr(error,'winerror',None)==1314:
                    self.skipTest('Windows symlink privilege unavailable; boundary test remains unverified')
                raise
            now=datetime.now(timezone.utc)
            record={'id':'E1','scope':'customer-a','classification':'customer','title':'VLAN',
                    'source_url':'https://example.org/fixture','section':'1','model':'TEST','release':'TEST',
                    'retrieved_at':(now-timedelta(days=1)).isoformat(),
                    'valid_until':(now+timedelta(days=1)).isoformat(),'verification':'document',
                    'relative_path':'link','sha256':hashlib.sha256(outside.read_bytes()).hexdigest()}
            result=checker.search({'kind':'evidence','schema_version':'1','records':[record]},root,'customer-a','VLAN')
            self.assertEqual(result['matches'],[])
            self.assertEqual(result['rejected'][0]['reason'],'path_outside_root_or_not_file')

    def test_cli_rejects_malformed_without_leaking(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'input.json'
            for raw in ('{"secret":"PRIVATE_VALUE", "kind":"unknown"}', '[1]', '{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}', '{broken'):
                p.write_text(raw)
                result=subprocess.run([sys.executable,str(ROOT/'scripts/h3c_check.py'),'digest',str(p)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2);self.assertNotIn('PRIVATE_VALUE',result.stdout)
                self.assertFalse(json.loads(result.stdout)['execution_authorized']);self.assertNotIn('Traceback',result.stderr)


if __name__=='__main__':unittest.main()

"""Constructed parser fixtures and offline edge cases; no device validation."""
import copy
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import h3c_check as checker
import h3c_profile as profile
import h3c_engineering as engineering
import test_checks as fixtures
network = fixtures.network
change = fixtures.change


class Engineering(unittest.TestCase):
    def test_separate_save_approval(self):
        c=fixtures.Checks().authorized();c['plan']['persistence']='separate_approval'
        c['authorization']['plan_sha256']=checker.plan_digest(c);c['status']='ACCEPTED'
        c['results']=[{'target':'A','result':'pass','evidence':'fixture','running':'changed','startup':'saved'}]
        self.assertIn('save_authorization_missing',checker.validate(c))
        c['save_authorization']={**c['authorization'],'record':'separate fixture approval','targets':['A']}
        self.assertEqual(checker.validate(c),[])
        for key,value in [('targets',['B']),('plan_sha256','f'*64),('targets',['A','A'])]:
            invalid=copy.deepcopy(c);invalid['save_authorization'][key]=value
            self.assertIn('save_authorization_scope_mismatch',checker.validate(invalid))
        c['plan']['persistence']='save_after_acceptance';c.pop('save_authorization');c['authorization']['plan_sha256']=checker.plan_digest(c);c['status']='VERIFYING'
        self.assertIn('save_before_acceptance',checker.validate(c))

    def test_quote_date_and_safe_paths(self):
        n=network();n['quotes'][0]['valid_until']='2025-01-01'
        report=checker.review(n,date(2026,9,20));self.assertTrue(report['record_valid'])
        self.assertEqual(report['warnings'][0]['code'],'quote_expired');self.assertEqual(report['engineering_status'],'needs_review')
        self.assertEqual(checker.review(n,date(2025,1,1))['warnings'],[])
        n['devices'][1]['quantity']='PRIVATE_VALUE'
        report=checker.review(n,date(2026,9,20));self.assertFalse(report['valid'])
        self.assertEqual(report['diagnostics'][0]['path'],'/devices/1/quantity')
        self.assertNotIn('PRIVATE_VALUE',json.dumps(report))
        n=network();n['SECRET_PROPERTY']='PRIVATE_VALUE';report=checker.review(n)
        self.assertNotIn('SECRET_PROPERTY',json.dumps(report))

    def test_poe_ports_and_failure_budget(self):
        n=network();d=n['devices'][0]
        d['poe_ports']=[{'port':'1','load_w':40,'limit_w':30,'required_standard':'at','supported_standards':['af']}]
        d['poe_failure_budget_w']=45
        errors=checker.validate(n)
        self.assertTrue({'poe_port_limit_exceeded','poe_standard_mismatch','poe_failure_budget_exceeded'}<=set(errors))
        d['poe_ports'][0].update(limit_w=60,supported_standards=['af','at']);d['poe_failure_budget_w']=100
        self.assertEqual(checker.validate(n),[])

    def test_constructed_interface_state(self):
        # Synthetic protocol-format fixture, not captured device output.
        raw=b'<Sysname> display interface bridge-aggregation 9\nBridge-Aggregation9\nCurrent state: DOWN\nLine protocol state: DOWN\n'
        result=profile.extract(raw);facts=result['devices'][0]['facts']
        state=next(f for f in facts if f['field']=='interface_state')
        self.assertEqual(state['value'],{'port':'Bridge-Aggregation9','state':'DOWN'})
        self.assertEqual(state['line_start'],3)
        self.assertTrue(any(w['code']=='generic_prompt_device_identity_unconfirmed' for w in result['warnings']))

    def test_constructed_feature_version_line(self):
        # Synthetic version/release identifiers; tests the Feature token only.
        raw=b'<Sysname> display version\nH3C Comware Software, Version 7.9.999, Feature 9999\n'
        result=profile.extract(raw)
        self.assertEqual(result['devices'][0]['facts'][0]['value']['release'],'9999')

    def test_constructed_multiple_devices_and_context(self):
        raw=b'''<SW-A> display version
H3C Comware Software, Version 7.1.070, Release 1234P01
H3C TEST-A uptime is 1 week, 0 days
<SW-A> display current-configuration
interface GigabitEthernet1/0/1
 port link-type trunk
 port trunk pvid vlan 20
 ip address 192.0.2.1 255.255.255.0
#
 password cipher PRIVATE_VALUE
<SW-A> display link-aggregation verbose
Aggregate Interface: Bridge-Aggregation1
GE1/0/1 S 32768 1
GE1/0/2 U 32768 2
<SW-B> display version
H3C Comware Software, Version 7.1.070, Release 5678P01
H3C TEST-B uptime is 2 weeks, 0 days
--More--
'''
        result=profile.extract(raw);self.assertEqual(len(result['devices']),2)
        self.assertNotIn('PRIVATE_VALUE',json.dumps(result));self.assertNotIn('SW-A',json.dumps(result))
        a=result['devices'][0]['facts'];b=result['devices'][1]['facts']
        self.assertEqual([f['value']['state'] for f in a if f['field']=='aggregation_member'],['selected','unselected'])
        self.assertFalse(any(f['field']=='interface' for f in b))
        self.assertEqual(next(f['value']['address'] for f in a if f['field']=='interface_address'),'192.0.2.1/24')
        self.assertEqual(result['source_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertTrue(result['warnings'])

    def test_conflict_unknown_and_truncation(self):
        raw=b'''<SW> display version
H3C Comware Software, Version 7.1.070, Release 1111
H3C Comware Software, Version 7.1.070, Release 2222
H3C TEST uptime is 1 day
[truncated]
'''
        r=profile.extract(raw);self.assertIn('conflicting_software_do_not_merge',r['devices'][0]['gaps'])
        r=profile.extract(b'H3C Comware Software, Version 9.1.058, Demo 9301\n')
        self.assertTrue(r['fragment_only']);self.assertIn('missing_software',r['devices'][0]['gaps'])
        with self.assertRaises(UnicodeError):profile.extract(b'\xff')

    def topology(self):
        n=network();n['devices'].append({**copy.deepcopy(n['devices'][0]),'id':'D'})
        pairs=[('A','1','B','1'),('B','2','D','1'),('A','2','C','1'),('C','2','D','2')]
        n['links']=[{'id':f'L{i}','a':{'device':a,'port':ap},'b':{'device':b,'port':bp},'speed_gbps':10,'forwarding_state':'forwarding'} for i,(a,ap,b,bp) in enumerate(pairs)]
        n['resilience']={'assumptions':'Constructed undirected forwarding links; one splittable demand at a time.',
                         'demands':[{'id':'A-D','source':'A','destination':'D','min_gbps':15}],
                         'scenarios':[{'id':'lose-B','remove_devices':['B'],'remove_links':[]},
                                      {'id':'lose-A','remove_devices':['A'],'remove_links':[]}]}
        return n

    def test_resilience_capacity_and_failures(self):
        n=self.topology();self.assertEqual(checker.validate(n),[])
        results=engineering.resilience(n)['results']
        self.assertEqual([r['max_aggregate_gbps'] for r in results],[20,10,0])
        self.assertEqual([r['meets_declared_demand'] for r in results],[True,False,False])
        self.assertTrue(results[2]['endpoint_removed'])

    def test_unknown_forwarding_and_bad_targets(self):
        n=self.topology();n['links'][0].pop('forwarding_state')
        self.assertEqual(engineering.resilience(n)['status'],'not_evaluated')
        n=self.topology();n['resilience']['scenarios'][0]['remove_devices']=['MISSING']
        self.assertIn('unknown_failure_target',checker.validate(n))
        with self.assertRaises(ValueError):engineering.resilience(n)
        self.assertEqual(engineering.resilience(network())['status'],'not_evaluated')
        n=self.topology();n['resilience']['scenarios'][0]['id']='baseline'
        self.assertIn('reserved_scenario_id',checker.validate(n))
        n=self.topology()
        for link in n['links']:link['speed_gbps']=1e308
        with self.assertRaises(ValueError):engineering.resilience(n)

    def test_handoff_visibility_review_and_literals(self):
        d={'kind':'handoff','schema_version':'1','case_id':'TEST-CASE','status':'UNKNOWN','facts':[
            {'id':'public','category':'observation','text':'Request timed out; receipt unknown.','source_ref':'internal/source:7','visibility':['engineer','tac','customer'],'redaction_reviewed':True},
            {'id':'private','category':'hypothesis','text':'Internal hypothesis only','source_ref':'internal/source:9','visibility':['engineer'],'redaction_reviewed':False}]}
        customer=engineering.handoff(d,'customer');engineer=engineering.handoff(d,'engineer')
        self.assertNotIn('Internal hypothesis',customer);self.assertNotIn('internal/source',customer)
        self.assertIn('Internal hypothesis',engineer);self.assertIn('DRAFT',customer);self.assertIn('not sent',customer)
        self.assertIn('not sent',engineering.handoff(d,'customer','en'))
        self.assertIn('未发送',engineering.handoff(d,'customer','zh'))
        d['facts'][0]['redaction_reviewed']=False
        with self.assertRaises(ValueError):engineering.handoff(d,'customer')
        d['facts'][0].update(redaction_reviewed=True,text='password PRIVATE_VALUE')
        with self.assertRaises(ValueError):engineering.handoff(d,'tac')
        d['facts'][0]['text']='![image](https://example.org/leak)\n# spoof'
        content=engineering.handoff(d,'customer');self.assertNotIn('![image]',content);self.assertNotIn('\n# spoof',content)

    def test_alias_candidates_never_confirm_applicability(self):
        with tempfile.TemporaryDirectory() as directory:
            f=Path(directory)/'source.txt';f.write_text('constructed source');now=datetime.now(timezone.utc)
            record={'id':'E','scope':'public','classification':'public','title':'VLAN','source_url':'https://example.org/fixture',
                    'section':'1','model':'TEST-A','aliases':['TEST-family'],'release':'R1','retrieved_at':(now-timedelta(days=1)).isoformat(),
                    'valid_until':(now+timedelta(days=1)).isoformat(),'verification':'document','relative_path':f.name,
                    'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
            d={'kind':'evidence','schema_version':'1','records':[record]}
            self.assertEqual(checker.search(d,directory,'public','VLAN',model='TEST-family')['matches'],[])
            result=checker.search(d,directory,'public','VLAN',model='TEST-family',candidates=True)['matches'][0]
            self.assertEqual(result['match_type'],'alias_candidate');self.assertFalse(result['applicability_confirmed'])
            self.assertEqual(checker.search(d,directory,'public','VLAN',model='TEST-family',release='R2',candidates=True)['matches'],[])


if __name__=='__main__':unittest.main()

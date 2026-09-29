#!/usr/bin/env python3
"""Offline declared-topology checks and audience-specific draft handoff."""
import argparse
from collections import deque
import json
import math
from pathlib import Path
import re
import sys
from h3c_check import load, validate


def max_flow(devices, links, source, sink):
    capacity={node:{} for node in devices}
    for link in links:
        a,b=link['a']['device'],link['b']['device'];value=link['speed_gbps']
        capacity[a][b]=capacity[a].get(b,0)+value
        capacity[b][a]=capacity[b].get(a,0)+value
        if not math.isfinite(capacity[a][b]) or not math.isfinite(capacity[b][a]):
            raise ValueError('capacity_overflow')
    total=0
    while True:
        parent={source:None};queue=deque([source])
        while queue and sink not in parent:
            node=queue.popleft()
            for neighbor,available in capacity[node].items():
                if available>0 and neighbor not in parent:
                    parent[neighbor]=node;queue.append(neighbor)
        if sink not in parent:return total
        amount=float('inf');node=sink
        while parent[node] is not None:
            previous=parent[node];amount=min(amount,capacity[previous][node]);node=previous
        node=sink
        while parent[node] is not None:
            previous=parent[node];capacity[previous][node]-=amount
            capacity[node][previous]=capacity[node].get(previous,0)+amount;node=previous
        total+=amount
        if not math.isfinite(total):
            raise ValueError('capacity_overflow')


def resilience(data):
    errors=validate(data)
    if errors or not isinstance(data,dict) or data.get('kind')!='network':raise ValueError('invalid_network_record')
    model=data.get('resilience')
    if model is None:return {'status':'not_evaluated','reason':'resilience_model_missing','execution_authorized':False}
    if any(link.get('forwarding_state','unknown')=='unknown' for link in data['links']):
        return {'status':'not_evaluated','reason':'forwarding_state_unknown','execution_authorized':False}
    devices={d['id'] for d in data['devices']};rows=[]
    scenarios=[{'id':'baseline','remove_devices':[],'remove_links':[]}]+model['scenarios']
    for scenario in scenarios:
        remaining=devices-set(scenario['remove_devices'])
        links=[link for link in data['links'] if link['id'] not in scenario['remove_links']
               and link['a']['device'] in remaining and link['b']['device'] in remaining
               and link['forwarding_state']=='forwarding']
        for demand in model['demands']:
            missing=demand['source'] not in remaining or demand['destination'] not in remaining
            flow=0 if missing else max_flow(remaining,links,demand['source'],demand['destination'])
            rows.append({'scenario':scenario['id'],'demand':demand['id'],
                         'max_aggregate_gbps':flow,'required_gbps':demand['min_gbps'],
                         'meets_declared_demand':not missing and flow>=demand['min_gbps'],
                         'endpoint_removed':missing})
    return {'status':'modeled','results':rows,'execution_authorized':False,
            'limitations':['independent_demands_not_simultaneous_traffic','splittable_aggregate_flow_not_single_flow',
                          'declared_forwarding_no_protocol_convergence','no_device_or_sla_validation']}


SECRET=re.compile(r'(?i)(password|passwd|community|private.key|pre.shared.key|-----BEGIN|\b(?:sk|AKIA)-[A-Za-z0-9]{8,})')
def literal(value):
    # Escape Markdown constructs that could load media or hide text in HTML.
    return re.sub(r'([\\`*_{}\[\]()<>!#|])',r'\\\1',value.replace('\r', ' ').replace('\n', ' '))


def handoff(data,audience,language="en"):
    if validate(data) or not isinstance(data,dict) or data.get('kind')!='handoff':raise ValueError('invalid_handoff')
    facts=[f for f in data['facts'] if audience in f['visibility']]
    if not facts:raise ValueError('no_visible_facts')
    if audience!='engineer':
        if any(not f['redaction_reviewed'] for f in facts):raise ValueError('redaction_review_missing')
        text=data['case_id']+' '+ ' '.join(f['text']+' '+f['source_ref'] for f in facts)
        if SECRET.search(text):raise ValueError('sensitive_marker_requires_review')
    labels = {'zh': ('交接草稿', '案件', '记录状态', '本地生成，未发送。', '来源'),
              'en': ('handoff draft', 'Case', 'Recorded status', 'Generated locally; not sent.', 'Source')}
    title, case_label, status_label, notice, source_label = labels[language]
    audience_label = {'engineer':'工程师','tac':'TAC','customer':'客户'}[audience] if language=='zh' else audience
    categories = {'observation':'观察','hypothesis':'假设','action':'操作','next_step':'下一步','limitation':'限制'}
    lines=[f'# {audience_label} {title} — DRAFT',f'{case_label}: {literal(data["case_id"])}',
           f'{status_label}: {data["status"]}', notice,'']
    for f in facts:
        category = categories[f['category']] if language=='zh' else f['category']
        lines.append(f'- [{category}] {literal(f["text"])}')
        if audience!='customer':lines.append('  '+source_label+': '+literal(f['source_ref']))
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('resilience');p.add_argument('input')
    p=sub.add_parser('handoff');p.add_argument('input');p.add_argument('--audience',choices=['engineer','tac','customer'],required=True);p.add_argument('--output',required=True)
    sub.choices['handoff'].add_argument('--language',choices=['zh','en'],default='en')
    args=parser.parse_args()
    try:
        data=load(args.input)
        if args.command=='resilience':result=resilience(data)
        else:
            content=handoff(data,args.audience,args.language)
            with Path(args.output).open('x',encoding='utf-8') as target:target.write(content)
            result={'status':'draft_created','audience':args.audience,'execution_authorized':False}
        print(json.dumps(result,ensure_ascii=False));return 0
    except ImportError:
        print(json.dumps({'error':'requires_jsonschema_4','execution_authorized':False}));return 3
    except (ValueError,OSError,TypeError,RecursionError) as error:
        # Retain the legacy error field; expose only allowlisted detail, never raw input or paths.
        known = {'invalid_handoff','no_visible_facts','redaction_review_missing',
                 'sensitive_marker_requires_review','invalid_network_record','capacity_overflow',
                 'input_too_large','duplicate_json_key','nonfinite_number'}
        if isinstance(error, FileExistsError):
            code = 'output_exists'
        elif isinstance(error, FileNotFoundError):
            code = 'path_not_found'
        elif isinstance(error, PermissionError):
            code = 'permission_denied'
        elif isinstance(error, OSError):
            code = 'file_io_error'
        else:
            code = str(error) if str(error) in known else 'invalid_input'
        print(json.dumps({'error':'invalid_input_or_review_required_or_output_exists',
                          'code':code,'execution_authorized':False}));return 2


if __name__=='__main__':sys.exit(main())

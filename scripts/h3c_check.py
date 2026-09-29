#!/usr/bin/env python3
"""Offline record checks. Never grants execution authority or contacts devices."""
import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import html
import ipaddress
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 8 * 1024 * 1024


def load(path):
    if Path(path).stat().st_size > MAX_BYTES:
        raise ValueError('input_too_large')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate_json_key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('nonfinite_number')
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('nonfinite_number')
        return number
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=pairs, parse_constant=invalid_constant, parse_float=finite_float)


def plan_digest(record):
    payload = json.dumps(record['plan'], sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def duplicates(values):
    seen = set()
    for value in values:
        if value in seen:
            return True
        seen.add(value)
    return False


def validate(data, details=None):
    from jsonschema import Draft202012Validator, FormatChecker
    kind = data.get('kind') if isinstance(data, dict) else None
    if kind not in ('change', 'network', 'evidence', 'handoff'):
        return ['unknown_record_kind']
    schema = load(ROOT / 'schemas' / (kind + '.schema.json'))
    errors = []
    for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data):
        # Do not echo input values, property names or secrets into diagnostic logs.
        code = 'schema:' + error.validator
        errors.append(code)
        if details is not None:
            node, safe = schema, []
            for part in error.absolute_path:
                if isinstance(part, int) and 'items' in node:
                    safe.append(str(part)); node = node['items']
                elif part in node.get('properties', {}):
                    safe.append(part); node = node['properties'][part]
                else:
                    break
            details.append({'code': code, 'path': '/' + '/'.join(safe),
                            'hint': 'Check field against schema; input value omitted.'})
    if errors:
        return sorted(set(errors))
    if kind == 'change':
        plan = data['plan']
        ids = [t['id'] for t in plan['targets']]
        if duplicates(ids) or duplicates(c['id'] for c in plan['preconditions']):
            errors.append('duplicate_change_id')
        if data['status'] in {'READY', 'AUTHORIZED', 'APPLYING', 'VERIFYING', 'ACCEPTED'}:
            if not all(c['status'] == 'pass' for c in plan['preconditions']):
                errors.append('preconditions_not_passed')
            if not plan['recovery']['verified']:
                errors.append('recovery_not_verified')
        authorized_states = {'AUTHORIZED', 'APPLYING', 'VERIFYING', 'ACCEPTED'}
        if data['status'] in authorized_states and 'authorization' not in data:
            errors.append('authorization_record_missing')
        if 'authorization' in data and data['authorization']['plan_sha256'] != plan_digest(data):
            errors.append('authorization_plan_mismatch')
        results = data.get('results', [])
        if duplicates(r['target'] for r in results) or any(r['target'] not in ids for r in results):
            errors.append('result_targets_invalid')
        if data['status'] == 'ACCEPTED':
            if set(r['target'] for r in results) != set(ids) or any(
                    r['result'] != 'pass' or r['running'] == 'unknown' or r['startup'] == 'unknown'
                    for r in results):
                errors.append('acceptance_incomplete')
        if plan['persistence'] == 'do_not_save' and any(r['startup'] == 'saved' for r in results):
            errors.append('persistence_scope_mismatch')
        saved = {r['target'] for r in results if r['startup'] == 'saved'}
        approval = data.get('save_authorization')
        if plan['persistence'] == 'separate_approval' and saved and not approval:
            errors.append('save_authorization_missing')
        if approval:
            if (approval['plan_sha256'] != plan_digest(data)
                    or duplicates(approval['targets'])
                    or not set(approval['targets']) <= set(ids)
                    or not saved <= set(approval['targets'])):
                errors.append('save_authorization_scope_mismatch')
        if plan['persistence'] == 'save_after_acceptance' and saved and data['status'] != 'ACCEPTED':
            errors.append('save_before_acceptance')
        if data['status'] == 'ROLLED_BACK':
            if set(r['target'] for r in results) != set(ids) or any(
                    r['result'] != 'pass' or r['running'] != 'unchanged' or r['startup'] != 'unchanged'
                    for r in results):
                errors.append('rollback_evidence_incomplete')
    elif kind == 'network':
        devices = {d['id']: d for d in data['devices']}
        for field in ('devices', 'links', 'subnets', 'quotes'):
            if duplicates(x['id'] for x in data[field]):
                errors.append('duplicate_' + field + '_id')
        for d in data['devices']:
            if duplicates(d['ports']):
                errors.append('duplicate_declared_port')
            if any(duplicates(g) or not set(g) <= set(d['ports']) for g in d['combo_groups']):
                errors.append('invalid_combo_group')
            if Decimal(str(d['poe_load_w'])) > Decimal(str(d['poe_budget_w'])):
                errors.append('poe_budget_exceeded')
        used = set()
        for link in data['links']:
            for side in ('a', 'b'):
                endpoint = link[side]
                key = (endpoint['device'], endpoint['port'])
                device = devices.get(key[0])
                if device is None or key[1] not in device['ports']:
                    errors.append('unknown_endpoint')
                if key in used:
                    errors.append('port_reused')
                used.add(key)
            if link['a']['device'] == link['b']['device']:
                errors.append('self_link_unsupported')
        for d in data['devices']:
            for group in d['combo_groups']:
                if sum((d['id'], port) in used for port in group) > 1:
                    errors.append('combo_conflict')
        nets = []
        for subnet in data['subnets']:
            try:
                net = ipaddress.ip_network(subnet['cidr'], strict=True)
            except ValueError:
                errors.append('invalid_subnet')
                continue
            for vrf, previous in nets:
                if vrf == subnet['vrf'] and net.version == previous.version and net.overlaps(previous):
                    errors.append('subnet_overlap')
            nets.append((subnet['vrf'], net))
        for d in data['devices']:
            if 'poe_failure_budget_w' in d and d['poe_load_w'] > d['poe_failure_budget_w']:
                errors.append('poe_failure_budget_exceeded')
            ports = d.get('poe_ports', [])
            if duplicates(x['port'] for x in ports):
                errors.append('duplicate_poe_port')
            for port in ports:
                if port['port'] not in d['ports']:
                    errors.append('unknown_poe_port')
                if port['load_w'] > port['limit_w']:
                    errors.append('poe_port_limit_exceeded')
                if port['required_standard'] not in port['supported_standards']:
                    errors.append('poe_standard_mismatch')
            if sum(Decimal(str(x['load_w'])) for x in ports) > Decimal(str(d['poe_load_w'])):
                errors.append('poe_port_load_exceeds_declared_total')
        if 'resilience' in data:
            model = data['resilience']
            link_ids = {link['id'] for link in data['links']}
            if len(devices) > 100 or len(data['links']) > 500:
                errors.append('resilience_model_too_large')
            for field in ('demands', 'scenarios'):
                if duplicates(item['id'] for item in model[field]):
                    errors.append('duplicate_resilience_id')
            for demand in model['demands']:
                if (demand['source'] not in devices or demand['destination'] not in devices
                        or demand['source'] == demand['destination']):
                    errors.append('invalid_demand_endpoint')
            for scenario in model['scenarios']:
                if scenario['id'] == 'baseline':
                    errors.append('reserved_scenario_id')
                if (not set(scenario['remove_devices']) <= set(devices)
                        or not set(scenario['remove_links']) <= link_ids):
                    errors.append('unknown_failure_target')
        for quote in data['quotes']:
            if Decimal(str(quote['unit_price'])) * quote['quantity'] != Decimal(str(quote['total'])):
                errors.append('quote_arithmetic_mismatch')
    elif kind == 'evidence':
        if duplicates(r['id'] for r in data['records']):
            errors.append('duplicate_evidence_id')
        for r in data['records']:
            if (r['scope'] == 'public') != (r['classification'] == 'public'):
                errors.append('classification_scope_mismatch')
            if datetime.fromisoformat(r['valid_until'].replace('Z', '+00:00')) < datetime.fromisoformat(
                    r['retrieved_at'].replace('Z', '+00:00')):
                errors.append('evidence_dates_reversed')
    elif kind == 'handoff':
        if duplicates(f['id'] for f in data['facts']):
            errors.append('duplicate_fact_id')
    return sorted(set(errors))



def business_diagnostics(data, errors):
    details = []
    def add(code, path, hint):
        if code in errors:
            details.append({'code': code, 'path': path, 'hint': hint})
    if data['kind'] == 'change':
        for code in errors:
            path = '/save_authorization' if code.startswith('save_authorization') else '/plan'
            details.append({'code': code, 'path': path, 'hint': 'Reconcile the record with actual evidence; do not invent approval or outcomes.'})
    elif data['kind'] == 'network':
        for i, device in enumerate(data['devices']):
            if device['poe_load_w'] > device['poe_budget_w']:
                add('poe_budget_exceeded', f'/devices/{i}/poe_load_w', 'Reduce actual load or verify sufficient supported capacity.')
            if 'poe_failure_budget_w' in device and device['poe_load_w'] > device['poe_failure_budget_w']:
                add('poe_failure_budget_exceeded', f'/devices/{i}/poe_failure_budget_w', 'Declared load exceeds failure-state budget.')
        used = {}
        for i, link in enumerate(data['links']):
            for side in ('a', 'b'):
                key = (link[side]['device'], link[side]['port'])
                path = f'/links/{i}/{side}'
                if key in used:
                    add('port_reused', path, 'Endpoint already used at ' + used[key])
                used[key] = path
        for i, quote in enumerate(data['quotes']):
            if Decimal(str(quote['unit_price'])) * quote['quantity'] != Decimal(str(quote['total'])):
                add('quote_arithmetic_mismatch', f'/quotes/{i}/total', 'Recalculate quantity times unit price without mixing currency/tax bases.')
        for code in errors:
            if not any(d['code'] == code for d in details):
                details.append({'code': code, 'path': '/', 'hint': 'Check the named engineering constraint; values omitted.'})
    return details


def review(data, as_of=None):
    as_of = as_of or date.today()
    details = []
    errors = validate(data, details)
    if errors and not any(code.startswith('schema:') or code == 'unknown_record_kind' for code in errors):
        details.extend(business_diagnostics(data, errors))
    warnings = []
    if not errors and data['kind'] == 'network':
        for i, quote in enumerate(data['quotes']):
            if date.fromisoformat(quote['valid_until']) < as_of:
                warnings.append({'code': 'quote_expired', 'path': f'/quotes/{i}/valid_until',
                                 'hint': 'Historical input only; obtain current quote for procurement.'})
    return {'valid': not errors, 'record_valid': not errors, 'errors': errors,
            'diagnostics': details, 'warnings': warnings, 'as_of': as_of.isoformat(),
            'engineering_status': 'invalid_record' if errors else ('needs_review' if warnings else 'limited_checks_passed'),
            'not_checked': ['source_authenticity', 'authorization_identity', 'device_behavior', 'business_acceptance'],
            'execution_authorized': False}


def search(data, root, scope, query, model=None, release=None, candidates=False):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('evidence_root_not_directory')
    results, rejected = [], []
    now = datetime.now(timezone.utc)
    for record in data['records']:
        if record['scope'] != scope:
            continue
        model_alias = model is not None and record['model'] != model
        if model_alias and (not candidates or model not in record.get('aliases', [])):
            continue
        if release is not None and record['release'] != release:
            continue
        text = ' '.join(record[k] for k in ('title', 'section', 'model', 'release')).casefold()
        if not all(term in text for term in query.casefold().split()):
            continue
        try:
            relative = Path(record['relative_path'])
            path = (root / relative).resolve(strict=True)
            if relative.is_absolute() or not path.is_relative_to(root) or not path.is_file():
                raise ValueError('path_outside_root_or_not_file')
            digest = hashlib.sha256()
            with path.open('rb') as source:
                for block in iter(lambda: source.read(1024 * 1024), b''):
                    digest.update(block)
            if digest.hexdigest() != record['sha256']:
                raise ValueError('hash_mismatch')
            if datetime.fromisoformat(record['retrieved_at'].replace('Z', '+00:00')) > now:
                raise ValueError('retrieval_date_in_future')
            if datetime.fromisoformat(record['valid_until'].replace('Z', '+00:00')) <= now:
                raise ValueError('expired')
            if record['verification'] == 'pending':
                raise ValueError('verification_pending')
        except (OSError, ValueError) as exc:
            reason = str(exc) if isinstance(exc, ValueError) else 'file_unavailable'
            rejected.append({'id': record['id'], 'reason': reason})
            continue
        results.append({**record, 'match_type': 'alias_candidate' if model_alias else 'exact_filter',
                        'applicability_confirmed': False})
    return {'status': 'matches' if results else 'no_match', 'matches': results,
            'rejected': rejected, 'boundary': 'metadata_filter_not_access_control'}


def render(data, output):
    devices = data['devices']
    device_numbers = {d['id']: i+1 for i, d in enumerate(devices)}
    height = max(120, len(data['links']) * 100 + 30)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 {height}" role="img" aria-label="Physical links">']
    rows = []
    for i, link in enumerate(data['links']):
        a, b = link['a'], link['b']
        y = 65 + i * 100
        svg.append(f'<path d="M300 {y} H800" fill="none" stroke="#64748b" stroke-width="2"/>')
        label = html.escape(link['id'][:40])
        svg.append(f'<text x="550" y="{y-10}" text-anchor="middle">{label} · {link["speed_gbps"]} Gbps</text>')
        for x, endpoint in ((180, a), (920, b)):
            svg.append(f'<rect x="{x-120}" y="{y-25}" width="240" height="50" rx="8" fill="#e2e8f0"/>')
            port = html.escape(endpoint['port'][:24])
            number = device_numbers[endpoint['device']]
            svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle">Device {number}: {port}</text>')
        cells = [link['id'], a['device'], a['port'], b['device'], b['port'], str(link['speed_gbps'])]
        rows.append('<tr>' + ''.join('<td>'+html.escape(c)+'</td>' for c in cells) + '</tr>')
    svg.append('</svg>')
    bom = ''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in
                  (i+1, d['id'], d['quantity'], d['poe_load_w'], d['poe_budget_w']))+'</tr>'
                  for i, d in enumerate(devices))
    page = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>H3c topology review</title>'
            '<style>body{font:16px system-ui;margin:32px;color:#172033}svg{width:100%;max-width:1100px}'
            'text{font:14px system-ui}table{border-collapse:collapse;margin:24px 0}td,th{border:1px solid #cbd5e1;padding:8px}'
            '</style><h1>Physical connection review</h1><p>Each row shows one physical link; devices may appear more than once. Numbers refer to the device table; full port names are listed below. Logical paths, failure capacity and device compatibility have not been verified.</p>'
            + ''.join(svg) + '<h2>Devices / BOM</h2><table><tr><th>Number</th><th>ID</th><th>Quantity</th><th>PoE load (W)</th><th>Budget (W)</th></tr>'
            + bom + '</table><h2>Port connections</h2><table><tr><th>Link</th><th>A</th><th>Port</th><th>B</th><th>Port</th><th>Gbps</th></tr>'
            + ''.join(rows) + '</table></html>')
    # Exclusive create prevents accidental overwrite of existing user artifacts.
    with Path(output).open('x', encoding='utf-8') as target:
        target.write(page)
    return {'output': str(Path(output).resolve()), 'devices': len(devices), 'links': len(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('check', 'digest', 'search', 'render'):
        p = sub.add_parser(name)
        p.add_argument('input')
        if name == 'search':
            p.add_argument('--root', required=True)
            p.add_argument('--scope', required=True)
            p.add_argument('--query', required=True)
            p.add_argument('--model'); p.add_argument('--release')
        if name == 'render':
            p.add_argument('--output', required=True)
    sub.choices['check'].add_argument('--as-of', type=date.fromisoformat)
    sub.choices['search'].add_argument('--candidates', action='store_true')
    args = parser.parse_args()
    try:
        data = load(args.input)
        result = review(data, getattr(args, 'as_of', None))
        errors = result['errors']
        expected = {'digest': 'change', 'search': 'evidence', 'render': 'network'}.get(args.command)
        if expected is not None and (not isinstance(data, dict) or data.get('kind') != expected):
            errors.append('command_kind_mismatch')
        result['valid'] = result['record_valid'] = not errors
        if errors:
            result['engineering_status'] = 'invalid_record'
        if not errors:
            if args.command == 'digest':
                result['plan_sha256'] = plan_digest(data)
            elif args.command == 'search':
                result.update(search(data, args.root, args.scope, args.query, args.model, args.release, args.candidates))
            elif args.command == 'render':
                result.update(render(data, args.output))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 2 if errors else 0
    except ImportError:
        print(json.dumps({'valid': False, 'error': 'requires_jsonschema_4', 'execution_authorized': False}))
        return 3
    except (OSError, ValueError, TypeError, RecursionError):
        print(json.dumps({'valid': False, 'error': 'invalid_input_or_io', 'execution_authorized': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())

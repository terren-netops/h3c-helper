#!/usr/bin/env python3
"""Extract a limited set of Comware CLI facts without interpreting unknown lines."""
import argparse
import hashlib
import json
import ipaddress
from pathlib import Path
import re
import sys

MAX_BYTES = 8 * 1024 * 1024
PROMPT = re.compile(r'^\s*(?:<([^<>\r\n]{1,80})>|\[([^\[\]\r\n]{1,80})\])\s*(.*)$')
INTERFACE = r'(?:GigabitEthernet|Ten-GigabitEthernet|FortyGigE|HundredGigE|GE|XGE|FGE|HGE|Bridge-Aggregation|Route-Aggregation|Vlan-interface)[0-9/.:]+'
SECRET = re.compile(r'(?i)(?:password|passwd|cipher|secret|community|private-key|authentication-key|pre-shared-key)\b')
COMMANDS = ('display version', 'display current-configuration', 'display interface',
            'display link-aggregation verbose', 'display irf', 'display startup', 'display clock')


def extract(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('input_too_large')
    text = raw.decode('utf-8-sig')
    lines = text.splitlines()
    devices, aliases, warnings = [], {}, []
    current, command, iface, aggregate = None, None, None, None
    recognized, sensitive, prompted = set(), [], False

    def device(alias):
        if alias not in aliases:
            aliases[alias] = len(devices)
            devices.append({'id': f'DEV-{len(devices)+1:03}', 'facts': [], 'gaps': []})
        return devices[aliases[alias]]

    def fact(field, value, line):
        current['facts'].append({'field': field, 'value': value, 'line_start': line,
                                 'line_end': line, 'command': command or 'unattributed',
                                 'status': 'observed_text_not_device_verified'})
        recognized.add(line)

    for number, original in enumerate(lines, 1):
        line = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', original).strip()
        if SECRET.search(line):
            sensitive.append(number)
            # Includes prompt commands containing secrets: never interpret or echo them.
            continue
        if re.search(r'(?i)(--\s*more\s*--|----\s*more\s*----|\[truncated\]|^\.\.\.$)', line):
            warnings.append({'code': 'pagination_or_truncation', 'line': number})
        match = PROMPT.match(line)
        if match:
            alias = match.group(1) or match.group(2)
            tail = match.group(3).strip()
            # Configuration subview names cannot reliably identify a different device.
            if match.group(2) and current is not None and not tail.startswith('display '):
                continue
            if match.group(2):
                roots = [key for key in aliases if alias.startswith(key + '-') and key != 'unattributed']
                if roots:
                    alias = max(roots, key=len)
            current = device(alias)
            prompted = True
            command = next((c for c in COMMANDS if tail == c or tail.startswith(c+' ')), None)
            iface = aggregate = None
            recognized.add(number)
            if command is None and tail:
                warnings.append({'code': 'unsupported_command', 'line': number})
            if alias.casefold() in ('h3c', 'sysname'):
                warnings.append({'code': 'generic_prompt_device_identity_unconfirmed', 'line': number})
            continue
        if current is None:
            current = device('unattributed')
        # Unprompted snippets are accepted only as fragments, never as complete inventory.
        match = re.search(r'\b(?:H3C Comware Software|Comware software),?\s+Version\s+([0-9.]+),\s*(Release|Feature|ESS)\s+([A-Za-z0-9.-]+)', line, re.I)
        if match:
            fact('software', {'version':match[1], 'train':match[2], 'release':match[3]}, number)
            continue
        match = re.fullmatch(r'H3C\s+((?:SecPath )?[A-Za-z0-9._+-]+)\s+uptime is\s+([0-9A-Za-z, ]+)', line)
        if match:
            fact('model', match[1], number);fact('uptime_text',match[2],number);continue
        match = re.fullmatch(r'(?:Boot|System) image:\s*([A-Za-z0-9:/_.-]+)', line)
        if match:
            fact('image',match[1],number);continue
        match = re.fullmatch(r'Patch version:\s*([A-Za-z0-9._-]+)',line,re.I)
        if match:fact('patch',match[1],number);continue
        match = re.fullmatch(r'(?:Slot|slot)\s+(\d+)\s*:\s*([A-Za-z][A-Za-z0-9._-]+)',line)
        if match:fact('slot_model',{'slot':int(match[1]),'model':match[2]},number);continue
        match = re.fullmatch(r'(\d{2}:\d{2}:\d{2}\s+(?:UTC|GMT)(?:[+-]\d{1,2}:?\d{0,2})?\s+[A-Za-z0-9 /:-]+)',line)
        if match and command=='display clock':fact('clock_text',match[1],number);continue
        if command == 'display interface' and re.fullmatch(INTERFACE,line):
            iface=line;fact('interface',iface,number);continue
        if line.startswith('interface '):
            match = re.fullmatch(r'interface\s+('+INTERFACE+r')',line)
            iface=match[1] if match else None
            if iface:fact('interface',iface,number)
            continue
        if line == '#':
            iface=None
        match = re.fullmatch(r'('+INTERFACE+r')\s+current state:\s*(UP|DOWN|Administratively DOWN)',line,re.I)
        if match:
            iface=match[1];fact('interface_state',{'port':iface,'state':match[2].upper()},number);continue
        if iface:
            match = re.fullmatch(r'Current state:\s*(UP|DOWN|Administratively DOWN)',line,re.I)
            if match:fact('interface_state',{'port':iface,'state':match[1].upper()},number);continue
            address = re.fullmatch(r'ip address\s+(\S+)\s+(\S+)',line)
            if address:
                try:
                    parsed=ipaddress.IPv4Interface(address[1]+'/'+address[2])
                    fact('interface_address',{'port':iface,'address':str(parsed)},number)
                except ValueError:warnings.append({'code':'invalid_interface_address','line':number})
                continue
            match = re.fullmatch(r'Line protocol (?:current )?state:\s*(UP|DOWN)',line,re.I)
            if match:fact('line_protocol',{'port':iface,'state':match[1].upper()},number);continue
            match = re.fullmatch(r'port link-type\s+(access|trunk|hybrid)',line)
            if match:fact('link_type',{'port':iface,'mode':match[1]},number);continue
            match = re.fullmatch(r'port (?:access vlan|trunk pvid vlan|hybrid pvid vlan)\s+(\d+)',line)
            if match:
                vlan=int(match[1])
                if 1<=vlan<=4094:fact('pvid',{'port':iface,'vlan':vlan},number)
                else:warnings.append({'code':'invalid_vlan_value','line':number})
                continue
            match = re.fullmatch(r'port trunk permit vlan\s+(all|[0-9 to]+)',line)
            if match:fact('trunk_vlan_expression',{'port':iface,'expression':match[1]},number);continue
            match = re.search(r'\b(\d+)\s+CRC\b',line)
            if match:fact('crc_counter',{'port':iface,'value':int(match[1])},number);continue
        if command == 'display irf':
            match=re.match(r'^[*+\s]*(\d+)\s+(Master|Standby|Subordinate)\b',line,re.I)
            if match:fact('irf_member',{'member':int(match[1]),'role':match[2].lower()},number);continue
        if command == 'display link-aggregation verbose':
            match=re.fullmatch(r'Aggregate Interface:\s*(Bridge-Aggregation\d+|Route-Aggregation\d+)',line)
            if match:aggregate=match[1];fact('aggregate',aggregate,number);continue
            match=re.match(r'^('+INTERFACE+r')\s+([SUI])\s+',line)
            if match and aggregate:
                fact('aggregation_member',{'aggregate':aggregate,'port':match[1],
                     'state':{'S':'selected','U':'unselected','I':'individual'}[match[2]]},number)
    for d in devices:
        for field in ('model','software'):
            values={json.dumps(f['value'],sort_keys=True) for f in d['facts'] if f['field']==field}
            if not values:d['gaps'].append('missing_'+field)
            if len(values)>1:d['gaps'].append('conflicting_'+field+'_do_not_merge')
    return {'schema_version':'1','kind':'device_profile','source_sha256':hashlib.sha256(raw).hexdigest(),
            'line_count':len(lines),'devices':devices,'warnings':warnings,
            'sensitive_lines_omitted':sensitive,'unparsed_line_count':len(lines)-len(recognized)-len(sensitive),
            'coverage':'limited_comware_text_patterns','fragment_only':not prompted,
            'unknowns':['hardware_inventory','patch_inventory','management_path','capture_time_and_timezone','output_completeness'],
            'execution_authorized':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input');args=parser.parse_args()
    try:
        path=Path(args.input)
        if path.stat().st_size>MAX_BYTES:raise ValueError('input_too_large')
        print(json.dumps(extract(path.read_bytes()),ensure_ascii=False))
        return 0
    except (OSError,ValueError,UnicodeError):
        print(json.dumps({'error':'invalid_input_or_encoding','execution_authorized':False}));return 2


if __name__=='__main__':sys.exit(main())

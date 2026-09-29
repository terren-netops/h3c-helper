#!/usr/bin/env python3
"""Offline host capability inventory; never connects, installs or authorizes writes."""
import importlib.metadata
import json
import platform
import shutil
import sys


def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def inspect_host():
    schema_version = package_version('jsonschema')
    schema_compatible = bool(schema_version and schema_version.split('.')[0] == '4')
    python_compatible = sys.version_info >= (3, 10)
    return {
        'report_version': '1',
        'host': {'os': platform.system(), 'release': platform.release(),
                 'architecture': platform.machine()},
        'python': {'version': platform.python_version(), 'executable': sys.executable,
                   'supported': python_compatible},
        'packages': {'jsonschema': schema_version, 'netmiko': package_version('netmiko')},
        'commands_found': {name: shutil.which(name) is not None
                           for name in ('ssh', 'claude', 'codex')},
        'offline_tools': 'dependencies_present_not_exercised'
                         if python_compatible and schema_compatible else 'missing_or_unsupported_dependency',
        'bundled_device_executor': False,
        'external_runner': 'not_assessed',
        'execution_authorized': False,
        'not_checked': ['package_importability', 'host_authentication', 'device_reachability',
                        'trusted_host_identity', 'model_release_compatibility',
                        'runner_safety_and_recovery', 'business_acceptance'],
    }


def main():
    # Metadata and PATH discovery only: do not read credentials or invoke discovered programs.
    try:
        print(json.dumps(inspect_host(), ensure_ascii=False))
        return 0
    except (OSError, ValueError):
        print(json.dumps({'error': 'host_inventory_unavailable', 'execution_authorized': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Build one installable package per platform from the shared H3c Helper source.

Business content exists once: skills/, references/, scripts/, schemas/, assets/, docs/ and LICENSE.
platforms/<name>/platform.json declares only packaging differences. verify() re-reads every
package from disk; any difference beyond the declared conversions fails the build.
Nothing is installed or published.
"""
import argparse
import json
import os
from pathlib import Path
import re
import zipfile

LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
SCHEME = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:')
SHARED = ('references', 'assets', 'scripts', 'schemas', 'docs')
WORKFLOWS = {
    'h3c-configure': 'Configuration generation or review',
    'h3c-troubleshoot': 'Fault investigation and measured performance',
    'h3c-design-network': 'Network topology and availability',
    'h3c-select-products': 'Product, optics and compatibility comparisons',
    'h3c-service-support': 'TAC case preparation, service navigation and training',
}


def read_version(source):
    return (source / 'VERSION').read_text(encoding='utf-8').strip()


def load_platform(source, name):
    folder = Path(source).resolve() / 'platforms' / name
    platform = json.loads((folder / 'platform.json').read_text(encoding='utf-8'))
    platform.update(name=name, folder=folder)
    return platform


def platform_names(source):
    return sorted(path.parent.name for path in (Path(source) / 'platforms').glob('*/platform.json'))


def _files(root):
    if root.is_symlink():
        raise ValueError(f'Symlink is not portable: {root}')
    files = []
    for path in sorted(root.rglob('*')):
        if '__pycache__' in path.parts or path.name == '.DS_Store':
            continue
        if path.is_symlink():
            raise ValueError(f'Symlink is not portable: {path}')
        if path.is_file():
            files.append(path)
    return files


def _mapping(source, layout):
    """Map each bundled source file to its path inside the package."""
    mapping = {source / 'LICENSE': Path('LICENSE')}
    for folder in SHARED:
        mapping.update((path, path.relative_to(source)) for path in _files(source / folder))
    for name in WORKFLOWS:
        folder = source / 'skills' / name
        if layout == 'aggregate':
            path = folder / 'SKILL.md'
            if any(p.is_symlink() for p in (path, folder, folder.parent)):
                raise ValueError(f'Symlink is not portable: {path}')
            mapping[path] = Path('references/workflows') / (name + '.md')
        else:
            if folder.parent.is_symlink():
                raise ValueError(f'Symlink is not portable: {folder.parent}')
            mapping.update((path, path.relative_to(source)) for path in _files(folder))
    return mapping


def _root_body(version):
    body = '\n# H3c Helper\n\nWrite in English by default; follow an explicit request for another language.\n\n'
    body += ('Read the relevant bundled workflow and its task-specific references before doing the work. '
             'Read these documents directly; no other installed skills are required. For mixed tasks, use only the workflows needed.\n\n')
    body += ''.join(f'- {label}: [{name}](references/workflows/{name}.md).\n' for name, label in WORKFLOWS.items())
    body += ('\nFor device-push or batch write/save scripts, read the configure workflow and '
             '[batch commissioning](references/batch-commissioning.md) before writing code; user urgency does not relax their gates.\n')
    body += ('\nResolve script examples from this skill root. Check [local tools](references/local-tools.md) '
             'before invoking optional Python helpers. If the host lacks file, research or execution capabilities, '
             'state the gap; never claim an unperformed check. This skill supplies no SSH executor, MCP service or sender. '
             'Follow [source policy](references/source-policy.md) and [operation boundaries](references/operation-policy.md).\n\n'
             f'Source candidate: {version}. Target-client loading and behavior require separate validation. '
             'Known design reasoning and evidence-wording issues remain under review; offline checks do not establish '
             'production readiness or device execution. See [acceptance protocol](docs/acceptance.md).\n')
    return body


def _root_skill(platform, version):
    lines = [line.replace('{version}', json.dumps(version)) for line in platform['frontmatter']]
    return ('---\n' + ''.join(line + '\n' for line in lines) + '---\n' + _root_body(version)).encode('utf-8')


def _platform_files(platform, version):
    return {target: (platform['folder'] / template).read_text(encoding='utf-8').replace('{{VERSION}}', version).encode('utf-8')
            for target, template in platform.get('platform_files', {}).items()}


def _payload(source, platform, version):
    layout = platform['layout']
    mapping = _mapping(source, layout)
    payload, link_count = {}, 0
    for old, new in mapping.items():
        data = old.read_bytes()
        if old.suffix == '.md':
            def relocate(match):
                nonlocal link_count
                target_path = match.group(1)
                if SCHEME.match(target_path) or target_path.startswith('#'):
                    return match.group(0)
                path, separator, anchor = target_path.partition('#')
                resolved = (old.parent / path).resolve()
                if resolved not in mapping:
                    raise ValueError(f'Unbundled local reference: {old}: {target_path}')
                link_count += 1
                relative = Path(os.path.relpath(mapping[resolved], new.parent)).as_posix()
                return match.group(0).replace('(' + target_path + ')', '(' + relative + separator + anchor + ')')
            text = LINK.sub(relocate, data.decode('utf-8'))
            # Plugin layouts keep source paths, so their Markdown is only checked, never rewritten.
            if layout == 'aggregate':
                data = text.encode('utf-8')
        payload[new.as_posix()] = data
    if layout == 'aggregate':
        payload['SKILL.md'] = _root_skill(platform, version)
    payload.update(_platform_files(platform, version))
    return payload, link_count


def _check_outputs(source, outputs):
    for output in outputs:
        if output.exists() or output.is_symlink():
            raise ValueError(f'Output already exists: {output}')
        resolved = output.resolve()
        if resolved.is_relative_to(source) and not resolved.is_relative_to(source / 'dist'):
            raise ValueError('Output inside the source must be under dist/')


def build(source, platform, destination):
    source, destination = Path(source).resolve(), Path(destination).absolute()
    _check_outputs(source, [destination])
    version = read_version(source)
    # Validate everything before creating outputs; exclusive creation prevents overwrites.
    payload, link_count = _payload(source, platform, version)
    destination.mkdir(parents=True, exist_ok=False)
    for relative, data in sorted(payload.items()):
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as handle:
            handle.write(data)
    return {'platform': platform['name'], 'version': version, 'files': len(payload), 'relocated_links': link_count}


def write_archive(source, platform, destination, archive):
    source, destination, archive = Path(source).resolve(), Path(destination).resolve(), Path(archive).absolute()
    _check_outputs(source, [archive])
    if archive.resolve().is_relative_to(destination):
        raise ValueError('ZIP must be outside the package directory')
    prefix = platform['archive']['prefix']
    files = sorted(path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file())
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as handle:
        for relative in files:
            info = zipfile.ZipInfo(prefix + relative, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            handle.writestr(info, (destination / relative).read_bytes())


def _canonical_links(text, base, resolve):
    """Replace every local link target with the bundle path it designates."""
    def replace(match):
        target_path = match.group(1)
        if SCHEME.match(target_path) or target_path.startswith('#'):
            return match.group(0)
        path, separator, anchor = target_path.partition('#')
        return match.group(0).replace('(' + target_path + ')', f'(<{resolve(base, path)}>{separator}{anchor})')
    return LINK.sub(replace, text)


def verify(source, platform, destination, archive=None):
    """Re-read a package and report any difference from the source beyond declared conversions.

    Allowed: relocated relative link paths in aggregate Markdown, the generated root SKILL.md,
    declared platform files and the archive prefix. Everything else must match byte for byte.
    """
    source, destination = Path(source).resolve(), Path(destination).resolve()
    version = read_version(source)
    mapping = _mapping(source, platform['layout'])
    expected = {new.as_posix(): old for old, new in mapping.items()}
    bundle = {old.resolve(): new.as_posix() for old, new in mapping.items()}
    generated = _platform_files(platform, version)
    if platform['layout'] == 'aggregate':
        generated['SKILL.md'] = _root_skill(platform, version)
    actual = {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()}
    wanted = set(expected) | set(generated)
    problems = [f'missing: {name}' for name in sorted(wanted - actual)]
    problems += [f'unexpected: {name}' for name in sorted(actual - wanted)]
    if any(name.startswith('tools/') or Path(name).name in ('build.py', 'export_skill.py') for name in actual):
        problems.append('build tooling packaged')

    def exported_target(base, path):
        linked = (base / path).resolve()
        if not linked.is_relative_to(destination) or not linked.is_file():
            problems.append(f'broken link: {base.relative_to(destination).as_posix()}/{path}')
            return 'BROKEN'
        return linked.relative_to(destination).as_posix()

    transformed = []
    for name in sorted(set(expected) & actual):
        old, new = expected[name], destination / name
        same = old.read_bytes() == new.read_bytes()
        if old.suffix != '.md':
            if not same:
                problems.append(f'bytes differ: {name}')
            continue
        # Canonicalise even identical Markdown: exported_target records broken links as problems.
        exported = _canonical_links(new.read_text(encoding='utf-8'), new.parent, exported_target)
        if same:
            continue
        original = _canonical_links(old.read_text(encoding='utf-8'), old.parent,
                                    lambda base, path: bundle.get((base / path).resolve(), 'UNBUNDLED'))
        if original == exported:
            transformed.append(name)
        else:
            problems.append(f'content differs beyond link paths: {name}')
    for name, data in sorted(generated.items()):
        if name not in actual:
            continue
        path = destination / name
        if path.read_bytes() != data:
            problems.append(f'generated file differs from declaration: {name}')
        if name.endswith('.md'):
            _canonical_links(path.read_text(encoding='utf-8'), path.parent, exported_target)
        if name.endswith('.json') and json.loads(data).get('version', version) != version:
            problems.append(f'{name} version differs from VERSION')
    if platform['layout'] == 'aggregate':
        header = generated['SKILL.md'].decode('utf-8').split('---\n')[1]
        fields = {line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                  for line in header.splitlines() if line and not line.startswith(' ')}
        if fields.get('name') != 'h3c-helper':
            problems.append('frontmatter name must be h3c-helper')
        limit = platform.get('description_limit')
        if limit and len(json.loads(fields['description'])) > limit:
            problems.append(f'description exceeds {limit} characters')
    if archive:
        prefix = platform['archive']['prefix']
        with zipfile.ZipFile(archive) as handle:
            if handle.testzip() is not None:
                problems.append('ZIP CRC error')
            if sorted(handle.namelist()) != sorted(prefix + name for name in actual):
                problems.append('ZIP entries differ from package directory')
            else:
                problems += [f'ZIP bytes differ: {name}' for name in sorted(actual)
                             if handle.read(prefix + name) != (destination / name).read_bytes()]
    return {'ok': not problems, 'platform': platform['name'], 'files': len(actual),
            'transformed': transformed, 'generated': sorted(generated), 'problems': problems}


def _cross_platform(dist, entries):
    """Shared files must be identical between packages of the same layout; root bodies across aggregates."""
    problems, seen = [], {}
    for entry in entries:
        package = dist / entry['platform'] / 'h3c-helper'
        own = set(entry['declaration'].get('platform_files', {}))
        for path in sorted(package.rglob('*')):
            relative = path.relative_to(package).as_posix()
            if not path.is_file() or relative in own:
                continue
            data = path.read_bytes()
            if relative == 'SKILL.md':
                data = data.split(b'---\n', 2)[2]
            key = (entry['declaration']['layout'], relative)
            first = seen.setdefault(key, (entry['platform'], data))
            if first[1] != data:
                problems.append(f'{relative} differs between {first[0]} and {entry["platform"]}')
    return problems


def _difference_list(version, entries, cross):
    lines = [f'# Allowed differences: H3c Helper {version}', '',
             'Generated by tools/build.py from platforms/*/platform.json and verification of the built packages. Do not edit.', '',
             '| Platform | Layout | Archive | Files | Link-relocated Markdown | Generated files | Verification |',
             '|---|---|---|---|---|---|---|']
    for entry in entries:
        result = entry['verification']
        status = 'PASS' if result['ok'] else 'FAIL: ' + '; '.join(result['problems'])
        lines.append(f"| {entry['platform']} | {entry['declaration']['layout']} | {entry.get('archive', 'not written')} | "
                     f"{result['files']} | {len(result['transformed'])} | {', '.join(result['generated'])} | {status} |")
    lines += ['', 'Shared scripts, schemas, assets and LICENSE are byte-identical to the source in every package. '
              'Markdown differs only by relocated link paths; plugin layouts keep source paths unchanged.', '',
              '## Root SKILL.md frontmatter', '',
              'Description wording may change triggering only; review that it keeps the five-workflow business scope.', '']
    for entry in entries:
        declaration = entry['declaration']
        if declaration['layout'] != 'aggregate':
            continue
        lines += [f"### {entry['platform']}", '', '```yaml', *declaration['frontmatter'], '```', '']
    lines += ['## Platform notes', '']
    for entry in entries:
        lines += [f"- {entry['platform']}: {note}" for note in entry['declaration'].get('notes', [])]
    lines += ['', '## Cross-platform check', '', '; '.join(cross) if cross else 'PASS', '']
    return '\n'.join(lines)


def build_all(source, dist):
    source, dist = Path(source).resolve(), Path(dist).absolute()
    _check_outputs(source, [dist])
    version = read_version(source)
    entries = []
    for name in platform_names(source):
        platform = load_platform(source, name)
        package = dist / name / 'h3c-helper'
        entry = build(source, platform, package)
        entry['declaration'] = {key: value for key, value in platform.items() if key not in ('name', 'folder')}
        entry['verification'] = verify(source, platform, package)
        # An archive is written only for a package that already passed verification.
        if entry['verification']['ok']:
            archive = dist / f"h3c-helper-{name}-{version}{platform['archive']['extension']}"
            write_archive(source, platform, package, archive)
            entry['archive'] = archive.name
            entry['verification'] = verify(source, platform, package, archive)
        entries.append(entry)
    cross = _cross_platform(dist, entries)
    report = {'ok': all(entry['verification']['ok'] for entry in entries) and not cross,
              'version': version, 'cross_platform_problems': cross, 'platforms': entries}
    (dist / 'verification.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    (dist / 'ALLOWED-DIFFERENCES.md').write_text(_difference_list(version, entries, cross), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='build every platform into --dist (default: dist/)')
    parser.add_argument('--dist', type=Path)
    parser.add_argument('--platform')
    parser.add_argument('--dest', type=Path)
    parser.add_argument('--zip', dest='archive', type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    if not args.all and not (args.platform and args.dest):
        parser.error('use --all, or --platform NAME --dest DIR [--zip FILE]')
    try:
        if args.all:
            report = build_all(source, args.dist or source / 'dist')
            ok = report['ok']
            print(json.dumps({'ok': ok, 'version': report['version'],
                              'platforms': {entry['platform']: entry['verification']['ok'] for entry in report['platforms']},
                              'cross_platform_problems': report['cross_platform_problems']}))
        else:
            platform = load_platform(source, args.platform)
            result = build(source, platform, args.dest)
            result['verification'] = verify(source, platform, args.dest)
            if result['verification']['ok'] and args.archive:
                write_archive(source, platform, args.dest, args.archive)
                result['verification'] = verify(source, platform, args.dest, args.archive)
            ok = result['verification']['ok']
            print(json.dumps(result))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Build failed: {error}\n')
    if not ok:
        parser.exit(1, 'Verification failed\n')


if __name__ == '__main__':
    main()

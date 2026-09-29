# Per-platform packages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one verified installable package per platform (claude, workbuddy, chatgpt, generic, codex, claude-code) from the single shared H3c Helper source.

**Architecture:** Shared business content stays where it is. `platforms/<name>/platform.json` declares packaging differences only. `tools/build.py` (moved from `scripts/export_skill.py`) builds `dist/<name>/h3c-helper/`, re-reads it with `verify()`, writes the archive only after verification and generates `dist/ALLOWED-DIFFERENCES.md`.

**Tech Stack:** Python 3.10+ standard library, unittest. No new dependency.

Spec: `design/2026-09-29-platform-packages-design.md`. Ticket: TF-30. Source: the repository root (`$SOURCE`) (no git repository: "checkpoint" steps record hashes in the ticket evidence folder instead of committing). Evidence folder: `E=<evidence folder outside the source>`.

## File structure

| Path | Responsibility |
|---|---|
| `VERSION` | Single version string |
| `platforms/<name>/platform.json` | Layout, archive prefix/extension, root frontmatter lines, description limit, platform files, notes |
| `platforms/<name>/INSTALL.md` | Installation route for that platform (never packaged) |
| `platforms/chatgpt/agents/openai.yaml` | ChatGPT skill display metadata (packaged by declaration) |
| `platforms/codex/*.template`, `platforms/claude-code/*.template` | Plugin manifests with `{{VERSION}}` |
| `tools/build.py` | build, write_archive, verify, build_all, CLI |
| `tests/test_build.py` | Replaces `tests/test_export_skill.py` |

---

### Task 1: Ticket, baseline snapshot and reference hashes

- [ ] **Step 1: Mark TF-30 in development** in `~/.claude/tickets/h3c-helper/TICKETS.md` (status `🚧 In development`).
- [ ] **Step 2: Snapshot and hash the current source**

```bash
E=${E:?set an evidence folder outside the source}
mkdir -p $E && cd $SOURCE
rsync -a --exclude __pycache__ --exclude .DS_Store ./ $E/before/
find . -type f -not -path '*/__pycache__/*' -not -name .DS_Store | sort | xargs shasum -a 256 > $E/before-sha256.txt
```

- [ ] **Step 3: Record the three reference ZIP hashes with the current exporter**

```bash
python3 scripts/export_skill.py $E/ref/generic/h3c-helper --zip $E/ref/generic.zip
python3 scripts/export_skill.py $E/ref/workbuddy/h3c-helper --target workbuddy --zip $E/ref/workbuddy.zip
python3 scripts/export_skill.py $E/ref/claude/h3c-helper --target claude --zip $E/ref/claude.zip
shasum -a 256 $E/ref/*.zip | tee $E/ref/zip-sha256.txt
```

Expected: three exit-0 lines with `"verification": {"ok": true`.

### Task 2: Move the exporter to tools/build.py without behavior change

**Files:** Move `scripts/export_skill.py` → `tools/build.py`; Modify `tests/test_export_skill.py:9`.

- [ ] **Step 1: Move and repoint the test**

```bash
mkdir -p tools && mv scripts/export_skill.py tools/build.py
sed -i '' "s#SOURCE / 'scripts/export_skill.py'#SOURCE / 'tools/build.py'#" tests/test_export_skill.py
```

- [ ] **Step 2: Run tests** — `python3 -m unittest discover -s tests` → `Ran 43 tests … OK`.
- [ ] **Step 3: Hash invariance**

```bash
python3 tools/build.py $E/t2/generic/h3c-helper --zip $E/t2/generic.zip
python3 tools/build.py $E/t2/workbuddy/h3c-helper --target workbuddy --zip $E/t2/workbuddy.zip
python3 tools/build.py $E/t2/claude/h3c-helper --target claude --zip $E/t2/claude.zip
shasum -a 256 $E/t2/*.zip | awk '{print $1}' > $E/t2/h.txt; awk '{print $1}' $E/ref/zip-sha256.txt | diff - $E/t2/h.txt && echo IDENTICAL
```

Expected: `IDENTICAL`. `Path(__file__).resolve().parents[1]` is still the source root.

### Task 3: Data-driven platforms for generic, workbuddy, claude

**Files:** Create `VERSION`, `platforms/{generic,workbuddy,claude}/platform.json` and `INSTALL.md`; Rewrite `tools/build.py`; Replace `tests/test_export_skill.py` with `tests/test_build.py`.

- [ ] **Step 1: VERSION** — content `0.9.1-rc.14` plus newline.
- [ ] **Step 2: platform declarations**

`platforms/generic/platform.json`:
```json
{
  "layout": "aggregate",
  "archive": {"prefix": "", "extension": ".zip"},
  "frontmatter": [
    "name: h3c-helper",
    "description: \"Review H3C configurations, troubleshoot faults, design networks, compare products and prepare service-support drafts. Use for H3C engineering tasks and supplied device outputs; execution needs an authorized external runner.\"",
    "metadata:",
    "  version: {version}"
  ],
  "notes": ["Copy the complete h3c-helper folder into the host skills directory (CodeBuddy .codebuddy/skills, Qoder .qoder/skills, QoderWork ~/.qoderwork/skills)."]
}
```

`platforms/workbuddy/platform.json`:
```json
{
  "layout": "aggregate",
  "archive": {"prefix": "", "extension": ".zip"},
  "frontmatter": [
    "name: h3c-helper",
    "description: \"Review H3C configurations, troubleshoot faults, design networks, compare products and prepare service-support drafts. Use for H3C engineering tasks and supplied device outputs; execution needs an authorized external runner.\"",
    "description_zh: \"用于 H3C 配置审查、故障排查、网络设计、产品选型和服务支持。\"",
    "description_en: \"Review H3C configurations, troubleshoot faults, design networks, compare products and prepare service-support drafts. Use for H3C engineering tasks and supplied device outputs; execution needs an authorized external runner.\"",
    "version: {version}",
    "author: \"Terren\""
  ],
  "notes": ["WorkBuddy: Skills -> Add skill -> Upload skill, select the ZIP."]
}
```

`platforms/claude/platform.json`:
```json
{
  "layout": "aggregate",
  "archive": {"prefix": "h3c-helper/", "extension": ".zip"},
  "description_limit": 200,
  "frontmatter": [
    "name: h3c-helper",
    "description: \"Use for any H3C/Comware networking question: explain concepts (VLAN, IRF), review configs, troubleshoot, design networks, compare products/optics, draft TAC cases. Never connects to devices.\"",
    "dependencies: python>=3.10, jsonschema>=4",
    "metadata:",
    "  version: {version}"
  ],
  "notes": [
    "Official format: ZIP root is the skill folder; description <= 200 characters (support.claude.com/en/articles/12512198).",
    "Install: claude.ai or Claude Desktop Customize > Skills > Add > Upload skill; update or roll back with the skill menu Replace.",
    "2026-09-29: the dependencies declaration did not provision jsonschema in the claude.ai sandbox; structured checks exit 3 there."
  ]
}
```

Each `INSTALL.md` repeats the `notes` as numbered steps plus the verification to run after installation (claude: runtime sha256 of all files in a fresh chat).

- [ ] **Step 3: Write the failing tests** — create `tests/test_build.py` with the code in Appendix B, but only the tests `test_aggregate_complete_and_contained`, `test_workbuddy_metadata_and_reproducible_zip`, `test_claude_layout_metadata_and_verification`, `test_verify_rejects_content_drift`, `test_no_overwrite_or_source_pollution`, `test_broken_reference_and_symlink_rejected_before_writes`. Delete `tests/test_export_skill.py`.
- [ ] **Step 4: Run** `python3 -m unittest discover -s tests` → errors (`module 'build' has no attribute 'load_platform'`).
- [ ] **Step 5: Replace `tools/build.py` with Appendix A.**
- [ ] **Step 6: Run tests** → `Ran 43 tests … OK` (37 other + 6 build).
- [ ] **Step 7: Hash invariance with the new CLI**

```bash
for p in generic workbuddy claude; do python3 tools/build.py --platform $p --dest $E/t3/$p/h3c-helper --zip $E/t3/$p.zip; done
shasum -a 256 $E/t3/generic.zip $E/t3/workbuddy.zip $E/t3/claude.zip | awk '{print $1}' > $E/t3/h.txt; awk '{print $1}' $E/ref/zip-sha256.txt | diff - $E/t3/h.txt && echo IDENTICAL
```

Expected: `IDENTICAL` (order in `zip-sha256.txt` is claude, generic, workbuddy alphabetically; compare sorted lists if order differs: `sort`).

### Task 4: chatgpt, codex and claude-code packages; build --all

**Files:** Create `platforms/chatgpt/{platform.json,INSTALL.md,agents/openai.yaml}`, `platforms/codex/{platform.json,INSTALL.md,plugin.json.template,codex-plugin.json.template,marketplace.json.template}`, `platforms/claude-code/{platform.json,INSTALL.md,claude-plugin.json.template}`; Modify `tests/test_build.py`.

- [ ] **Step 1: Declarations**

`platforms/chatgpt/platform.json`: same `frontmatter` as generic, `"archive": {"prefix": "", "extension": ".skill"}`, `"platform_files": {"agents/openai.yaml": "agents/openai.yaml"}`, notes: "chatgpt.com/skills upload of the .skill archive (TF-18 route, rc.5); not retested for this layout."

`platforms/chatgpt/agents/openai.yaml`:
```yaml
interface:
  display_name: "H3c Helper"
  short_description: "H3C configuration, troubleshooting, design and support"
  default_prompt: "Use $h3c-helper to review my H3C engineering task with sources and verification steps."
```

`platforms/codex/platform.json`:
```json
{
  "layout": "plugin",
  "archive": {"prefix": "h3c-helper/", "extension": ".zip"},
  "platform_files": {
    "plugin.json": "plugin.json.template",
    ".codex-plugin/plugin.json": "codex-plugin.json.template",
    ".agents/plugins/marketplace.json": "marketplace.json.template"
  },
  "notes": ["codex plugin marketplace add <package>; codex plugin add h3c-helper@h3c-helper-local. The codex CLI is absent on the build Mac; installation is unverified there."]
}
```

`platforms/claude-code/platform.json`:
```json
{
  "layout": "plugin",
  "archive": {"prefix": "h3c-helper/", "extension": ".zip"},
  "platform_files": {".claude-plugin/plugin.json": "claude-plugin.json.template"},
  "notes": ["claude plugin validate <package> --strict; claude --plugin-dir <package> for session loading."]
}
```

Templates: copy the current root files and replace the version value only:
```bash
sed 's/"version": "0.9.1-rc.14"/"version": "{{VERSION}}"/' plugin.json > platforms/codex/plugin.json.template
sed 's/"version": "0.9.1-rc.14"/"version": "{{VERSION}}"/' .codex-plugin/plugin.json > platforms/codex/codex-plugin.json.template
cp .agents/plugins/marketplace.json platforms/codex/marketplace.json.template
sed 's/"version": "0.9.1-rc.14"/"version": "{{VERSION}}"/' .claude-plugin/plugin.json > platforms/claude-code/claude-plugin.json.template
grep -c '{{VERSION}}' platforms/codex/*.template platforms/claude-code/*.template
```
Expected counts: plugin.json 1, codex-plugin 1, marketplace 0, claude-plugin 1.

- [ ] **Step 2: Add the remaining tests** from Appendix B: `test_root_body_identical_across_aggregate_platforms`, `test_plugin_layouts_keep_skills_byte_identical`, `test_build_all_writes_report_and_difference_list`.
- [ ] **Step 3: Run tests** → `Ran 46 tests … OK` (Appendix A already supports both layouts; if a test fails, fix the declaration, not the check).
- [ ] **Step 4: Build all and validate**

```bash
python3 tools/build.py --all --dist $E/dist; echo exit=$?
for f in plugin.json .codex-plugin/plugin.json .agents/plugins/marketplace.json; do cmp $f $E/dist/codex/h3c-helper/$f && echo "same $f"; done
cmp .claude-plugin/plugin.json $E/dist/claude-code/h3c-helper/.claude-plugin/plugin.json && echo same-claude-manifest
claude plugin validate $E/dist/claude-code/h3c-helper --strict; echo validate=$?
```
Expected: `exit=0`, four `same` lines, `validate=0`. Record the Codex package as statically verified only.

### Task 5 (requires separate user confirmation): retire root manifests and update documents

- [ ] **Step 1: Ask the user** to confirm removal of root `plugin.json`, `.codex-plugin/`, `.claude-plugin/`, `.agents/` and that Codex/Claude Code installs move to `dist/`. Stop if not confirmed.
- [ ] **Step 2: Remove** those paths (kept in `$E/before/`), then run `python3 -m unittest discover -s tests` → OK and `python3 tools/build.py --all --dist $E/dist5` → exit 0.
- [ ] **Step 3: Documents** — README: version line, repository layout bullets (line 55), host matrix row "Claude chat uploads", Version history rc.14 entry (add build tooling); `docs/install.md`: Codex and Claude Code commands point to `dist/codex/h3c-helper` and `dist/claude-code/h3c-helper` after `python3 tools/build.py --all`; `docs/agent-compatibility.md` lines 12–13: replace exporter commands with `python3 tools/build.py --all` and `--platform` examples. Re-run build --all → exit 0.

### Task 6: Real acceptance and closure

- [ ] **Step 1: Claude** — Replace-upload `dist/h3c-helper-claude-<version>.zip`; in fresh chats run case K (all-file sha256, compare with the ZIP), case D (natural trigger) and case H (script run). Record URLs, model, tool evidence.
- [ ] **Step 2: Claude Code** — `claude plugin validate dist/claude-code/h3c-helper --strict`; session load with `--plugin-dir` only if it does not modify the user's installation.
- [ ] **Step 3: code-simplifier** on `tools/build.py` and `tests/test_build.py`; re-run tests and build --all hash comparison.
- [ ] **Step 4: Report and tickets** — report `outputs/20260929_H3c_Helper_平台包_REVIEW_v01.md`; TF-30 and TF-29 status with evidence.

---

## Appendix A: tools/build.py

```python
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
# Root manifests remain until they are retired (TF-30 Task 5); they must not disagree with VERSION.
ROOT_MANIFESTS = ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json')


def read_version(source):
    version = (source / 'VERSION').read_text(encoding='utf-8').strip()
    for path in ROOT_MANIFESTS:
        manifest = source / path
        if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8'))['version'] != version:
            raise ValueError(f'{path} version differs from VERSION')
    return version


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
    problems = [f'missing: {name}' for name in sorted((set(expected) | set(generated)) - actual)]
    problems += [f'unexpected: {name}' for name in sorted(actual - set(expected) - set(generated))]
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
        path = destination / name
        if name not in actual:
            continue
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
```

## Appendix B: tests/test_build.py

Task 3 Step 3 creates the file with everything above the `# --- Task 4 tests ---` marker; Task 4 Step 2 adds the rest.

```python
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', SOURCE / 'tools/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
VERSION = (SOURCE / 'VERSION').read_text(encoding='utf-8').strip()


def platform(name):
    return build.load_platform(SOURCE, name)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def package(self, name, archive=False):
        out = self.root / name / 'h3c-helper'
        build.build(SOURCE, platform(name), out)
        zip_path = None
        if archive:
            zip_path = self.root / f'{name}.zip'
            build.write_archive(SOURCE, platform(name), out, zip_path)
        return out, zip_path

    def test_aggregate_complete_and_contained(self):
        out, _ = self.package('generic')
        self.assertEqual(list(out.rglob('SKILL.md')), [out / 'SKILL.md'])
        for path in out.rglob('*.md'):
            for match in build.LINK.finditer(path.read_text()):
                target = match.group(1).split('#')[0]
                if not target or ':' in target:
                    continue
                linked = (path.parent / target).resolve()
                self.assertTrue(linked.is_relative_to(out.resolve()))
                self.assertTrue(linked.is_file(), (path, target))
        for folder in ('scripts', 'schemas'):
            for path in (out / folder).glob('*'):
                self.assertEqual(path.read_bytes(), (SOURCE / folder / path.name).read_bytes())
        self.assertEqual((out / 'LICENSE').read_bytes(), (SOURCE / 'LICENSE').read_bytes())
        self.assertTrue(build.verify(SOURCE, platform('generic'), out)['ok'])

    def test_workbuddy_metadata_and_reproducible_zip(self):
        zips = []
        for index in (1, 2):
            out = self.root / str(index) / 'h3c-helper'
            build.build(SOURCE, platform('workbuddy'), out)
            zips.append(self.root / f'{index}.zip')
            build.write_archive(SOURCE, platform('workbuddy'), out, zips[-1])
        self.assertEqual(zips[0].read_bytes(), zips[1].read_bytes())
        header = (self.root / '1/h3c-helper/SKILL.md').read_text().split('---')[1]
        for field in ('description', 'description_zh', 'description_en', 'version', 'author'):
            self.assertIn('\n' + field + ':', header)
        with zipfile.ZipFile(zips[0]) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn('SKILL.md', archive.namelist())

    def test_claude_layout_metadata_and_verification(self):
        out, archive = self.package('claude', archive=True)
        header = (out / 'SKILL.md').read_text().split('---')[1]
        fields = dict(line.strip().split(': ', 1) for line in header.strip().splitlines() if ': ' in line)
        self.assertLessEqual(len(json.loads(fields['description'])), 200)
        self.assertEqual(fields['dependencies'], 'python>=3.10, jsonschema>=4')
        self.assertEqual(json.loads(fields['version']), VERSION)
        with zipfile.ZipFile(archive) as handle:
            self.assertIsNone(handle.testzip())
            self.assertTrue(all(name.startswith('h3c-helper/') for name in handle.namelist()))
        self.assertTrue(build.verify(SOURCE, platform('claude'), out, archive)['ok'])
        generic, _ = self.package('generic')
        for path in generic.rglob('*'):
            if path.is_file() and path.name != 'SKILL.md':
                self.assertEqual(path.read_bytes(), (out / path.relative_to(generic)).read_bytes())

    def test_verify_rejects_content_drift(self):
        out, _ = self.package('generic')
        generic = platform('generic')
        workflow = out / 'references/workflows/h3c-configure.md'
        original = workflow.read_bytes()
        workflow.write_text(workflow.read_text() + '\nAlways save after display output.\n')
        self.assertFalse(build.verify(SOURCE, generic, out)['ok'])
        workflow.write_bytes(original)
        self.assertTrue(build.verify(SOURCE, generic, out)['ok'])
        script = out / 'scripts/h3c_check.py'
        script.write_bytes(script.read_bytes() + b'\n')
        self.assertFalse(build.verify(SOURCE, generic, out)['ok'])
        script.unlink()
        self.assertFalse(build.verify(SOURCE, generic, out)['ok'])

    def test_no_overwrite_or_source_pollution(self):
        for path in (self.root, SOURCE / 'new-output'):
            with self.assertRaises(ValueError):
                build.build(SOURCE, platform('generic'), path)

    def test_broken_reference_and_symlink_rejected_before_writes(self):
        source = self.root / 'source'
        shutil.copytree(SOURCE, source, ignore=shutil.ignore_patterns('__pycache__', 'dist'))
        generic = build.load_platform(source, 'generic')
        reference = source / 'references/test-export.md'
        reference.write_text('[missing](../../private.txt)')
        with self.assertRaises(ValueError):
            build.build(source, generic, self.root / 'broken')
        self.assertFalse((self.root / 'broken').exists())
        reference.unlink()
        reference.symlink_to(source / 'LICENSE')
        with self.assertRaises(ValueError):
            build.build(source, generic, self.root / 'symlink')
        self.assertFalse((self.root / 'symlink').exists())

    # --- Task 4 tests ---

    def test_root_body_identical_across_aggregate_platforms(self):
        bodies = set()
        for name in ('generic', 'workbuddy', 'claude', 'chatgpt'):
            out, _ = self.package(name)
            bodies.add((out / 'SKILL.md').read_bytes().split(b'---\n', 2)[2])
        self.assertEqual(len(bodies), 1)

    def test_plugin_layouts_keep_skills_byte_identical(self):
        for name, manifest in (('codex', '.codex-plugin/plugin.json'), ('claude-code', '.claude-plugin/plugin.json')):
            out, _ = self.package(name)
            for path in (SOURCE / 'skills').rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts and path.name != '.DS_Store':
                    self.assertEqual(path.read_bytes(), (out / path.relative_to(SOURCE)).read_bytes())
            self.assertEqual(json.loads((out / manifest).read_text())['version'], VERSION)
            self.assertFalse((out / 'SKILL.md').exists())
            self.assertTrue(build.verify(SOURCE, platform(name), out)['ok'])

    def test_build_all_writes_report_and_difference_list(self):
        dist = self.root / 'dist'
        report = build.build_all(SOURCE, dist)
        self.assertTrue(report['ok'], report['cross_platform_problems'])
        names = {entry['platform'] for entry in report['platforms']}
        self.assertEqual(names, {'chatgpt', 'claude', 'claude-code', 'codex', 'generic', 'workbuddy'})
        differences = (dist / 'ALLOWED-DIFFERENCES.md').read_text(encoding='utf-8')
        for name in names:
            self.assertIn(f'| {name} |', differences)
        for package in dist.glob('*/h3c-helper'):
            self.assertFalse(any(path.name == 'build.py' for path in package.rglob('*')))
            self.assertFalse((package / 'tools').exists())
        self.assertTrue((dist / f'h3c-helper-chatgpt-{VERSION}.skill').is_file())


if __name__ == '__main__':
    unittest.main()
```

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
        declaration = platform(name)
        out = self.root / name / 'h3c-helper'
        build.build(SOURCE, declaration, out)
        zip_path = None
        if archive:
            zip_path = self.root / f'{name}.zip'
            build.write_archive(SOURCE, declaration, out, zip_path)
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

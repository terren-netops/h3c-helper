# Source and redistribution review

The maintainer selected the [MIT License](../LICENSE) on 2026-09-28, with attribution to Terren. It covers project-authored material; external vendor documents and trademarks are not relicensed.

## Public source review

- Skills, references and templates contain maintained workflow instructions, generic engineering methods and source links. No vendor manual, firmware, slide deck or customer configuration is bundled.
- Python scripts and schemas are project source. Dependencies are not vendored. The optional jsonschema package is installed separately; preserve upstream notices if dependencies are ever bundled.
- Two short vendor-output excerpts formerly used in parser tests were replaced with explicitly constructed fixtures. These test format handling and are not evidence of real device behavior.
- Historical internal source filenames and fingerprints were removed from the public migration note; the maintainer retains the original provenance record privately. No private source is needed to load the skills.
- H3C and its product identifiers are descriptive references. No vendor endorsement or trademark ownership is claimed.

This review identifies the contents of the current distribution. A file scan cannot certify authorship or third-party rights. Report any specific attribution or rights concern to the maintainer with a public source reference; do not upload confidential originals to a public issue. Replace or obtain permission for material found to have uncertain rights before redistributing it.

## Release hygiene

`.gitignore` is an exclusion aid, not a secret scanner or access control. It does not remove tracked files or past commits. Review the exact public file list, diffs and any history, including attachments. Keep credentials, customer evidence, raw logs and internal rights records outside the public repository.

Check the README for current behavior and platform verification limits. Applying MIT does not establish model reliability, Windows support or device-execution readiness.

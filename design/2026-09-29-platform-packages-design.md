# Per-platform packages from shared content

Date: 2026-09-29. Ticket: TF-30. Status: design approved in conversation, pending written-spec review.

## Goal

One copy of the H3C engineering content produces one installable package per platform. Platform adapters describe only packaging differences. Every build re-verifies that no business content changed.

Industry basis: the Agent Skills format (SKILL.md folder with scripts, references and assets) is read by Claude, Codex, Cursor and other agents; platform differences are mainly storage location, trigger metadata and packaging.

## Scope

In scope: Claude Desktop/claude.ai, WorkBuddy, ChatGPT Skills, generic (CodeBuddy/Qoder and similar copy-in hosts), Codex plugin, Claude Code plugin.

Out of scope: any change to workflows, references, templates, schemas, scripts, exit codes or language rules; TF-17/21/25; device access; publication.

## Layout

```
h3c-helper/
├── VERSION                         single version source
├── skills/<five workflows>/SKILL.md   shared, unchanged
├── references/ scripts/ schemas/ assets/ docs/ LICENSE   shared, unchanged
├── platforms/<platform>/platform.json + INSTALL.md (+ manifest templates for plugin layouts)
├── tools/build.py                  moved from scripts/export_skill.py; never packaged
├── design/                         never packaged
├── tests/
└── dist/                           build output, git-ignored
```

Platforms: `claude`, `workbuddy`, `chatgpt`, `generic` use the aggregate layout; `codex`, `claude-code` use the plugin layout.

- Aggregate: one `h3c-helper` skill. A generated root SKILL.md routes to `references/workflows/<workflow>.md`. This is the layout already accepted on WorkBuddy and Claude.
- Plugin: the five skills as separate folders plus a manifest rendered from the platform template, with version from `VERSION`. The repository-root `plugin.json`, `.codex-plugin/`, `.claude-plugin/` and `.agents/` become build outputs.

`platform.json` may declare only: layout, ZIP root prefix, root SKILL.md frontmatter keys and values, description text and length limit, dependency declaration, manifest template, installation notes and known platform limits. It may not contain engineering rules. The root SKILL.md body comes from one template in `tools/build.py` and is identical on every aggregate platform.

## Consistency verification

`verify` re-reads each built directory and ZIP from disk. Any failure makes the build exit non-zero and suppresses that ZIP.

1. Byte-identical: every non-Markdown file under `scripts/`, `schemas/`, `assets/`, and `LICENSE`; plugin-layout workflow SKILL.md files whose links need no relocation.
2. Markdown: after replacing each local link target with the bundled file it designates, the text must equal the source text. The only permitted Markdown differences are relocated link paths and the aggregate move `skills/<name>/SKILL.md` → `references/workflows/<name>.md`.
3. Root SKILL.md: body byte-identical across aggregate platforms; frontmatter key set exactly equals the platform declaration; `name` is `h3c-helper`; version equals `VERSION`; description within the platform limit (Claude: 200 characters).
4. Completeness: file set equals the source mapping; all local links resolve inside the package; no symlinks; build tooling absent from every package.
5. ZIP: valid CRC; entries equal directory files plus the platform prefix; entry bytes equal directory bytes; two builds of the same source give identical ZIP hashes.
6. Cross-platform: shared files are byte-identical between all packages, apart from the documented path conversions.

Manual review item: description wording may change how a platform triggers the skill but must keep the five-workflow business scope. Each description is listed for review in the generated difference list.

`dist/ALLOWED-DIFFERENCES.md` is generated on every build from the platform declarations and actual verification results: per platform, the files transformed, the conversion type, frontmatter values and verification outcome. It is not maintained by hand.

Known platform limit, recorded in `platforms/claude/platform.json`: declaring `dependencies: python>=3.10, jsonschema>=4` did not provision jsonschema in the claude.ai sandbox on 2026-09-29 (case H rc.14). Structured checks there still exit 3.

## Migration

Each step is independently verifiable; the rc.14 snapshot is the rollback point.

1. Open the ticket; snapshot rc.14; record hashes of the current generic, WorkBuddy and Claude ZIPs and of the root plugin files.
2. Move `scripts/export_skill.py` to `tools/build.py`; update test paths. Verify the three ZIP hashes are unchanged.
3. Move hard-coded platform constants to `platforms/*/platform.json`; add `VERSION`. Verify the three ZIP hashes are still unchanged.
4. Add `chatgpt`, `generic`, `codex` and `claude-code` packages. Verify plugin skills are byte-identical to source, rendered manifests match the current root manifests except for the version source, `claude plugin validate dist/claude-code --strict` passes, and the Codex manifest is checked with an available local validator or explicitly marked unverified.
5. Retire the root manifests (kept in the snapshot) and update README and install instructions. This changes Codex/Claude Code installation and requires separate user confirmation before execution.
6. `python3 tools/build.py --all` builds every package, the difference list and a combined verification report; any failure exits 1.

## Tests

Keep the existing 43 unittest cases. Add: per-platform frontmatter key sets and limits; identical root bodies; manifest version equals `VERSION`; reproducible ZIPs; tamper detection for a changed script byte, an added Markdown rule and a deleted file; build tooling absent from packages. Standard library only.

## Real acceptance

Pipeline: main source update → generated packages → consistency verification → installation and real behavior acceptance, recorded separately from consistency results.

- Claude: Replace upload of the generated ZIP; runtime sha256 of all files; one natural-trigger case and one script case in fresh sessions.
- Codex / Claude Code: temporary registration/installation and listing from `dist/`, then removal. The user's existing personal installation is not changed without separate approval.
- WorkBuddy and ChatGPT: build and verify only; reinstallation requires the user's login and is not part of this change.
- No device connection and no publication.

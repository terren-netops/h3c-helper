# Claude Desktop and claude.ai custom skill

1. Run `python3 tools/build.py --all`; it must exit 0.
2. Settings > Capabilities: "Code execution and file creation" must be on.
3. First install: Customize > Skills > Add > Upload skill, select `dist/h3c-helper-claude-<version>.zip`. Update or roll back: the skill's "..." menu > Replace, select the new or earlier ZIP (there is no version history to pick from).
4. Verify in a fresh chat: ask the skill to run `cd /mnt/skills/plugins/h3c-helper && find . -type f | LC_ALL=C sort | xargs sha256sum` and compare every hash with `dist/claude/h3c-helper`.

The `dependencies` declaration did not provision jsonschema in the claude.ai sandbox on 2026-09-29, so structured checks exit 3 there.

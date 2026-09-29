# Generic skill folder (CodeBuddy, Qoder, QoderWork and similar hosts)

1. Run `python3 tools/build.py --all` from the source root; it must exit 0.
2. Copy the complete `dist/generic/h3c-helper` folder into the host skills directory: CodeBuddy `.codebuddy/skills/`, Qoder CLI `.qoder/skills/` or `~/.qoder/skills/`, QoderWork `~/.qoderwork/skills/`.
3. Start a new session and confirm the skill is listed. Copying a single SKILL.md is insufficient.

These routes come from each product's documentation; no installed client of these hosts has been tested.

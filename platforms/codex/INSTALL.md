# Codex plugin

1. Run `python3 tools/build.py --all`; it must exit 0.
2. With a Codex version whose `codex plugin --help` lists `marketplace`, `add` and `list`, from `dist/codex/h3c-helper`:
   `codex plugin marketplace add .`, then `codex plugin add h3c-helper@h3c-helper-local`, then `codex plugin list --marketplace h3c-helper-local --json`.
3. Confirm installed/enabled and that the version matches `VERSION`. Start a new task and use `$h3c-configure` or another listed skill.

Do not overwrite an existing personal marketplace. The codex CLI was not available on the build Mac on 2026-09-29.

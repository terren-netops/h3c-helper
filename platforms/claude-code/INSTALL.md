# Claude Code plugin

1. Run `python3 tools/build.py --all`; it must exit 0.
2. `claude plugin validate dist/claude-code/h3c-helper --strict` must pass.
3. Session loading: `claude --plugin-dir /absolute/path/to/dist/claude-code/h3c-helper`, then use `/h3c-helper:h3c-configure` or another listed skill.

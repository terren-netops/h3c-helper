Download the package for your platform. Every package is built from the same source by `tools/build.py` and verified: shared scripts, schemas and templates are byte-identical, and Markdown differs only by relocated link paths. See `ALLOWED-DIFFERENCES.md` and `SHA256SUMS.txt`.

| Platform | File | Install |
|---|---|---|
| Claude Desktop / claude.ai | `h3c-helper-claude-<version>.zip` | Customize > Skills > Add > Upload skill |
| WorkBuddy | `h3c-helper-workbuddy-<version>.zip` | Skills > Add skill > Upload skill |
| ChatGPT Skills | `h3c-helper-chatgpt-<version>.skill` | chatgpt.com/skills upload |
| CodeBuddy / Qoder / other skill hosts | `h3c-helper-generic-<version>.zip` | Unzip into the host's skills directory |
| Codex | `h3c-helper-codex-<version>.zip` | Unzip, then `codex plugin marketplace add .` |
| Claude Code | `h3c-helper-claude-code-<version>.zip` | Unzip, then `claude --plugin-dir <folder>` |

Known issues and per-platform verification status are listed at the top of README.md and in `platforms/<platform>/INSTALL.md`. The tools never connect to devices; review recommendations against current H3C documentation. MIT licensed; not affiliated with or endorsed by H3C.

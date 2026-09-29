# Local installation

Build the packages first with `python3 tools/build.py --all` (Python 3.10+, no dependency); it must exit 0. Install from the complete package under `dist/`, not from the source root. The current README identifies the tested version and unresolved acceptance limits. Installing a candidate does not validate its advice. The optional Python tools do not connect to devices; your AI host may send inputs to its model provider.

## Codex

Prerequisite: a Codex version whose `codex plugin --help` exposes `marketplace`, `add` and `list`. From `dist/codex/h3c-helper`:

```sh
codex plugin marketplace add .
codex plugin list --marketplace h3c-helper-local --available --json
codex plugin add h3c-helper@h3c-helper-local
codex plugin list --marketplace h3c-helper-local --json
```

The generated `.agents/plugins/marketplace.json` points to this package directory. Confirm the listed source path is the intended directory and the installed version matches the README. If another checkout already owns this marketplace name, reconcile it before proceeding. Start a new task after installation; use `$h3c-configure` or another skill listed in the README.

The previously documented `h3c-helper@personal` belongs to the maintainer's own setup and is not required. Do not overwrite an existing personal marketplace file.

Registration, installation and installed/enabled listing for 0.9.1-rc.9 were verified on macOS using the local CLI, then the temporary installation and registration were removed. This proves packaging/loading, not model behavior or device execution. Windows remains untested. Follow [OpenAI's plugin packaging guide](https://developers.openai.com/plugins/build/plugins) if your host exposes a different installation surface.

## Claude Code

From the project root, after building:

```sh
claude plugin validate dist/claude-code/h3c-helper --strict
claude --plugin-dir dist/claude-code/h3c-helper
```

Use `/h3c-helper:h3c-configure`, `/h3c-helper:h3c-troubleshoot`, `/h3c-helper:h3c-design-network`, `/h3c-helper:h3c-select-products` or `/h3c-helper:h3c-service-support`.

Session loading and actual Skill calls were tested on macOS. This is not permanent plugin installation. See [Claude Code's plugin documentation](https://code.claude.com/docs/en/plugins) for that separate workflow.

## Optional offline tools

The skills' Markdown workflows do not require Python. To run the included scripts, use Python 3.10+; structured checks and engineering tools require jsonschema 4.x. Use your approved package/environment setup. Nothing in this project automatically installs dependencies.

From the project root, with dependencies already available:

```sh
python3 -m unittest discover -s tests -v
```

On Windows, first identify the available Python 3.10+ launcher (for example `py -3`); do not assume `python3` exists. Windows launcher, path and symlink behavior remain untested. See [local tool instructions](../references/local-tools.md) for individual commands.

# Contributing

Project-authored contributions are distributed under the [MIT License](LICENSE). The public repository is not published yet. See [source rights](docs/source-rights.md) before redistributing this candidate.

Keep changes focused on one observed problem. Describe the expected and actual behavior, affected host/version and relevant full device model/Release. Use sanitized examples; never attach passwords, keys, customer configurations, internal training materials or raw production logs to a public issue or pull request.

Preserve the Skills-only architecture. An execution proposal must explicitly identify its scope and evidence; software checks do not demonstrate safe device operation. Do not test a contribution by writing to a production device.

From the project root, run `python3 -m unittest discover -s tests -v` with Python 3.10+ and the existing jsonschema 4.x dependency available. Validate both host manifests and each skill with the host's available validators, check relative links, and record failures or skips. A guidance change also needs actual host-model regression cases; unit tests alone do not validate assistant behavior. Windows remains unverified.

Keep source versions aligned across the three manifests. Update README scope and validation evidence, including unresolved limitations. Contributions must identify third-party content and its redistribution terms. Reference vendor documentation rather than copying manuals or internal materials.

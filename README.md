# H3c Helper

> **Pre-release.** 0.9.1-rc.14 is an evaluation candidate, not a stable release. Known open issues: network-design failure-domain reasoning (TF-17), evidence-uncertainty wording (TF-21) and novice VLAN explanations on some hosts (TF-25). The batch-script and optics fixes (TF-24, TF-28) have been retested on Claude only. Review every recommendation against current official documentation; this project never connects to devices. Download the package for your platform from the [GitHub Releases page](https://github.com/terren-netops/h3c-helper/releases), or build all packages with `python3 tools/build.py --all`.

Current source version: **0.9.1-rc.14** (review candidate). Codex was observed installed/enabled at 0.9.1-rc.1 on 2026-09-28. The rc.12 portable export was installed in WorkBuddy on 2026-09-29; no public release has been made. TF-15 targeted configuration gates passed the rc.11 Claude cases, but WorkBuddy batch-script pressure failed (TF-24). Design reasoning (TF-17), evidence wording (TF-21) and novice VLAN explanations (TF-25) remain open. Windows and device execution remain unverified.

English-first workflows for H3C configuration review, troubleshooting, network design, product selection and service support. The plugin combines five skills with optional offline engineering tools. It uses the host's available file and research capabilities.

## Start a task

In Codex, after installation start a new task and ask naturally, or invoke a skill:

| Skill | Example request |
|---|---|
| `$h3c-configure` | Review this H3C configuration. Identify the platform and Release, then recommend minimal changes with verification and rollback steps. |
| `$h3c-troubleshoot` | Diagnose these logs. Separate observations from hypotheses and give the next checks. |
| `$h3c-design-network` | Design a campus network with explicit capacity assumptions and failure domains. |
| `$h3c-select-products` | Compare these complete model numbers, verify compatibility and prepare a BOM. |
| `$h3c-service-support` | Draft an English TAC case using the symptoms, impact and checks already completed. |

English is the default for responses, templates and generated headings. An explicit request for another language takes precedence. Commands, model numbers and identifiers retain their original spelling. Simple requests receive concise answers; templates support more complex work.

## Support and verification matrix

| Host / mode | Evidence and current limit |
|---|---|
| Codex on this Mac: skills and offline tools | Local installation, official validators and software tests; constructed behavior cases are separate from device evidence |
| Claude Code on macOS: plugin registration | Five skills registered in external 0.8.0 evaluation; explicit manifest added in 0.8.1. Current manifest validation does not establish actual Skill injection |
| Claude Code model behavior | Actual Skill calls cover all five workflows in rc.11 (nine fresh contexts, ten replies) on Claude Code 2.1.283/macOS. B4 intake/pressure, P17/P18 core persistence gates and exception handling passed scoped independent review. The original design still fails technical criteria (TF-17); minor evidence wording issues are recorded separately (TF-21). These constructed model cases are not device execution tests |
| WorkBuddy 5.6.2 on macOS arm64 | rc.12 ZIP imported/enabled; 45 files match. Ten fresh real-host cases: six scoped passes, three failures, one partial. All five workflow paths accessible; Chinese/space paths and dependency exit codes exercised. Fast routed to Deepseek-V4.1-Flash or GLM-5.3-Flash. Batch-script safety, design and concept accuracy failed; not accepted for device execution. Lifecycle tests remain pending |
| Windows: either host | Not tested; launcher/path and symlink privileges need real Windows validation |
| Claude Desktop / claude.ai custom skill | rc.12 and rc.14 packages uploaded via Customize > Skills (Chat and Cowork); runtime files sha256-identical to the package. Opus 5.5 fresh sessions: rc.14 retests of batch-script pressure, optics intake and their complete-input counterexamples pass; bundled scripts run, but jsonschema is absent in the sandbox even with a dependencies declaration. See the TF-26/TF-30 reports |
| Device execution / unattended batches | No bundled executor. External runner, credentials, reachability, model/Release and recovery validation remain required |

A limited production read-path check on a WX1810H-PWR running Comware 7.1.064 R5482 verified SSH login, four status reads, paging and logout through external OpenSSH/pexpect. It did not test this plugin as an SSH executor, configuration writes, business service acceptance, save or recovery. Customer evidence and credentials are excluded from this package.

Use the [unified acceptance protocol](docs/acceptance.md) for real test gates and the [external runner contract](references/runner-contract.md) when integrating execution. This matrix separates documentation, local software, model behavior and device evidence; no row implies another is verified.

## Assistance that adapts to the task

You do not need to choose a role or pass an expertise quiz. The skills adapt to the immediate objective, urgency and familiarity with the specific topic. Explanation depth and interaction pace are independent; ask for either explicitly when useful.

- "I am new to this. Explain what to inspect and help me interpret the output."
- "I know LACP. Review my diagnosis, identify contrary evidence and give the next decisive check."
- "This is an outage. Give me the next useful checks; explain the theory later."
- "Give me the full change plan, with concise reasoning and verification."

A customer engineer can receive expert-level analysis, and a field engineer can request guided learning in an unfamiliar area. Simple conceptual questions receive direct explanations. Device-specific actions still need applicable evidence and authorization. See [adaptive assistance](references/engineer-audiences.md).

## What is included

- `skills/`: five workflow entry points and English UI metadata.
- `references/`: evidence policy, platform boundaries, troubleshooting playbooks and tool instructions.
- `assets/templates/`: change, incident, design, comparison, service, evidence, upgrade and handoff templates.
- `scripts/`: optional CLI profiling, structured validation, physical topology rendering, declared resilience analysis and audience-specific handoff drafts.
- `schemas/` and `tests/`: input definitions and software regression checks.
- `VERSION`: the single source version.
- `platforms/<platform>/`: packaging differences only (layout, archive root, root frontmatter, manifest templates, installation notes) for claude, workbuddy, chatgpt, generic, codex and claude-code.
- `tools/build.py`: builds one verified package per platform into `dist/` and generates `dist/ALLOWED-DIFFERENCES.md`; it is never packaged.
- [Migration record](docs/migration.md): provenance and exclusions.

## Open-source preparation

Published as a pre-release at https://github.com/terren-netops/h3c-helper. Project-authored code and documentation use the [MIT License](LICENSE). Vendor documentation, trademarks and excluded private materials are not relicensed. See [source and redistribution review](docs/source-rights.md) and [contribution guidance](CONTRIBUTING.md). Current content review found no remaining concrete proprietary passage or real credential; this is not a certification of third-party rights.

Local loading does not mean local model inference. Your host may send prompts, configurations and tool outputs to its model provider. Minimize and redact inputs before sharing them with a model, and follow your organization's data policy. The included Python tools run locally when invoked directly; this does not make the surrounding AI session offline.

Install a complete package built under `dist/`. Copying only one `SKILL.md` breaks its relative links. Start with a sanitized configuration review or a conceptual question; installation itself grants no device-change authorization. This project is independent and is not endorsed by H3C.

## Portable local skills

Every platform receives a package built from the same shared content: `python3 tools/build.py --all` writes `dist/<platform>/h3c-helper` and an archive per platform, re-reads each package and exits 1 on any difference beyond the declared conversions. WorkBuddy, Claude, ChatGPT, CodeBuddy and Qoder-family hosts use a self-contained skill with all five workflows. See [agent compatibility and build instructions](docs/agent-compatibility.md). WorkBuddy import and scoped runtime tests completed with behavioral failures; CodeBuddy and Qoder-family client tests remain pending. The original five plugin skills stay canonical.

## Installation and updates

For a new machine, use the [local installation guide](docs/install.md). It includes a checkout-local Codex marketplace and Claude Code session loading.

The maintainer-specific local installation uses `h3c-helper@personal`; this is not a public marketplace identifier. Do not use it on another machine unless you have configured that marketplace. Where that marketplace already points to the source, reinstall with `codex plugin add h3c-helper@personal` and inspect `codex plugin list --marketplace personal --json`. Start a new task to load updated skills.

Maintain the shared source directly and never edit generated packages. Record user-visible changes under a distinct `VERSION` and update this README with scope, validation and limitations. Plugin manifests are generated from `platforms/codex` and `platforms/claude-code` templates. The `+codex.<timestamp>` suffix refreshes the local installation cache; it does not replace the source version. Use the official plugin-creator cachebuster/reinstall flow. Do not create a separate enhancement ZIP for routine updates.

## Claude Code (local loading)

Keep the entire plugin directory together: individual skills reference shared files outside their own folders. From a local terminal, build the packages and load the Claude Code package for the session:

```sh
python3 tools/build.py --all
claude --plugin-dir /absolute/path/to/h3c-helper/dist/claude-code/h3c-helper
```

Replace the path with the actual plugin root on another machine. Use natural language or these Claude Code invocation names:

- `/h3c-helper:h3c-configure`
- `/h3c-helper:h3c-troubleshoot`
- `/h3c-helper:h3c-design-network`
- `/h3c-helper:h3c-select-products`
- `/h3c-helper:h3c-service-support`

The `$h3c-*` examples and `codex plugin add` above are Codex-specific. Claude Code uses the generated `.claude-plugin/plugin.json`, whose version comes from `VERSION`. Codex cache metadata may carry an additional `+codex.<timestamp>` suffix. Check the package with `claude plugin validate /absolute/path/to/h3c-helper/dist/claude-code/h3c-helper --strict`. Loading or validation is not proof of model behavior or device support.

External evaluation of 0.8.0 on Claude Code 2.1.280 / macOS arm64 registered all five skills and passed 22 software tests. Its behavior evaluation used independent Claude subagents reading skills, not end-to-end Skill-tool injection: CLI OAuth had expired. One batch-script scenario failed; 0.8.1 adds a targeted correction. Later authenticated Claude end-to-end replay is recorded in the current support matrix; permanent Claude installation and Windows remain unverified. One production AC has limited read-only evidence through an external host tool; configuration execution remains unverified. On Windows, first verify the available Python 3.10+ launcher, paths and symlink-test permissions; do not assume the macOS command examples work unchanged.

## Optional local tools

See [local tools](references/local-tools.md) for commands and [operation boundaries](references/operation-policy.md) for change planning. Scripts require Python 3.10+; structured validation and engineering tools also require jsonschema 4.x (MIT). Preflight and the experimental journal use only the standard library. No automatic dependency installation occurs. Without execution support or dependencies, the skills still provide Markdown analysis and drafts; state which checks were not run.

From the plugin root, run existing software tests with:

```sh
python3 -m unittest discover -s tests -v
```

Validate the plugin and all five skills with the host's official validators. Check relative references and affected behavior before updating an installation.

## Evidence and limitations

This is a Skills-only assistant, not an official H3C product, complete command database or entitlement system. It has no MCP server, device executor, remote backend or message sender. Host tools may retrieve documentation when available and authorized. Official documents must match the full model and Release before technical examples can be applied.

Local checks validate declared constraints; they do not establish approver identity, source authenticity, device behavior, compatibility or service acceptance. Catalog scope filters are not filesystem access control. CLI profiling supports limited formats and retains unknowns. Resilience results do not establish single-flow throughput, concurrent demand capacity, convergence or SLAs. Handoffs remain drafts.

Structured records retain schema_version=1 and optional engineering fields. Saved results under separate_approval require genuine save authorization. Historical quotes remain historical; not_checked and engineering_status identify coverage limits. Existing Markdown workflows remain supported. English handoff labels are the default; explicit `--language zh` translates headings, audience and category labels while preserving supplied facts and technical/status identifiers.

Internal materials are used only within authorized tasks and are excluded from redistribution. The original Technical Support and Empowerment presentation was unavailable during migration; related files are not substitutes. Software tests are not lab or production-device validation. Online upload, review, publication and cross-host acceptance are separate from local installation.

Retain prior source snapshots for rollback and restore to a separate directory before registration. Do not overwrite unsaved work. Plugin rollback does not undo device configuration changes.

## Version history

### 0.9.1-rc.14 — 2026-09-29 (batch-script and optics guard candidate, not released)

Packaging (TF-29/TF-30): `scripts/export_skill.py` moved to `tools/build.py`; per-platform declarations under `platforms/`; single `VERSION`; root plugin manifests retired in favor of generated packages under `dist/`. Every build verifies byte identity of shared non-Markdown files, link-only Markdown differences, declared frontmatter and archive contents, and writes `dist/ALLOWED-DIFFERENCES.md`. Generic and WorkBuddy archives were byte-identical before and after the move.

TF-24: the configure workflow states that urgency or requests to skip process do not change the batch evidence state, forbids runnable write/save scripts before qualified implementation, and forbids runner defaults that disable host-key verification, push to all targets at once or save on display/absent-error text alone. The exported root skill routes device-push requests to the configure workflow and batch commissioning first. TF-28: missing device model, port/card, Release or transceiver part makes an optics compatibility conclusion insufficient evidence, even when a direct answer is requested. No executor, runtime or schema change. Real-host retests are recorded in the Claude acceptance report; other hosts are not retested.

### 0.9.1-rc.13 — 2026-09-29 (production evidence collection candidate, not released)

Add production fault-information collection guidance to the existing evidence reference, troubleshooting entry point and incident template: preserve the scene, separate backup from authorization, bound diagnostic load and neighbor scope, record clock provenance without changing clocks, name and redact captures, sample according to fault timescale and compare applicable baselines. No executor, runtime or schema change. Software/reference/export checks are separate from real-host behavior; rc.13 model and device validation remain pending. Existing TF-17/21/24/25 findings are not claimed resolved. Installed WorkBuddy and ongoing Claude Desktop rc.12 artifacts remain unchanged.

### 0.9.1-rc.12 — 2026-09-28 (portable skill candidate, not released)

Add a standard-library exporter for one self-contained local skill, with generic and WorkBuddy metadata targets. Preserve five canonical workflows, relocate resource links, retain MIT and byte-identical runtime helpers/schemas, and document CodeBuddy/Qoder installation routes. Forty-one software tests and host format checks pass; domestic-client import/invocation and Windows remain untested. TF-17/TF-21 remain open.

### 0.9.1-rc.11 — 2026-09-28 (review candidate, not released)

Make save-result and startup-content verification explicit for all persistence policies, including interruption and later recovery. Distinguish same-VLAN switching from dependence on a firewall-hosted default gateway. These target concrete residual findings in rc.10; runtime code is unchanged. Actual Claude Code 2.1.283 replay completed: all five skills invoked across nine fresh contexts and ten replies. Earlier failures remain in the evaluation history. This round still contains unsupported absolute claims in the original design and persistence wording gaps; public release remains blocked. Software/package checks are reported separately from model acceptance.

### 0.9.1-rc.10 — 2026-09-28 (review candidate, not released)

Keep early availability alternatives functional until gateway roles and platform support are known. Clarify that a redundant transit core can preserve access to a firewall-hosted gateway; core redundancy does not require core-hosted routing. This addresses the rc.9 design reply's false prerequisite. Also preserve actual earlier-target persistence when isolating a later failure. Runtime code is unchanged; configuration and design replays are pending.

### 0.9.1-rc.9 — 2026-09-28 (review candidate, not released)

Use explicit evidence states to keep incomplete batch requests at intake, preserve each target's own baseline, and distinguish proposed paths from installed evidence in design reviews. Add a portable local marketplace and installation instructions. rc.8 still selected premature pilots and overstated physical evidence; regression for this candidate is pending.

### 0.9.1-rc.8 — 2026-09-28 (review candidate, not released)

Restructure configuration intake around the current deliverable; qualify design alternatives without invented cost, failure-frequency or convergence ranking. Replace two quoted manual test excerpts with labeled constructed parser fixtures, correct two source-index descriptions and move historical source fingerprints out of the public migration note. Runtime code is unchanged. Actual model regression is pending; rc.7 still failed pressured future promises and included unsupported design recommendations.

### 0.9.1-rc.7 — 2026-09-28 (review candidate, not released)

Apply the maintainer-selected MIT license. Clarify incomplete-input progression, runbook evidence handling and service-path reasoning for partial redundancy. Runtime scripts and schemas are unchanged. Actual host behavior replay and redistribution review are in progress; no execution or publication claim.

### 0.9.1-rc.6 — 2026-09-28 (open-source preparation, not released)

Add repository exclusion rules, contribution guidance, source-rights review and local-versus-cloud data boundaries. All five skill bodies, scripts, schemas and tests are unchanged from rc.5. License, redistribution rights and public repository setup remain pending. TF-15 and TF-17 remain open; this documentation update does not establish behavioral acceptance. A separate aggregate rc.5 skill was uploaded to the maintainer's personal ChatGPT library; that upload was not public plugin publication.

### 0.9.1-rc.5 — 2026-09-28 (review candidate)

Make the interrupted-operation distinction explicit for both running state and startup persistence, including hypothetical explanations: neither partial application nor unsaved state follows from a lost session. This targets the contradictory rc.4 B4 response. Actual rc.5 replay completed (three sessions, four replies). Save/business/UNKNOWN handling improved; independent review still found premature push promises without a complete plan and incomplete raw-output handling in the positive runbook. Exceptions passed scoped criteria. The separate TF-17 network-design reasoning finding remains open; this candidate is not ready for public release. Clean-directory validation passed 37 software tests, both host manifests, five skill validators and 108 links. The other four skill bodies are byte-identical to the rc.4 evaluation; their earlier results are carried evidence, not new rc.5 model runs.

### 0.9.1-rc.4 — 2026-09-28 (review candidate)

Keep incomplete-input replies focused on current preparation and the next supported action, without prematurely promising a runnable collector or later push sequence. The rc.3 replay improved business/save gates and management-impact wording but invented a collection-time estimate and unverified immediate readiness; that round did not pass. Actual rc.4 evaluation completed: eight constructed cases through real Claude Skill invocation; six met their scoped criteria, B4 and the network-design case failed. B4 inferred a partly applied, unsaved state after disconnect despite calling the outcome unknown. The design case understated the WAN value of core redundancy (TF-17). No runtime code or production device was changed.

### 0.9.1-rc.3 — 2026-09-28 (review candidate)

Replace the configure entrypoint's repeated automation warnings with explicit change, acceptance, persistence and wave decisions covering code, runbooks and follow-up promises. Distinguish current baseline from a compatible backup and management access risk from an unsupported guarantee. Keep complete-input progression and separately approved earlier-save policies. No SSH executor or runtime code change is included. Actual rc.3 replay: positive baseline/save-policy and exception cases passed their core criteria; the B4 pressure reply still failed an unsupported timing/readiness claim. TF-15 remains open.

Intended release scope is five Skills-only engineering workflows and optional offline tools. The journal remains experimental; unattended device execution and Windows support are not claimed. Final public submission requires a reviewed distributable, actual target-host checks and publisher/listing materials.

### 0.9.1-rc.2 — 2026-09-28 (not released)

Add an experimental [offline transition journal](references/execution-journal.md): durable pre-write intents, attempt-bound checks, save/wave gates and explicit interruption reconciliation. Uses SQLite from the standard library; no new dependency, SSH transport or bundled device executor. Its API checks caller-supplied state; it does not authenticate evidence/authorization or enforce controls on a runner that bypasses it. Only do-not-save and save-after-acceptance are supported; exceptions block the job conservatively. Existing change schemas are unchanged.

Validation on this Mac: 37 software tests passed (27 existing plus 10 journal tests), zero skips; the 10 journal tests also passed with third-party package loading disabled (`python3 -S`). Five skill validators, Codex plugin validation, Claude strict manifest validation and 108 relative links passed. Independent review found no blocking defect. Evidence is recorded in TF-16 and the local review report. Local database tests do not close the TF-15 Claude behavior gap, demonstrate device readiness, or establish Windows compatibility. A subsequent authenticated rc.2 Claude replay (three sessions, four replies) confirmed B4 remains incomplete: no push code was emitted, but an unsupported disconnect assertion and future business-save gate omission persisted. Exception-case checks passed; the positive runbook preserved P17/P18 save ordering but assumed backup equivalence to current baseline in one step. Original transcripts and findings are retained in the local review report.

### 0.9.1-rc.1 — 2026-09-28 (not released)

Target the authenticated Claude B4 failure observed in 0.9.0: define incomplete-input drafts as having no reachable device-write/save path, including behind an apply flag. Review actual code branches for evidence-bound manual/business gates and secret-safe error handling. Surface unsupported device/recovery claims at the configure entrypoint. Complete-input planning and authorized implementations remain supported. This is guidance, not an SSH executor or proof of model reliability. Original 0.9.0 live Claude results supersede its earlier authentication blocker: actual Skill injection worked, the positive runbook passed, and pressured script generation failed. Retest: three authenticated Claude B4 two-turn runs across targeted corrections, plus one complete-input runbook and one exception-case response (five fresh contexts, eight replies). The final B4 no longer emits write/save code, but its promised future sequence still does not clearly preserve business acceptance before saving. Positive/exception cases passed scoped review on the first candidate. At that evaluation TF-15 remained partial and no candidate installation was performed. No arbitrary-script or device reliability claim.

### 0.9.0 — 2026-09-28

Complete the local operational guidance and acceptance scope:

- Add an offline host inventory command without connection, credential discovery or installation.
- Define the external runner evidence/ownership/data contract and continued progress when inputs and authorization suffice. This is a specification, not implemented runtime enforcement.
- Map requirements to add/modify/remove/preserve decisions and checks; account for concurrent human changes, durable unknown attempts, restart reconciliation and plan-specific save ordering.
- Distinguish diagnostic file writes and disruptive failover tests from status reads.
- Improve handoff diagnostics with an additive allowlisted `code` while preserving legacy `error` and exit codes; translate Chinese audience/category labels without translating facts.
- Clarify unsupported interface-brief parsing; separate privilege-dependent symlink testing from other evidence-boundary tests, reporting any skip explicitly.
- Publish the support matrix and paired positive/negative acceptance protocol. Real Windows, authenticated Claude Skill injection and device execution remain separate pending gates.

Validation on this Mac (2026-09-28): 27 software tests passed with zero skips; 10 local CLI fixture cases passed, including isolated missing-dependency handling; five skill validators, Codex plugin validation, Claude strict manifest validation and 103 relative links passed. An independent code review found no blocking defect. Two fresh Codex participant contexts produced a complete-input operator runbook and an interruption/drift/identity exception response; author review passed the scoped criteria. These were constructed single-response cases, not actual runner execution or a Claude model retest. Claude auth status reported loggedIn=false, so real Skill injection remains pending.

No new external dependency, bundled runner, public release or enhancement archive. Schema version and existing consumers remain compatible. Final per-layer validation results are retained with the release evidence; no blanket cross-platform or fleet-readiness claim.

### 0.8.1 — 2026-09-28

Add the Claude Code manifest and host-specific loading/invocation instructions while retaining one shared set of skills and resources. Extend batch guidance explicitly to generated push scripts: reviewed per-device plans, wave gates, trusted host keys, evaluated acceptance/save policy and unknown-state recovery must remain in the executable behavior. No runner or dependency is added; offline code and schemas are unchanged. Original external evaluation limitations remain visible above. Targeted validation evidence is recorded separately; this change is not a claim of Claude or device acceptance.

### 0.8.0 — 2026-09-25

Pilot-first batch commissioning workflow:

- Establish direct SSH, jump-host or bootstrap access needs; distinguish planning from available execution capability.
- Group devices by role and actual applicability; validate representative pilots, then review concrete per-device template differences.
- Define one scoped batch authorization, save policy, wave/dependency ordering and local/group/global stop conditions.
- Track per-device outcomes, inspect state after timeouts and reconcile checkpoints before resuming.
- Close against business tests, temporary changes and actual startup persistence.

See [batch workflow](references/batch-commissioning.md) and [batch record](assets/templates/batch-commissioning.md). This release adds guidance and a Markdown record only: no SSH executor, new dependencies, credential handling implementation or device operations. Existing script/schema interfaces are unchanged. Validation covers official plugin/five skill checks, reference integrity, source/cache consistency and static workflow scenarios; no live rollout or new model-response evaluation is claimed.

### 0.7.0 — 2026-09-25

Evidence intake and case continuity:

- Reconcile device/site identity, capture times and planned/reported/running state before combining supplied material; filename recency and matching IPs are not identity proof.
- Request the smallest decisive missing information with a way to obtain it; reuse attachments and prior checks.
- Track corrections, scoped exclusions, completed versus proposed actions, temporary changes and next checks within the task. Resume without repeating the intake questionnaire.
- Distinguish last reported action from freshly verified state; missing restoration or save evidence stays unconfirmed.
- Provide a concise handover when requested, without claiming automatic cross-task memory.

See [evidence intake and continuity](references/evidence-and-continuity.md). English default, Skills-only architecture and offline tool interfaces are unchanged.

Behavioral evaluation uses independent model participants and explicitly constructed inputs, not real customer/device evidence. A three-turn novice case is compared with 0.6.1; a two-turn expert case checks correction handling, counter continuity and TAC preparation. Baseline already handled the main identity and VLAN boundaries, so no broad improvement rate is claimed. Candidate handoff initially overstated ACL restoration status. The guidance was corrected; a fresh participant's targeted handoff retest retained both restoration and persistence as unconfirmed. In total, four independent participant contexts produced nine actual replies: three baseline, three initial candidate, two expert and one targeted retest. The primary author reviewed the replies against prewritten criteria; this is a small qualitative evaluation, not independent grading or a statistical success rate. The targeted retest did not replay the entire three-turn case.

Validation: official plugin/five skill validators and relative links passed; final installed source comparison recorded. Scripts, schemas and software tests are unchanged, so the previous 22-test result is not claimed as a new run. Real customer incidents, device commands and live acceptance were not tested.

### 0.6.1 — 2026-09-25

Progress-aware assistance and escalation:

- Separate help-seeking behavior from experience; support early peer/TAC requests without forcing a self-help checklist.
- Continue checks that add evidence, including useful failed experiments; redirect unchanged retries and uncontrolled changes.
- Judge escalation by service impact, recovery options and missing capability rather than a fixed attempt count.
- Provide concrete, non-blaming pushback with a useful alternative and a focused handoff question.
- Correct the assistant's own inapplicable advice and account for any resulting state changes.

Validation: official plugin/five skill checks, relative references and installed source consistency checked; six contrasting cases reviewed as static instruction coverage. No new model-response evaluation or device test. Script/schema interfaces and English default remain unchanged.

### 0.6.0 — 2026-09-25

Adaptive help for different levels of topic familiarity:

- Choose assistance from the task goal and urgency rather than employer or job title.
- Separate explanation depth from interaction pace; support guided checks, complete plans and direct peer review.
- Interpret returned evidence and adjust the next step; avoid repeated questionnaires and unnecessary teaching during outages.
- Explain concepts without demanding unrelated device details; preserve model/Release checks for dependent technical claims and commands.
- Support technical disagreement through assumptions, counterevidence and decisive checks. Familiarity does not change authorization or evidence requirements.
- Keep one shared reference across the five workflows; improve explicit training guidance without adding tools or schemas.

Validation: official plugin/five skill checks, relative links, source/cache comparison and six contrasting scenarios reviewed statically. No new independent model-response trials or real-device tests are claimed. Tool code is unchanged; the 22 software-test result recorded under 0.5.0 is historical, not a new behavioral score for 0.6.0.

### 0.5.0 — 2026-09-25

Field and customer engineering workflows:

- Distinguish field engineers, customer engineers and business stakeholders. Customer operators retain the technical detail needed to act.
- Explain check location, purpose, command applicability, output fields, result branches, impact and evidence to return.
- Separate reported patch installation, verified running state, service recovery, observation, root cause and customer acceptance.
- Make handover questions, next owners and escalation conditions explicit.
- Route the five skills to focused [audience guidance](references/engineer-audiences.md) and [service acceptance](references/service-acceptance.md); update troubleshooting and handoff templates.

Compatibility: English remains the default; explicit language requests are supported. Skills-only architecture, script interfaces and schema versions are unchanged.

Validation: official plugin and five skill checks, 22 existing software tests and relative-link checks passed for the engineering update. Source and installed cache were compared. Six scenarios received static guidance review, not independent model-response evaluation. Real customer case trials, device validation and public publication remain outstanding.

### 0.4.0 — local engineering baseline and English update

Offline engineering tools, evidence checks and five workflows. The 2026-09-25 English update translated the interface, skills, references and templates, and refreshed the local cache while retaining the 0.4.0 base version. Cache timestamps distinguish those historical local builds.

### 0.4.1 — separate distribution preparation, 2026-09-21

An independent Skills-only distribution copy was prepared from the earlier engineering baseline. It did not replace the installed local source. This historical package is not the current source and does not establish public publication.

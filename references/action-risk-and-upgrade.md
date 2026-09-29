# Action impact, security baseline and upgrade review

These are review rules, not execution permissions. See [engineering sources](engineering-sources.md). Neither a command prefix nor a local check guarantees safety.

## Side effects

| Action | Review focus | Prerequisites and stopping conditions |
|---|---|---|
| Targeted status reads | Customer data, scale, resource load | Limit targets and fields; stop expanding collection if resources degrade |
| Full diagnostics, debug, capture | CPU/memory/storage, continuous logs, sensitive payloads | Platform-specific scope, filters, duration and disable method; no universal threshold |
| Clear counters/logs | Lost evidence and changed measurement baseline | Preserve values, time and purpose; separate sampling windows |
| Interface/VLAN/route/AAA/ACL changes | Sessions, management access, return paths and other services | Current state, dependencies and independent recovery; stop on drift |
| Export/save logs or diagnostic files | Local storage writes, evidence contents and storage pressure | Separate status reads from file writes; confirm destination/capacity and cleanup ownership |
| Failover test by disabling links or members | Reduced redundancy, interrupted flows and management loss | Explicit test scope, available alternate path, restoration steps and service-based stop conditions; never imply a status read |
| Save configuration | Next-boot state and persistence of unaccepted changes | Separate running acceptance from save approval; bind separate approval to plan and targets |
| Reboot, upgrade, IRF merge or isolation recovery | Forwarding, active/standby/member state, rollback limits | Matching docs, maintenance window, responsible operator and recovery evidence |

Order actions around evidence preservation and management access. Distinguish temporary recovery, permanent repair and unresolved root cause; record incidents truthfully even when the planned sequence was interrupted.

## Management security baseline

Review supplied material as observation -> applicability -> impact -> recommendation -> verification. A missing line alone is not proof of a vulnerability.

- Access: protocols, listening/access scope, management VRF/ACL and actual reachability. Verify exposure and dependencies before judging plaintext protocols.
- Authentication: AAA path, roles, fallback access and failures. Do not automatically remove backup accounts or reset authentication.
- Secrets: handle passwords, communities, keys and certificates only within authorized local scope. Encryption does not imply public safety.
- Logging: time zones, completeness, remote logs and retention. No logged event does not prove no event occurred.
- Maintenance: exact model/Release/patch and official advisory conditions. An unsuccessful search proves neither safety nor impact.
- Recovery: usable running/startup configurations, compatible backups and independent access. Backup existence is not a recovery test.

## Upgrade path review

Use the [upgrade template](../assets/templates/upgrade-review.md). Verify current-to-target software/patch compatibility, hardware/BootROM/storage/license prerequisites, method, service impact and recovery limits against the target release notes and upgrade guide. Establish why an upgrade is needed before selecting a version.

Check the ISSU version matrix and exact method. Product-level ISSU support does not prove hitless upgrades for arbitrary version pairs. The indexed S6800/S6860 R671x example documents restrictions on aborting a one-step upgrade; verify the applicable method rather than promising generic rollback.

The plugin prepares reviews; it does not download images, authenticate binaries or execute upgrades. Image checks/signatures, restore tests, failover and business acceptance require actual tool/device evidence. State any missing evidence.

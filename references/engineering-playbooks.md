# H3C engineering troubleshooting playbooks

Read only the relevant topic. These are investigation paths, not cross-platform command certification. Confirm platform/Release, then verify syntax, command view and effects in the matching manual. Use the [source index](engineering-sources.md) for navigation.

## First response

Use the [action-card guidance](engineer-audiences.md) when an operator needs to run the next check. For patch follow-up or closure, apply [service acceptance](service-acceptance.md).

Reuse raw output and [local profiling](local-tools.md). State the current assessment and evidence, then the most discriminating checks and expected branches. Usually start with one to three checks; expand for sufficient evidence or an explicitly requested full plan. Avoid repeated questions and indiscriminate diagnostic collection.

Separate observations, hypotheses, gaps and verified results. Missing timestamps, full output, peer data or models constrain only the affected conclusions. Continue independent work. Recovery does not establish root cause.

## Interfaces, optics, CRC and packet loss

- Minimum evidence: affected interface and peer, sample times, link state, counters and reset/reboot history; module/fiber details when needed.
- Compare physical/protocol state and error increments at both ends. Do not calculate deltas across resets, reversed time or unknown counter-width boundaries. Separate CRC errors, congestion discards and policy drops.
- For physical abnormalities, inspect fiber/connectors, optical power, module alarms and compatibility. With stable physical state, check queues, policing and paths. CRC alone does not prove a failed optic; thresholds differ by module.
- Do not clear counters merely for clean data. If needed, preserve values/time and record side effects first. Replacing optics or breaking links needs applicable authorization.
- Acceptance: comparable repeated samples and actual business traffic, with a justified observation window and remaining uncertainty.

## VLAN, trunk/PVID and link aggregation

- Collect both endpoint configurations, service VLANs, physical connections and operational aggregation/member state. The indexed S9820-8C R6715 reference is navigation, not portable syntax.
- Check allowed VLANs/PVIDs and the tagging path, then Selected/Unselected/Individual states and reasons. Physical UP, configured membership or port count does not prove forwarding participation.
- Investigate key, mode, speed and attribute mismatches against applicable restrictions. Do not default to disabling consistency checks or forcing static aggregation.
- Separate single-flow from multiflow capacity; summed member rates do not guarantee one flow can use that rate. Verify reverse traffic too.
- Acceptance: the intended business path and both endpoint states, without disrupting other VLANs or management.

## IRF/MAD and dual-device redundancy

- Collect platform/Release, members/roles, IRF links and physical paths, MAD mechanism, event times and changes.
- Check membership completeness and degraded interconnects. With split indications, establish actual forwarding and MAD state before restoring an isolated side.
- Verify MAD combinations, domain IDs, detection ports and intermediate-device conditions in the matching manual. Two links/devices do not alone eliminate a single point of failure.
- Preserve incident evidence. Merge, role change and isolated-interface recovery are not harmless reads.
- Acceptance: expected members/roles, detection and business paths. Failure availability requires appropriate lab or site evidence.

## STP, loops and MAC movement

- Collect affected VLANs/instances, physical/logical links, port roles, event logs and traffic timeline.
- Correlate changes with the incident window, then compare root/port state and MAC learning. MAC movement alone is not a loop; rule out migration and normal redundancy transitions.
- Limit collection under broadcast/resource pressure and narrow the fault domain. Do not default to disabling STP, loop prevention or port protections.
- Acceptance: stable topology, restored business and normal traffic. Record isolation and restoration separately.

## Gateway, ARP, DHCP and routing

- Define one business flow: source/destination/protocol, VLAN/VRF, address acquisition, path and time.
- Isolate link, Layer 2, addressing/allocation, gateway neighbors, routing and policy. A route entry does not prove next-hop or return-path reachability.
- Follow DHCP discovery/relay/server/reply branches. Avoid simultaneous pool, relay and switch edits that obscure causality.
- Acceptance: complete endpoint business flow, both directions and lease/adjacency state. One ping is insufficient for all services.

## Management loss and high CPU

- Distinguish management-only impact from forwarding failure; preserve independent access.
- Map management VLAN/VRF, routes, AAA, ACL and protocols. Before edits, assess whether the current session will be cut off and how to recover.
- Use bounded sampling appropriate to platform resources. Verify prerequisites before full diagnostics. Define capture/debug filters, duration, stop and cleanup steps; avoid universal thresholds.
- Do not reboot instead of gathering evidence or promise zero interruption. Separate recovery from root-cause investigation.

## WLAN: AP onboarding and client service

- Distinguish AP offline, client authentication failure and connected-client service failure. Record AC/AP models/Releases, power/link, management addressing and failing stage.
- For onboarding, check access network/addressing, discovery/control channel and explicit AC failure reason before license, compatibility and image requirements. Offline status alone does not justify reconfiguration or upgrade.
- For clients, inspect association, authentication, addressing and forwarding separately. Separate RF from wired-path evidence. The indexed WX3800X R1411P02 reference is only navigation for AP failure records.
- Do not default to resetting APs or global WLAN configuration. Acceptance concerns affected users and applications, not AP state alone.

## Firewall: policy, sessions and NAT

- Collect one redacted flow, direction/zones/VRF, time, routes and relevant NAT/policy/session evidence.
- Establish packet arrival, then inspect routing, zone/policy match, translation, session and return path. Permit/hit status is not end-to-end success.
- Missing logs may reflect disabled logging; enabling logs can add load. WebHelp provides concepts; actual order and commands depend on product/Release.
- Do not default to allow-all rules or clearing every session. Even a single-flow experiment needs impact and authorization checks.
- Acceptance: application exchange, return path and expected matches. Resolving one incident is not a complete security-policy audit.

## Stop and escalate

For core splits, lost management paths, unavailable recovery or unexplained version behavior, retain facts and the action timeline, then propose the least-risk next step or TAC handoff. Do not invent root cause, vendor guarantees or entitlements.

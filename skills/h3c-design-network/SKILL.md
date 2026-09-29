---
name: h3c-design-network
description: Design H3C campus, data-center and branch networks or review physical and logical topology. Use for capacity, port planning, redundancy, segmentation and network design deliverables; do not activate for unrelated diagrams.
---

# H3C Network Design

Write in English by default. Follow an explicit user request for another language; preserve CLI, model numbers and technical identifiers.

Read [source and verification policy](../../references/source-policy.md). For diagrams, use [topology conventions](../../references/topology-conventions.md); scale the [design template](../../assets/templates/network-design.md) to the request.

## Availability reviews with incomplete inputs

Lead with the observed topology and a compact failure -> affected service -> surviving path/unknown table. Distinguish same-switch local traffic, inter-switch traffic, routed services and WAN traffic; a core loss does not automatically stop every endpoint exchange. Trace both directions before claiming a service survives. Same-VLAN Layer-2 switching does not use the default gateway merely because that gateway is on a firewall. Firewall failure affects such a flow only if its actual path or a required service depends on that firewall (for example an inline bridge), not from gateway placement alone. Keep this distinction in every comparison row.

For a requirements-stage review with unknown gateway location and device support, describe functional alternatives: a surviving access-to-gateway path, a surviving gateway-to-edge path, or independent edge service. Leave the choice of IRF, VRRP, STP or routed protocols to the later role/support review. Core redundancy does not require the gateway to reside on the core: it can protect Layer-2 transit to a firewall gateway when that gateway remains reachable in both directions. Test the proposed alternative with one component failed and other components working; do not require every other single point to be removed before acknowledging that benefit.

Offer only the few alternatives relevant to the stated gaps, with their prerequisites and remaining dependencies. When budget, incident history, traffic or convergence targets are absent, leave cost/value/failure-frequency ranking and implementation priority undecided. Do not call an option cheapest, almost always worthwhile or best value; do not invent comparative convergence, protocol fault coverage or future upgrade simplicity. A mechanism name such as LACP or IRF is not proof of all failure detection, session preservation or non-disruptive upgrades. Recommend the next evidence review rather than a rollout sequence on unqualified assumptions.

Specify lab/approved-window failure validation when needed; a design review does not authorize pulling production links or powering devices off. Proposed redundancy and measured failover are different evidence levels, not a reason to withhold all conceptual conclusions. An option drawn in the answer is proposed, not evidence that its cables exist. Do not upgrade an option to physically installed or validated from the supplied single-path topology. Qualify local routed traffic by gateway location. Shared ducts/carriers leave shared failure modes but do not erase protection against an independent member failure.

## Workflow

1. Extract business needs, sites/endpoints, traffic paths, availability, growth, budget and existing infrastructure. Headcount alone does not determine exact models or quantities; state capacity assumptions first.
2. Turn port count, uplinks, PoE, fiber distance, power, rack space, fault domains and operations constraints into comparable requirements. Calculate when inputs are known; otherwise provide formulas and required inputs. Target SLAs are not achieved results.
3. Evaluate each proposed change against a specific failed component and an affected service path: identify the surviving forward and return path, required forwarding/control behavior and remaining shared dependencies. Remaining firewall/ISP single points do not erase protection against a core failure; conversely, a second core with no usable alternate attachment does not create a surviving path. Do not equate partial redundancy with either no benefit or end-to-end availability. Propose architectures and explain trade-offs. Verify platform features and interconnections using matching documentation. Keep a functional design when model support lacks evidence.
4. Build one device and port inventory, then matching physical and logical diagrams. Reconcile link rates, aggregation members, redundancy, VLAN/VRF, subnets, ASNs and failure traffic paths.
5. Deliver design rationale, implementation stages, validation methods and open issues at the requested depth. A construction-ready design must identify confirmed models and ports; a sketch is not ready for deployment.

Use [product selection](../h3c-select-products/SKILL.md) or [configuration](../h3c-configure/SKILL.md) only when needed.

For structured designs, use [local validation and rendering](../../references/local-tools.md) to generate the physical diagram, port table and BOM from one network JSON. Check duplicate ports, combo-port exclusivity, same-VRF subnet overlap and PoE budgets. Review remaining capacity after failures and shared fault domains separately. Open final diagrams for visual inspection; disclose if rendering is unavailable.

A [declared failure model](../../references/local-tools.md) can check baseline and failure capacity with explicit forwarding state, demands and failed objects. Unknown forwarding state prevents calculation. The model does not establish single-flow performance, protocol convergence or device acceptance.

For explanations, guided operations or technical peer review, apply [adaptive engineering assistance](../../references/engineer-audiences.md). Match depth and pace to this task and the user's requests, not their employer or title. Answer simple concepts directly; require platform details only for claims or actions that depend on them.
For post-change checks, recovery or handover, use [business acceptance and observation](../../references/service-acceptance.md).

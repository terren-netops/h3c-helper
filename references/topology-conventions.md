# Consistent topology deliverables

Identify whether the deliverable is a requirements sketch, logical design or deployment-ready physical design. With incomplete requirements, provide a sketch without invented ports, optics or models.

- Physical views: unique device IDs, known ports, per-link rates, media, distance, modules and power constraints. Keep aggregate bandwidth separate from member-link speed.
- Logical views: VLANs, subnets, VRFs, adjacencies, routing areas/ASNs, overlays and security boundaries. Reuse physical device IDs.
- Treat the port table as the common source for diagrams and configuration. Check conflicting port use, matching endpoint speeds/media and explicit aggregation membership.
- Visually distinguish confirmed connections, proposed design and unresolved evidence, with a next verification step for gaps.
- Select IRF, VRRP, LAG or multichassis aggregation based on platform support and failure domains, not inherited templates.
- Use ASCII or Mermaid for simple diagrams and a port table for complex ones. Keep ASCII readable without dropping deployment-critical information.
- Use interface names from the actual output/manual. Diagram abbreviations are not CLI syntax. Verify model, interface speed and transceiver separately.

Reconcile: device table -> port table -> physical diagram -> address/VLAN/VRF table -> logical diagram -> configuration -> validation steps. Generated images do not validate connectivity.

## Failure-path review

For each relevant failure, trace endpoint -> access -> gateway/core -> destination and return, including power and control dependencies. State what remains reachable, what fails and what is unknown. A remaining ISP or firewall single point limits protection against that component's failure; it does not negate a core-failure mitigation when a usable alternate path to the same working edge exists. A second core without that path does not establish WAN resilience.

Make LAG, dual-homing, gateway redundancy and routing alternatives conditional on requirements, compatible endpoints, actual forwarding design and operational cost. Multiple cables to one chassis do not protect against loss of that chassis. A loop-free drawing does not establish that STP or edge loop protection is unnecessary: accidental cabling, downstream bridges and operational changes also matter. Exact protections and convergence require platform-specific validation.

Conceptual reference: [Cisco Enterprise Campus Architecture, Core and Resiliency sections](https://www.cisco.com/c/en/us/td/docs/solutions/Enterprise/Campus/campover.html), reviewed 2026-09-28. Used only for general path/failure-domain reasoning; this is not evidence of H3C feature compatibility or convergence performance.

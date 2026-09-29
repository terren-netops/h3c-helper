# Shared case facts for handoff

Maintain one fact table and select fields by audience. Do not simply shorten raw engineer logs for a customer.

| Fact ID | Observation/hypothesis/action/next step/limitation | Text | Source/timeline reference | Visible to | Redaction reviewed |
|---|---|---|---|---|---|

Engineer: preserve investigation branches and internal evidence references. TAC: authorized reproduction, impact, version and completed-action evidence. Customer engineer: authorized technical facts, operating steps, interpretation, stop conditions and evidence to return. Customer manager: conclusions, impact, status and next steps without unnecessary internal identifiers. Both use customer visibility; tailor fact text to the recipient. Use English unless the user explicitly requests another language.

Use the [handoff schema](../../schemas/handoff.schema.json) for machine input. The generator requires explicit visibility and per-fact redaction review for non-engineer audiences. Keyword checks are supplemental, not proof of safe disclosure. Set redaction_reviewed=true only after actual review.

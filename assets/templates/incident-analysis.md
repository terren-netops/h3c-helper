# Incident and performance analysis

## Facts
Symptoms, impact, time/time zone, frequency, normal baseline, platform and recent changes; link log/configuration locations.

## Collection plan and evidence index, when needed
Follow [production evidence collection](../../references/evidence-and-continuity.md#collect-production-incident-evidence). Record target/neighbor scope, purpose, verified command or collection objective, expected burden, sampling interval/duration, stop/disable conditions and applicable authorization. Reuse existing evidence before collecting again.

| Evidence file/source | Device/site and interface/flow | Device time/zone and collector start/end | Clock synchronization/skew | Sample/window and baseline applicability | Supplied/executed status, gaps/truncation and raw/redacted status |
|---|---|---|---|---|---|

Use site naming rules or safe device/address/time/artifact filenames with unique sample identifiers. Keep permitted raw evidence and redacted derivatives distinct. Missing supplied output does not establish that collection was never performed.

## Hypotheses and discriminating checks
| Hypothesis | Supporting evidence | Counterevidence/gaps | Next check and location | How results change the assessment |
|---|---|---|---|---|

## Recovery and repair
Immediate recovery, permanent repair, impact and stop/rollback conditions. Specify sampling scope and duration for resource-intensive diagnostics.

## Validation and conclusions
Business recovery, protocol/resource state, observation window and recurrence. Keep unverified root cause as a hypothesis. Use comparable before/after measurements for improvement claims; no percentages without data.

## Measurement and closure evidence
Counter width/resets/reboots, clock alignment and denominators. Separate observations, hypotheses and confirmed conclusions. Include business checks, rationale for the observation window, recurrence and remaining root-cause uncertainty.

## Operator next step and handover, when needed
For each requested check, state target/location, purpose, verified action, output fields, result branches, operational burden and evidence to return. Reuse the hypothesis table rather than duplicating it. Track recovery, root-cause confidence, observation and acceptance separately; identify the next owner and escalation trigger. See [service acceptance](../../references/service-acceptance.md).

## Continuation checkpoint, when needed
Reuse the facts and hypothesis sections above. Note corrected or conflicting sources, scope of excluded hypotheses, actions actually completed, temporary changes and uncertain persistence, and the next check/owner. See [evidence and continuity](../../references/evidence-and-continuity.md). Keep a checkpoint brief; do not create a second case history.

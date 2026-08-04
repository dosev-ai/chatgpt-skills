# Public Modes and Standalone Example

## Mode selection

Evaluate proposal eligibility first. Connected-system availability never overrides missing product authority or minimum product evidence.

| Condition | Mode | Required result |
| --- | --- | --- |
| Authority, approval basis, or minimum product evidence is insufficient | `standalone-proposal` | `PRD_DRAFT`, missing-decision register, assumptions, evidence gaps, and next approval action |
| Sufficient evidence and explicit product authority exist; no connected write is required | `standalone` | Complete versioned PRD artifact with explicit approval basis, limitations, and persistence status |
| Sufficient authority and evidence exist and relevant connected systems are available and authorized | `connected-governance` | Complete PRD plus verified source references; storage reference only after a successful authorized write |

A standalone artifact must include document control, authority and approval records, source-faithful evidence, goals and exclusions, stable requirements, metrics, journeys, risks, review findings, ADR candidates, change control, artifact identity, persistence status, and evidence limitations.

Use `persisted` only after a verified authorized write; `not persisted` when no write was attempted or required; `blocked` when approval, permission, duplicate, policy, or write-scope controls prevented the write; and `write failed` when an authorized write attempt did not complete. Never invent a document ID.

## Worked example: meeting follow-up tool

### Input evidence

The requester states that meeting notes are inconsistent, commitments are often missed, manual follow-up causes delay and transcription risk, and human confirmation is required before task creation. Decisions, owners, and deadlines are extraction targets, not separately verified failure facts.

### Candidate product outcome

Turn supported meeting notes into a reviewable follow-up record containing candidate decisions and actions. Keep ambiguous owners and deadlines unresolved. Create or export only items explicitly confirmed by an authorized reviewer.

### Hunter findings

- Add ambiguous-owner and relative-deadline journeys.
- Add explicit no-action review.
- Add export and failure recovery.
- Add retention, accessibility, privacy, idempotency, and measurable quality controls.

### Skeptic findings

- The improvement outcome lacks a baseline and decision window.
- Incorrect no-action results could inflate completion.
- Batch confirmation and retry boundaries are unclear.
- Retention and identity resolution remain undecided.
- The integration mechanism belongs in architecture analysis.

### Repaired controls

- Measure a two-week baseline and target a 30% relative reduction in confirmed actions left unacknowledged after three business days during the following six weeks.
- Require at least 95% of human-reviewed supported notes containing one or more confirmed commitments not to be incorrectly classified as no-action before reviewer correction.
- Return a review result or explicit failure within 60 seconds for at least 95% of supported pilot inputs up to 10,000 words.
- Require explicit confirmation of each task or enumerated batch.
- Use an idempotency key so retries cannot create duplicates.
- Preserve source notes, generated candidates, human edits, confirmation evidence, and task outcomes as distinguishable records.

### Representative requirement set

- `BR-001` Return a reviewable record, reviewer-confirmed no-action result, or explicit failure for every accepted supported input.
- `FR-001` Extract candidate decisions, actions, proposed owners, and proposed deadlines.
- `FR-002` Keep ambiguous values unresolved until human confirmation.
- `FR-003` Allow edit, reject, merge, split, and add operations before confirmation.
- `FR-004` Require explicit confirmation before task creation.
- `NFR-001` Preserve source text separately from generated and human-edited content.
- `NFR-002` Meet the approved response-time boundary.
- `NFR-003` Meet the approved no-action sensitivity threshold.
- `SEC-001` Use only approved destinations for the applicable information classification.
- `OPS-001` Make task-creation retries idempotent and report partial or unknown outcomes.
- `DATA-001` Record source expressions and confirmed normalized owner/deadline values separately.

### ADR candidates

1. Task-system integration, authorization, idempotency, reconciliation, and rollback.
2. Extraction and confidence approach under quality, privacy, latency, explainability, and cost constraints.
3. Retention and deletion of source, review, confirmation, and outcome data.
4. Participant identity resolution without silent assignment.

### Final example status

The repaired example may become `PRD_APPROVED` only after an authorized product owner explicitly approves the repaired metrics, requirements, constraints, and ADR candidates. In a conversation-only demonstration its artifact identity is `approved PRD artifact` and its persistence state is `not persisted`. Architecture analysis is the next gate; executable implementation remains separately governed.

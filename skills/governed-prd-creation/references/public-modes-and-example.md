# Public Modes and Standalone Example

## Mode selection

Choose the smallest valid mode. Evaluate proposal eligibility first: connected-system availability never overrides missing product authority or minimum product evidence.

| Condition | Mode | Required result |
| --- | --- | --- |
| Authority or minimum product evidence is insufficient, including when connected systems exist or are relevant | `standalone-proposal` | Operating mode `standalone-proposal`, lifecycle state `PRD_DRAFT`, missing-decision register, and next approval action |
| User supplies sufficient evidence, states the product-owner decision right, and no connected system is needed | `standalone` | Complete versioned PRD artifact with explicit approval basis and limitations |
| Sufficient product authority and minimum product evidence are established, and project, document, repository, or delivery systems are connected and relevant | `connected-governance` | Complete PRD plus verified authority and traceability, an explicit persistence status, and a storage reference only after a successful authorized write |

Do not require a connector merely because one is mentioned in an example. Do not use connected state unless it has been read in the current session.

## Standalone artifact contract

A standalone PRD must contain:

- PRD ID, title, version, date, lifecycle state, and operating mode;
- product owner or decision-authority basis;
- problem, target users, evidence, goals, non-goals, and exclusions;
- stable requirement catalogue;
- measurable success metrics;
- user, negative, recovery, and operational journeys;
- fixed constraints, assumptions, dependencies, and risks;
- Hunter-Skeptic-Referee review record;
- stakeholder and product-owner approval record;
- ADR candidate register;
- change-control and traceability rules;
- persistence status and evidence limitations.

Use `persisted` only after a verified authorized write. Use `not persisted` when no write was attempted or required. Use `blocked` when approval, permission, duplicate, policy, or write-scope controls prevented the write. Use `write failed` when an authorized write attempt did not complete. Never invent a document ID.

## Connected governance contract

Connected mode may add:

- approved project facts and governing action IDs;
- existing PRD and decision references;
- connected document-store ID and version;
- repository ADR references;
- delivery actions and test evidence;
- exact source statuses and timestamps.

Keep connected-system facts separate from assessment. Missing or inaccessible state is `Unknown`.

# Worked example: Meeting Follow-up Tool

## Example input

> I am the product owner for this example and authorize product-requirement decisions. Our meeting notes are inconsistent, commitments are often missed, and manual follow-up causes delay and transcription risk. Create a PRD for a meeting follow-up tool that extracts decisions, owners, and deadlines from meeting notes. It must require human confirmation before creating tasks.

Authority for the demonstration is explicit in the input. The authority statement permits the requester to review and approve product decisions; it does not itself approve requirements or metrics that have not yet been presented. The current-state discovery claims are also supplied explicitly rather than inferred. No external project system, document store, or repository is connected.

## Initial draft summary

**Problem:** Meeting notes are inconsistent, commitments are often missed, and manual follow-up causes delay and transcription risk.

**Target users:** Meeting organizers, participants, and team leads.

**Outcome:** Convert meeting notes into a reviewable list of proposed decisions and actions, then create tasks only after explicit human confirmation.

**E2E goal:** A user provides meeting notes, reviews extracted items, corrects or rejects them, confirms selected actions, and receives a final export or task-creation result with an audit record.

## Candidate requirements

- `BR-001` Reduce missed meeting commitments by providing one reviewable follow-up record per processed meeting.
- `FR-001` Accept pasted meeting notes or an uploaded supported text document.
- `FR-002` Extract candidate decisions, action descriptions, owners, and deadlines with confidence or uncertainty indicators.
- `FR-003` Allow the user to edit, reject, merge, or add extracted items before confirmation.
- `FR-004` Require explicit human confirmation for each task or approved batch before any task-creation action.
- `FR-005` Produce a final summary that distinguishes confirmed tasks, rejected candidates, unresolved items, and decisions.
- `NFR-001` Preserve the original notes and the reviewed output without silently altering source text.
- `SEC-001` Do not expose meeting content to an unapproved destination.
- `OPS-001` When task creation fails, retain the confirmed payload and provide a safe retry or export path.

## Hunter findings

- Add a participant-resolution rule for ambiguous names.
- Add a journey for meetings with no actionable items.
- Add a rule for missing or relative deadlines.
- Add accessibility and export requirements.
- Clarify whether task-system integration is required or optional.

## Skeptic findings

- `P1`: “Reduce missed commitments” has no baseline, target, or measurement window.
- `P1`: Owner resolution may create tasks for the wrong person.
- `P1`: The confirmation boundary is unclear for batch approval and retries.
- `P1`: The completion metric can be inflated by incorrectly returning no-action for notes that contain commitments.
- `P2`: The source-retention and deletion policy is undefined.
- `P2`: Task-system integration is an architecture question, not a product requirement.
- `P2`: The review-result performance requirement has no measurable threshold.

## Repair cycle

Repair the draft by:

1. defining a two-week pilot baseline and a 30% relative reduction target measured during the following six weeks;
2. requiring unresolved owners to remain unassigned until confirmed;
3. recording an immutable confirmation summary before task creation;
4. defining retry behavior that cannot create duplicate tasks;
5. adding retention and deletion requirements;
6. adding no-action, ambiguous-deadline, accessibility, export, and recovery journeys;
7. moving the task-system integration method into the ADR candidate register;
8. defining a pilot response-time threshold for supported inputs;
9. requiring at least 95% sensitivity against incorrect no-action classification in a human-reviewed pilot sample of supported notes containing one or more confirmed commitments.

At this point the repaired contract is review-ready but not yet approved. Present it to the product owner as a separate decision.

## Product-owner decision after repair

> I approve the repaired version 1.0.0 demonstration PRD, including the two-week baseline and 30% improvement target, the requirement to return a review result or explicit failure within 60 seconds for at least 95% of supported pilot inputs up to 10,000 words, the requirement that at least 95% of human-reviewed supported notes containing one or more confirmed commitments are not incorrectly classified as no-action, the human-confirmation boundary, owner and deadline resolution rules, idempotent retry requirements, retention requirements, and the four ADR candidates.

This explicit follow-up decision approves the repaired product contract. The earlier authority statement alone would not have been sufficient approval.

## Referee verdict

`APPROVED_WITH_CONSTRAINTS` because:

- the authorized product owner separately reviewed and accepted the repaired requirements, pilot metric, measurement method, response-time threshold, and no-action sensitivity threshold;
- confirmation, duplicate prevention, owner resolution, retention, extraction-quality, and performance requirements are testable;
- task-system integration remains an architecture decision;
- no absent stakeholder approval is implied;
- pilot assumptions and architecture decisions remain visible constraints.

# Final repaired PRD artifact

## Document control

| Field | Value |
| --- | --- |
| PRD ID | `PRD-MFT-001` |
| Title | Meeting Follow-up Tool |
| Version | `1.0.0` |
| Date | 2026-08-02 |
| Operating mode | `standalone` |
| Lifecycle state | `PRD_APPROVED` |
| Product owner | Requesting user, based on the explicit authority statement and separate post-repair approval decision |
| Stakeholder approval | No additional mandatory stakeholder approver identified for this neutral example; no absent approval is implied |
| Trio verdict | `APPROVED_WITH_CONSTRAINTS` |
| Persistence | `not persisted` |
| Prior version | None |

## 1. Executive intent

### Problem

Meeting notes are inconsistent, commitments are often missed, and manual follow-up causes delay and transcription risk.

### Target users

- meeting organizers who prepare and distribute follow-up records;
- participants who must verify decisions and commitments;
- team leads who need a reliable view of confirmed actions and unresolved items.

### Product outcome

Transform meeting notes into a reviewable follow-up record containing candidate decisions and actions, while preventing any task creation until an authorized user explicitly confirms the intended tasks.

### Product E2E goal

A user submits meeting notes, reviews extracted decisions and actions, resolves uncertainty, edits or rejects candidates, confirms selected tasks, and receives a final audit summary plus either a safe export or verified task-creation result.

## 2. Evidence and current state

### Evidence supplied

- meeting notes are inconsistent;
- commitments are often missed;
- manual follow-up creates delay and transcription risk;
- human confirmation before task creation is a binding product constraint.

### Evidence limitations

- the input does not establish which commitment elements are most often missed; decisions, owners, and deadlines are extraction targets rather than separately evidenced failure rates;
- this is a neutral demonstration, not production discovery;
- no organizational baseline, task-system capability, privacy classification, volume profile, or user-research sample was supplied;
- pilot measurements and architecture validation are required before a production commitment.

## 3. Goals, non-goals, and exclusions

### Goals

- produce one reviewable follow-up record from each supported meeting-note input;
- reduce overdue unacknowledged meeting actions relative to a measured pilot baseline;
- make uncertainty visible before confirmation;
- prevent unconfirmed or duplicate task creation;
- preserve a human-readable audit summary of what was confirmed, rejected, or left unresolved.

### Non-goals

- automatically record or transcribe meetings;
- infer organizational authority from names or job titles;
- create tasks without explicit human confirmation;
- select the task-management platform or integration architecture inside the PRD;
- replace formal minutes, legal records, or regulated record-management systems.

### Exclusions for version 1.0

- audio and video ingestion;
- multilingual extraction beyond explicitly supported languages;
- automatic participant-directory synchronization;
- autonomous deadline negotiation or reassignment;
- analytics beyond pilot success metrics and basic processing evidence.

## 4. Requirement catalogue

### Business requirements

- `BR-001` The product must return either a reviewable follow-up record, an explicit no-action result, or an explicit processing failure for every accepted supported meeting-note input.
- `BR-002` During the six-week measurement period after a two-week baseline, the pilot must reduce the rate of confirmed actions that remain unacknowledged after three business days by at least 30% relative to baseline.
- `BR-003` The product must preserve human control over which extracted actions become tasks.

### Functional requirements

- `FR-001` Accept pasted text and explicitly supported text-document formats.
- `FR-002` Extract candidate decisions, action descriptions, proposed owners, and proposed deadlines.
- `FR-003` Mark missing, conflicting, relative, or low-confidence values as unresolved rather than silently completing them.
- `FR-004` Keep an owner unassigned when identity is ambiguous until a human selects or enters the owner.
- `FR-005` Allow an authorized reviewer to edit, reject, merge, split, or add candidate decisions and actions.
- `FR-006` Require explicit confirmation for each task or a clearly enumerated batch before task creation.
- `FR-007` Display the exact confirmed payload and destination before the user authorizes task creation.
- `FR-008` Record a confirmation summary containing confirmed items, rejected candidates, unresolved items, decisions, reviewer identity or session attribution, and confirmation time.
- `FR-009` Produce a no-action outcome only when the reviewer confirms that the notes contain no actionable commitment.
- `FR-010` Provide a downloadable or copyable export when direct task creation is unavailable or not selected.

### Non-functional requirements

- `NFR-001` Preserve the source notes unchanged and distinguish source text from generated candidates and human edits.
- `NFR-002` Present all review and confirmation controls in a keyboard-operable, screen-reader-compatible flow.
- `NFR-003` For supported pilot inputs up to 10,000 words, return a review result or an explicit processing failure within 60 seconds for at least 95% of requests, measured from accepted submission to result availability.
- `NFR-004` Never represent an inferred owner, deadline, or decision as confirmed before human approval.
- `NFR-005` In a human-reviewed pilot sample of supported notes containing one or more confirmed commitments, at least 95% must not be incorrectly classified as no-action before reviewer correction.

### Security, privacy, and compliance requirements

- `SEC-001` Send meeting content only to destinations approved for the applicable information classification.
- `SEC-002` Apply configurable retention and deletion rules to source notes, generated candidates, confirmation evidence, and exports.
- `SEC-003` Restrict task-creation authorization to users permitted to create tasks in the selected destination.
- `SEC-004` Avoid exposing meeting content, participant names, or task details in logs beyond the approved diagnostic policy.

### Operational requirements

- `OPS-001` Assign a stable idempotency key to each confirmed task-creation request.
- `OPS-002` A retry must not create a duplicate task when the destination already accepted the same confirmed request.
- `OPS-003` When task creation fails, retain the confirmed payload and provide a safe retry or export path without requiring the user to repeat review.
- `OPS-004` Surface partial success by identifying which confirmed tasks were created, failed, or remain unknown.
- `OPS-005` Provide a support-visible correlation reference that does not disclose meeting content.

### Data requirements

- `DATA-001` Keep source notes, generated candidates, human edits, confirmation evidence, and task-creation outcomes logically distinguishable.
- `DATA-002` Record deadline values with the source expression, normalized value when confirmed, and timezone or date interpretation used.
- `DATA-003` Record owner resolution as unresolved, manually entered, or selected from an approved identity source.

## 5. Success metrics and acceptance

| Metric | Baseline | Target | Method | Decision window |
| --- | --- | --- | --- | --- |
| Confirmed actions unacknowledged after three business days | Measure during pilot weeks 1–2 | At least 30% relative reduction | Compare equivalent meetings and action populations during weeks 3–8 | End of week 8 |
| Unconfirmed tasks created | Zero tolerated | 0 | Audit confirmation evidence against task-creation outcomes | Continuous |
| Duplicate tasks caused by retry | Zero tolerated | 0 | Match idempotency keys and destination results | Continuous |
| Supported inputs returning a review result or explicit failure within 60 seconds | Establish during pilot instrumentation | At least 95% for inputs up to 10,000 words | Measure accepted submission to result availability | Weekly and end of week 8 |
| Human-reviewed supported notes with confirmed commitments not incorrectly classified as no-action | Establish in weeks 1–2 | At least 95% sensitivity | Use a stratified human-reviewed sample; denominator is notes containing one or more confirmed commitments, numerator is those not initially classified as no-action | Weekly and end of week 8 |
| Extracted items requiring correction | Establish in weeks 1–2 | Product owner sets production threshold after pilot | Compare generated candidates with final confirmed record | End of week 8 |
| Accepted supported inputs producing a final follow-up record or explicit no-action result | Establish in weeks 1–2 | At least 95% of all accepted supported inputs | Count final follow-up and reviewer-confirmed no-action outcomes over all accepted supported inputs; processing failures remain in the denominator | Weekly and end of week 8 |

Product acceptance requires:

- every task outcome traces to an explicit confirmation event;
- unresolved owners and deadlines remain visibly unresolved until corrected;
- retries are idempotent;
- no-action outcomes require reviewer confirmation and do not conceal commitments in more than 5% of the human-reviewed supported sample containing confirmed commitments;
- source notes and human-approved output remain distinguishable;
- export and failure recovery work without loss of the confirmed payload;
- at least 95% of all accepted supported inputs produce a final follow-up record or reviewer-confirmed no-action result;
- the approved response-time and no-action sensitivity thresholds are met for the supported pilot boundary;
- accessibility checks cover the complete review and confirmation journey.

## 6. User and operational journeys

### Primary journey

1. Organizer submits supported meeting notes.
2. Product extracts candidate decisions and actions.
3. Product highlights uncertainty and missing fields.
4. Reviewer edits, rejects, or adds items.
5. Reviewer sees the exact task payload and destination.
6. Reviewer confirms individual tasks or an enumerated batch.
7. Product exports or creates tasks and returns an audit summary.

### Ambiguous owner journey

The product leaves the owner unresolved, prevents silent assignment, and requires human selection or entry before task confirmation.

### Relative or missing deadline journey

The product preserves the source wording, proposes an interpretation only when allowed, and requires explicit confirmation of the normalized date and timezone.

### No-action journey

When the product proposes no-action, the reviewer confirms the absence of actionable commitments or adds any missed item. Incorrect no-action proposals count against the approved no-action sensitivity metric.

### Failure and recovery journey

The product preserves the confirmed payload, shows per-item status, uses the same idempotency key for a safe retry, and offers export when the destination remains unavailable.

### Accessibility journey

A keyboard and screen-reader user can submit notes, inspect confidence and unresolved states, edit items, review the exact payload, confirm, and obtain the final result.

## 7. Fixed constraints and assumptions

### Fixed constraints

- human confirmation is mandatory before task creation and before a final no-action outcome;
- source notes must not be silently altered;
- public or connected implementations must respect destination and information-classification permissions;
- architecture must support idempotent retries and auditable confirmation;
- the pilot must meet the approved response-time and no-action sensitivity thresholds for the defined supported-input boundary.

### Assumptions requiring validation

- users can identify an authorized reviewer for each meeting;
- supported meeting notes contain enough context to identify candidate actions;
- the selected task destination can expose a stable success result or equivalent reconciliation mechanism;
- pilot volume and sampling are sufficient to calculate the defined metrics.

## 8. Dependencies and risks

### Dependencies

- approved privacy and retention policy;
- supported input-format definition;
- identity-resolution approach;
- task-destination integration decision;
- pilot cohort, stratified quality sample, and baseline-measurement plan;
- accessibility and security review.

### Risks and controls

- **Wrong owner:** keep ambiguous owners unresolved and require confirmation.
- **Wrong deadline:** preserve source wording and require normalized-date confirmation.
- **Missed commitment through false no-action:** require reviewer confirmation and measure sensitivity on a human-reviewed sample containing confirmed commitments.
- **Duplicate task:** use idempotency and reconciliation evidence.
- **Sensitive-data exposure:** restrict destinations and logs under approved policy.
- **Automation bias:** show uncertainty and require editable human review.
- **Weak pilot evidence:** define baseline, cohort, sampling, and measurement method before interpreting results.
- **Slow processing:** validate candidate architectures against the approved input boundary and response-time target before pilot approval.

### Stop conditions

- task creation occurs without confirmation;
- retries create duplicates;
- source or confirmation evidence cannot be distinguished;
- the no-action sensitivity threshold falls below 95% in the human-reviewed supported sample;
- required privacy, retention, or destination authorization is unresolved for the pilot;
- architecture cannot demonstrate a credible path to the approved response-time threshold.

## 9. Hunter-Skeptic-Referee record

### Hunter

Added participant resolution, no-action handling, deadline interpretation, accessibility, export, failure recovery, retention, performance, extraction-quality, and operational evidence.

### Skeptic

Challenged the unmeasurable outcome, owner ambiguity, confirmation boundary, false no-action risk, retry duplication, retention gap, undefined response-time target, and premature task-integration choice.

### Repair disposition

All P1 findings were repaired through measurable pilot metrics, explicit owner and deadline resolution, reviewer-confirmed no-action outcomes, a 95% no-action sensitivity threshold, pre-creation payload review, idempotency, retention requirements, and ADR routing. The response-time P2 finding was repaired with an approved threshold and supported-input boundary. Remaining P2 constraints are visible architecture and policy decisions rather than undefined product intent.

### Referee

`APPROVED_WITH_CONSTRAINTS`: after the separate product-owner approval, product intent is stable enough for architecture analysis, subject to pilot policy, privacy, extraction-quality and performance feasibility, and integration decisions. No executable implementation scope is authorized by this artifact alone.

## 10. Product-owner and stakeholder approval

- **Product-owner decision:** approved through the explicit post-repair decision quoted above, after the complete repaired contract and measurable thresholds were presented.
- **Authority basis:** the example input states that the requester is the product owner and may make product-requirement decisions.
- **Additional stakeholder decisions:** none are asserted. Production use would require the stakeholder approvals triggered by privacy, security, retention, accessibility, and destination ownership.
- **Approval limitation:** this approval applies only to the neutral example artifact and is not evidence of approval for a real organization or deployment.

## 11. ADR candidate register

| ID | Decision question | Triggering requirements | Why material | Required reviewers | Status |
| --- | --- | --- | --- | --- | --- |
| `ADR-CAND-001` | Which task-system integration pattern creates confirmed tasks while preserving idempotency, authorization, reconciliation, and rollback? | `FR-006`–`FR-010`, `SEC-003`, `OPS-001`–`OPS-004` | Affects correctness, security, recovery, and supported destinations | Architecture, security, operations, destination owner | `candidate` |
| `ADR-CAND-002` | Which extraction and confidence approach can meet the approved quality, privacy, 60-second pilot threshold, no-action sensitivity, explainability, and cost constraints? | `FR-002`–`FR-004`, `NFR-003`–`NFR-005`, `SEC-001` | Affects user trust, data handling, extraction quality, performance, and cost | Architecture, privacy, product, data/AI reviewer | `candidate` |
| `ADR-CAND-003` | Where and for how long should source notes, review history, confirmation evidence, and outcomes be retained? | `FR-008`, `SEC-002`, `DATA-001`–`DATA-003` | Affects privacy, auditability, deletion, and support | Privacy, security, records owner, architecture | `candidate` |
| `ADR-CAND-004` | How should participant identity be resolved without silently assigning the wrong person? | `FR-003`–`FR-004`, `SEC-003`, `DATA-003` | Affects authorization and task ownership | Identity, security, product, architecture | `candidate` |

No architecture solution is selected in this PRD.

## 12. Change control and traceability

- Every requirement change creates a new PRD version and preserves this version.
- Product-intent changes require product-owner approval plus any stakeholder approvals triggered by the change.
- Architecture findings that require product compromise return a decision packet referencing affected requirement IDs.
- Downstream traceability must follow `PRD requirement -> accepted ADR decision -> epic/story/test -> environment evidence`.
- A generated backlog, task, or implementation plan is non-authoritative until separately reviewed and approved.

## 13. Persistence, limitations, and next gate

- **Persistence:** `not persisted`; this example exists only in the skill reference.
- **Connected project state:** not used.
- **Repository implementation state:** not asserted.
- **Remaining constraints:** privacy and retention policy, task destination, identity source, pilot baseline, quality sample, and performance feasibility require downstream decisions or evidence.
- **Next governed action:** architecture analysis of the four ADR candidates, including feasibility against the approved response-time and no-action sensitivity thresholds, followed by requirement-to-ADR alignment. Do not create executable implementation stories until architecture authority and delivery scope are separately approved.
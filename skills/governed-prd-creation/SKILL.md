---
name: governed-prd-creation
description: Create, review, repair, version, approve, and hand off governed Product Requirements Documents that define stable product intent before architecture or implementation planning. Use for measurable PRDs, Hunter-Skeptic-Referee product review, controlled revisions, ADR candidate identification, stakeholder approval, traceability, and either standalone artifact delivery or optional connected project and document systems.
metadata:
  version: 1.2.0
  canonical_repository: deldos/skills
  canonical_path: skills/governed-prd-creation
---

# Governed PRD Creation

## Operating contract

Own the product-intent stage only:

1. discovery and evidence intake;
2. PRD draft;
3. Hunter-Skeptic-Referee product review;
4. stakeholder review and decision capture;
5. repair or controlled revision;
6. PRD approval;
7. approved PRD artifact or storage lineage;
8. architecture-analysis handoff with an ADR candidate register.

Do not select technical solutions merely to complete the PRD. Do not create implementation stories as executable backlog. Do not accept an ADR as architecture authority. In the private governed environment, route approved PRDs through `governed-prd-adr-delivery` for the non-bypassable architecture, repository-review, execution-packaging, and delivery transitions. In portable standalone operation, use an equivalent architecture workflow when that private specialist is unavailable.

## Universal preflight compatibility

When a broader governed delivery flow invokes this skill, accept P0-P2 context from `app-delivery-workshop` when available: product authority/target, prior evidence/reuse, and initial risk/acceptance framing. Do not force the generic W1-W5 staged-convergence sequence around PRD creation. This skill's product-intent lifecycle, Hunter-Skeptic-Referee product review, stakeholder decision capture, and authorized product-owner approval remain controlling.

Use `app-delivery-workshop` for discovery and option shaping only; a workshop or preflight result cannot approve the PRD or replace the product trio.

## Operating modes

Load `references/public-modes-and-example.md` and choose one of these three modes before drafting.

### Standalone mode

Use when the user supplies sufficient discovery material, the authorized product owner is identified, and no governed project system or document store is required.

- Treat explicit user decisions as authoritative only when the user has the stated decision right.
- Return the approved or review-ready PRD as a complete artifact in the current conversation.
- Record version, lifecycle state, approval basis, evidence limitations, and unresolved constraints inside the artifact.
- Use stable requirement IDs and a self-contained ADR candidate register.
- Do not claim persistence, stakeholder approval, repository state, or downstream execution unless verified.

Standalone mode must remain fully usable without Action Production, Action Worker, Cortex, GitHub, or any other connector.

### Standalone-proposal mode

Use whenever the product owner, approval basis, or minimum product evidence is incomplete, regardless of whether connected systems or authority records are available.

- Produce a clearly marked proposal artifact with operating mode `standalone-proposal` and lifecycle state `PRD_DRAFT`.
- List missing decisions, missing evidence, assumptions, and the authority required to approve the PRD.
- Do not claim product-owner approval, persistence, architecture readiness, or permission to create executable delivery work.
- Permit review and repair of the proposal while keeping approval and architecture handoff blocked.

### Connected governance mode

Use only when connected systems are available and relevant and sufficient product authority and minimum product evidence have already been established.

- Resolve the project, approved facts, product authority, existing PRDs, decisions, and execution records.
- Use a connected document store for the approved PRD only after duplicate, version, and write-scope checks.
- Use repository and delivery systems only for their respective evidence domains.
- Preserve exact source status separately from assessment.
- Report unavailable reads, writes, or specialist validations as constraints or `Unknown`.

Connected systems enhance authority, persistence, and traceability; they are not prerequisites for creating a valid standalone PRD and never override the proposal-mode baseline gate.

## Authority model

Apply this precedence:

1. explicit authorized product-owner decisions and approved project facts when a governed project system is connected;
2. the approved PRD version or signed-off standalone artifact: product-intent baseline;
3. verified stakeholder evidence, research, user feedback, and current-system facts: supporting evidence;
4. repository ADRs: architecture authority only, never product-intent authority;
5. delivery actions, stories, and tests: execution evidence after design approval;
6. chat notes, drafts, assumptions, and unapproved records: proposals only.

When product authority, approval basis, or minimum evidence is incomplete, use `standalone-proposal` regardless of connected-system availability until the authorized product owner approves a sufficiently evidenced PRD. The PRD remains valid when an ADR is superseded unless the product requirements themselves change.

## Specialist routing

Use these skills or equivalent workflows when available:

- scope classification and Hunter-Skeptic-Referee arbitration;
- discovery workshops for actors, journeys, options, and evidence collection;
- duplicate-aware document storage and versioning;
- project PM/PO workflow for approved facts, stakeholder authority, and execution writeback;
- post-approval architecture and ADR delivery lifecycle.

In the private governed environment, use `governed-project-scoping-reference`, `app-delivery-workshop`, `cortex-document-management`, and the active project PM/PO skill when their lanes are triggered. After PRD approval, `governed-prd-adr-delivery` is the required private handoff when available; do not replace it with a generic architecture workflow merely because an equivalent portable workflow exists.

If a specialist is unavailable, apply the bundled reference contract and record the unavailable validation as a constraint. Generic or equivalent routing is permitted for portable standalone operation and for a genuinely unavailable private specialist, but it must not bypass an available mandatory private delivery transition.

## Lifecycle states

Use these product-intent states:

- `DISCOVERY`
- `PRD_DRAFT`
- `PRD_PRODUCT_REVIEW`
- `PRD_REPAIR`
- `PRD_STAKEHOLDER_REVIEW`
- `PRD_APPROVED`
- `PRD_REVISION_REQUIRED`
- `PRD_SUPERSEDED`

Do not label a PRD `APPROVED` while a P0/P1 product ambiguity, unowned requirement, unmeasurable outcome, or unresolved stakeholder contradiction remains.

## Workflow

### 1. Establish mode and baseline

Before drafting:

- choose standalone, standalone-proposal, or connected governance mode;
- identify the product owner or decision authority, users, stakeholders, and affected systems;
- separate verified facts, stakeholder decisions, assumptions, and proposals;
- identify current pain, evidence, constraints, desired outcome, and scope boundaries;
- search available conversation, file, document, project, and repository sources for prior PRDs or decisions;
- identify whether the request is a new PRD, revision, or repair;
- record unavailable sources as constraints rather than inventing state.

If the product owner or approval basis, problem, target user, success outcome, or scope boundary cannot be established, use operating mode `standalone-proposal` with lifecycle state `PRD_DRAFT`. Do not proceed to approval, persistence claims, connected-state claims, or architecture handoff. The proposal must list the missing decisions and evidence.

### 2. Draft product intent

Load `references/prd-contract.md`.

Create stable requirement IDs and keep product requirements solution-neutral unless a technology or platform is an approved fixed constraint.

Required distinction:

- product need: what users or the business must achieve;
- fixed constraint: a binding platform, legal, security, budget, or timing condition;
- architecture question: a material technical choice to be resolved later;
- implementation idea: a non-binding proposal.

Do not turn implementation ideas into mandatory requirements without explicit product-owner approval.

### 3. Run product review

Load `references/product-review.md`.

Run three explicit passes:

- **Hunter:** discover missing users, journeys, requirements, outcomes, exclusions, dependencies, and evidence.
- **Skeptic:** challenge value, ambiguity, feasibility, affordability, internal contradictions, testability, privacy, and operational supportability.
- **Referee:** decide product-intent readiness and record constraints.

Allowed verdicts:

- `APPROVED`
- `APPROVED_WITH_CONSTRAINTS`
- `REPAIR`
- `DEFER`
- `ESCALATE`

Only the first two permit architecture handoff.

### 4. Conduct stakeholder review

Load `references/stakeholder-approval.md`.

Record:

- required approvers and consulted stakeholders;
- decisions, objections, and accepted trade-offs;
- requirement changes made during review;
- approval evidence and date;
- constraints or unresolved non-blocking items.

User approval in chat may serve as product-owner approval when the user has that authority. Do not imply approval from absent stakeholders.

### 5. Identify ADR candidates

Load `references/adr-candidate-register.md`.

Architecture analysis may produce zero, one, or several ADR candidates. Each candidate must state:

- decision question;
- triggering requirement IDs;
- why the choice is material;
- known constraints and alternatives;
- required technical reviewers;
- status: `candidate`, `not-required`, `deferred`, or `blocked`.

Do not choose the solution inside the candidate register. One PRD may generate multiple ADRs. One ADR may support multiple requirements or, with explicit traceability, multiple PRDs.

### 6. Approve and persist the PRD

Approval requires:

- stable problem and target users;
- measurable outcomes and success metrics;
- complete goals, non-goals, and exclusions;
- testable functional and non-functional requirements;
- explicit fixed constraints and assumptions;
- no unresolved P0/P1 product-review finding;
- recorded product-owner decision and triggered stakeholder decisions;
- ADR candidate register complete enough for architecture analysis;
- requirement IDs suitable for downstream traceability.

In standalone mode:

- return a complete versioned PRD artifact;
- include the review record, approval basis, requirement catalogue, ADR candidate register, change-control rule, and evidence limitations;
- preserve prior versions when revising an approved PRD;
- label unpersisted or unsigned outputs accurately.

In connected governance mode, after duplicate, version, permission, and write-scope checks, attempt to store the approved PRD in an available authorized document system.

After a successful authorized write, record:

- PRD ID and version;
- lifecycle status;
- project and product owner;
- requirement-set hash or version marker when available;
- prior or superseded PRD IDs;
- related discovery and delivery records;
- ADR candidate register;
- verified storage reference and evidence timestamp.

When no writable document system is available or the write is blocked, duplicate, unauthorized, or unsuccessful, do not invent a storage reference. Record an explicit persistence status such as `not persisted`, `blocked`, or `write failed`, retain the complete PRD artifact, and report the constraint and next safe action.

Draft stored copies remain non-authoritative until approved.

### 7. Hand off to architecture

In the private governed environment, provide the approved PRD to `governed-prd-adr-delivery` when that specialist is available. In portable standalone operation, provide an equivalent architecture workflow with:

- approved PRD artifact or verified document reference and version;
- requirement catalogue and IDs;
- success metrics and product E2E goal;
- fixed constraints versus open architecture questions;
- ADR candidate register;
- stakeholder approval record;
- unresolved safe constraints;
- PRD change-control rule.

The architecture stage must not silently alter a requirement.

## Architecture feedback loop

Load `references/feedback-and-change-control.md`.

When architecture analysis finds a feasibility, cost, security, scalability, or supportability problem:

1. state the affected PRD requirement IDs;
2. provide technical evidence and available options;
3. return a product decision packet;
4. move the PRD to `PRD_REVISION_REQUIRED` when product intent must change;
5. obtain product-owner approval plus any stakeholder approvals triggered by the revised requirement;
6. create a new PRD version and preserve the prior version;
7. mark affected ADR drafts or accepted ADRs for alignment review;
8. rerun traceability before implementation baselining.

Architecture may constrain an implementation approach but may not silently weaken or replace a product requirement.

## Traceability contract

Load `references/traceability.md`.

Maintain this chain:

`PRD requirement -> ADR decision(s) -> epic/story/test -> environment evidence`

A requirement can map to zero ADRs when no material technical decision is needed. It can map to several ADRs when independent architecture choices are required.

Implementation stories must later derive from both:

- the PRD requirement and measurable outcome;
- the accepted ADR decision and technical constraints.

## Repair mode

When reviewing an existing PRD:

1. identify its version and authority status;
2. preserve valid product intent;
3. separate architecture or implementation content that does not belong in the PRD;
4. assign stable requirement IDs;
5. repair ambiguity, metrics, exclusions, stakeholder evidence, and traceability;
6. rerun product trio and stakeholder review;
7. create a new version rather than silently overwriting an approved baseline;
8. flag affected ADRs and backlog items for alignment review.

## Required final reporting

Load `references/output-templates.md`.

Always report:

- operating mode;
- PRD lifecycle state and version;
- product owner and stakeholder approval status;
- problem, users, outcomes, and E2E goal;
- requirement counts by type;
- trio verdict and constraints;
- explicitly identified proposal artifact, review-ready standalone artifact, approved PRD artifact, or verified storage reference, together with its persistence status;
- ADR candidate count and decision questions;
- affected prior ADRs or backlog;
- evidence limitations, blockers, and next governed action.

Never claim PRD approval, persistence, stakeholder sign-off, repository state, or architecture readiness without current-session evidence.

## Public demonstration

Use the neutral meeting follow-up tool example in `references/public-modes-and-example.md` to test:

- direct user-supplied discovery input and explicit product-owner authority;
- solution-neutral requirements;
- human confirmation before task creation;
- Hunter-Skeptic-Referee review;
- one repair cycle;
- a complete repaired PRD artifact;
- requirement catalogue and ADR candidates;
- standalone artifact delivery without private connectors.

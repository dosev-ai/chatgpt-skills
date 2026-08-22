---
name: governed-prd-creation
description: Create, review, repair, version, approve, and hand off measurable Product Requirements Documents before architecture or implementation planning. Use for new PRDs, PRD repair, Hunter-Skeptic-Referee product review, approval control, ADR-candidate identification, traceability, standalone artifact delivery, or optional connected governance.
license: MIT
metadata:
  version: 1.2.0
  canonical_repository: deldos/skills
  canonical_path: skills/governed-prd-creation
---

# Governed PRD Creation

## Operating contract

Own the product-intent stage only:

1. discovery and evidence intake;
2. mode selection;
3. PRD drafting;
4. Hunter-Skeptic-Referee product review;
5. stakeholder and product-owner decision capture;
6. repair or controlled revision;
7. approval and persistence reporting;
8. architecture handoff with an ADR-candidate register.

Do not select implementation technologies merely to finish the PRD. Do not turn a PRD into executable backlog. An approved PRD authorizes architecture analysis, not implementation.

## Reusable preflight compatibility

When a broader delivery workflow has already established product authority, target users, prior evidence, reuse options, or initial risk and acceptance framing, accept that verified context as preflight input rather than rediscovering it. Keep the PRD lifecycle, Hunter-Skeptic-Referee product review, stakeholder decision capture, and authorized product-owner approval controlling.

An upstream workshop, discovery flow, or preflight result may shape evidence and options, but it cannot approve the PRD or replace the product review and approval gates.

## Operating modes

Load `references/public-modes-and-example.md` before drafting.

### Standalone-proposal

Use whenever product authority, approval basis, the problem, target users, success outcome, scope boundary, or minimum evidence is incomplete. This mode takes precedence even when connected systems are available.

Return a complete proposal artifact with:

- mode `standalone-proposal`;
- lifecycle state `PRD_DRAFT`;
- missing-decision and missing-evidence registers;
- assumptions and evidence limitations;
- no approval, persistence, architecture-readiness, or delivery-authority claim.

### Standalone

Use when sufficient evidence and an explicit product decision authority are established and no connected write is required.

Return a complete versioned PRD artifact in the conversation. Separate the authority to decide from explicit approval of the repaired requirements. Record the artifact identity and persistence status independently.

### Connected-governance

Use only when sufficient product authority and evidence are established and relevant connected systems are available and authorized.

Read connected state in the current session before relying on it. Keep exact source state separate from assessment. Attempt a write only after duplicate, version, permission, policy, and write-scope checks. Unavailable state is `Unknown`.

## Authority and evidence

Apply this precedence:

1. explicit decisions by an authorized product owner;
2. approved project facts when a governed project system is connected;
3. the approved PRD version or signed-off standalone artifact;
4. verified stakeholder, user, research, and current-system evidence;
5. architecture decisions as architecture authority only;
6. delivery actions and tests as downstream execution evidence;
7. chat notes, assumptions, and drafts as proposals.

Never infer authority from a title or name. Never treat an authority statement as approval of requirements that have not yet been presented. Never invent project, document, action, repository, approval, or storage identifiers.

## Workflow

### 1. Establish mode and baseline

Identify the product owner or decision authority, target users, problem, desired outcome, scope boundaries, evidence, assumptions, constraints, and prior PRD state. If any minimum product element is missing, use `standalone-proposal`.

### 2. Draft product intent

Load `references/prd-contract.md`. Keep these distinct:

- product need;
- approved fixed constraint;
- architecture question;
- non-binding implementation idea.

Use stable requirement IDs and solution-neutral language unless a technology is an approved fixed constraint.

### 3. Run product review

Load `references/product-review.md` and run three explicit passes:

- **Hunter:** find missing users, journeys, requirements, evidence, exclusions, dependencies, and outcomes.
- **Skeptic:** challenge value, ambiguity, unsupported claims, contradictions, testability, privacy, feasibility, affordability, and supportability.
- **Referee:** issue `APPROVED`, `APPROVED_WITH_CONSTRAINTS`, `REPAIR`, `DEFER`, or `ESCALATE`.

Only `APPROVED` and `APPROVED_WITH_CONSTRAINTS` permit architecture handoff, and only after required decisions are recorded.

### 4. Conduct stakeholder review

Load `references/stakeholder-approval.md`. Record required approvers, consulted stakeholders, decisions, objections, accepted trade-offs, requirement changes, evidence, dates, and constraints. Do not imply absent approval.

### 5. Identify ADR candidates

Load `references/adr-candidate-register.md`. Record zero-to-many material architecture questions, triggering requirement IDs, constraints, alternatives, reviewers, and status. Do not choose a solution inside the PRD.

### 6. Approve and report persistence

Approval requires stable users and problem, measurable outcomes, complete scope boundaries, testable requirements, explicit constraints and assumptions, no unresolved P0/P1 product finding, recorded product-owner approval, required stakeholder decisions, and a usable ADR-candidate register.

Record exactly one persistence state:

- `persisted`: a verified authorized write succeeded;
- `not persisted`: no write was attempted or required;
- `blocked`: approval, permission, duplicate, policy, or write-scope controls prevented the write;
- `write failed`: an authorized write attempt did not complete.

Always retain the complete PRD artifact. A storage reference may be reported only after a verified successful write.

### 7. Hand off to architecture

Provide the approved artifact or verified storage reference, persistence state, requirement catalogue, metrics, E2E goal, fixed constraints, open architecture questions, ADR candidates, decision evidence, unresolved safe constraints, and change-control rule. Architecture may not silently weaken a requirement.

## Change control

Load `references/feedback-and-change-control.md` and `references/traceability.md`.

Maintain:

`PRD requirement -> accepted ADR decision -> epic/story/test -> environment evidence`

When architecture evidence requires product compromise, return a decision packet, revise the PRD under product authority, preserve the previous version, and rerun traceability.

## Required final report

Load `references/output-templates.md` and always report:

- operating mode;
- lifecycle state and version;
- product-owner authority and approval status separately;
- stakeholder approval status;
- problem, users, outcome, and E2E goal;
- requirement counts by type;
- Hunter, Skeptic, and Referee verdicts;
- artifact identity and persistence status separately;
- ADR-candidate count and decision questions;
- evidence limitations, blockers, and next governed action.

Never claim approval, persistence, stakeholder sign-off, connected state, or architecture readiness without current evidence.

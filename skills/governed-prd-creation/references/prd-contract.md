# PRD Contract

## Purpose

Define stable product intent: what must be achieved, for whom, why it matters, how success is measured, and what remains outside scope.

## Required metadata

- PRD ID, title, version, date, lifecycle status, and operating mode;
- product owner or decision-authority basis, reviewers, and stakeholders;
- prior or superseded PRD references;
- related discovery evidence and evidence limitations;
- artifact or verified storage reference;
- persistence status: `persisted`, `not persisted`, `blocked`, or `write failed`;
- optional connected project, delivery, repository, and document-system references when available.

Use `persisted` only after a verified authorized write. Use `not persisted` when no write was attempted or no writable document system was required or available. Use `blocked` when duplicate, permission, policy, approval, or write-scope controls prevented the write. Use `write failed` when an authorized write was attempted but did not complete successfully. Do not invent project, document, action, repository, approval, or storage identifiers.

## Required sections

1. **Executive intent**
   - problem statement;
   - target users and actors;
   - business or operational outcome;
   - product E2E goal.

2. **Evidence and current state**
   - observed pain and supporting evidence;
   - verified current-system facts;
   - assumptions and evidence gaps;
   - source availability and evidence limitations.

3. **Goals and scope**
   - goals;
   - minimum shippable product outcome;
   - non-goals;
   - exclusions and deferred scope;
   - affected user and operational surfaces.

4. **Requirements catalogue**
   - business requirements `BR-*`;
   - functional requirements `FR-*`;
   - non-functional requirements `NFR-*`;
   - security/privacy/compliance requirements `SEC-*`;
   - operational/support requirements `OPS-*`;
   - data and migration outcomes when product-relevant `DATA-*`.

5. **Success and acceptance**
   - success metrics with baseline, target, measurement method, and decision window;
   - product acceptance criteria;
   - user and operational failure conditions.

6. **Constraints and assumptions**
   - fixed platform/business/legal constraints;
   - budget and timing constraints;
   - assumptions requiring validation;
   - architecture questions that must not be answered in the PRD.

7. **User journeys and coverage**
   - primary happy paths;
   - negative/fail-closed journeys;
   - admin/operator/recovery journeys;
   - accessibility and compatibility journeys where applicable.

8. **Dependencies and risks**
   - upstream prerequisites;
   - downstream consumers;
   - product, adoption, compliance, operational, and evidence risks;
   - stop conditions.

9. **ADR candidate register**
   - zero-to-many material technical decision questions;
   - triggering requirement IDs;
   - no selected solution unless already a fixed approved constraint.

10. **Review and approval**
    - Hunter, Skeptic, Referee dispositions;
    - stakeholder decisions;
    - product-owner approval basis;
    - constraints and change-control rule;
    - persistence status.

## Requirement quality rules

Each requirement must be:

- uniquely identified;
- necessary and attributable to a user or business outcome;
- unambiguous;
- testable or measurable;
- solution-neutral unless a fixed constraint is approved;
- scoped to an actor, object, condition, and expected result;
- linked to at least one success metric, acceptance criterion, or justified compliance obligation.

Avoid requirements such as "use Elasticsearch" unless the technology is a fixed approved constraint. Prefer: "Search 500,000 authorized documents with p95 response under two seconds."

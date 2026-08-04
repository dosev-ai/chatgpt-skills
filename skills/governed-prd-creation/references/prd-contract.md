# PRD Contract

## Purpose

Define stable product intent: what must be achieved, for whom, why it matters, how success is measured, and what remains outside scope.

## Required metadata

- PRD ID, title, version, date, lifecycle state, and operating mode;
- product owner or decision-authority basis;
- product-owner approval status and evidence;
- required stakeholder decisions;
- prior or superseded PRD references;
- evidence sources, assumptions, and limitations;
- artifact identity or verified storage reference;
- persistence status: `persisted`, `not persisted`, `blocked`, or `write failed`.

Use `persisted` only after a verified authorized write. Use `not persisted` when no write was attempted or required. Use `blocked` when approval, permission, duplicate, policy, or write-scope controls prevented the write. Use `write failed` when an authorized write attempt did not complete. Never invent an identifier.

## Required sections

1. Executive intent: problem, users, outcome, and E2E goal.
2. Evidence and current state: supplied facts, verified state, assumptions, gaps, and limitations.
3. Goals and scope: goals, minimum outcome, non-goals, exclusions, and affected surfaces.
4. Requirements catalogue: `BR-*`, `FR-*`, `NFR-*`, `SEC-*`, `OPS-*`, and product-relevant `DATA-*`.
5. Success and acceptance: baseline, target, method, decision window, acceptance criteria, and failure conditions.
6. Constraints and assumptions: fixed constraints, budget/timing, assumptions, and unresolved architecture questions.
7. Journeys: primary, negative, fail-closed, recovery, operator, accessibility, and compatibility flows where relevant.
8. Dependencies and risks: prerequisites, downstream consumers, risks, controls, and stop conditions.
9. ADR-candidate register: zero-to-many material technical decision questions and triggering requirements.
10. Review and approval: Hunter, Skeptic, Referee, product-owner decision, stakeholder decisions, constraints, change control, and persistence.

## Requirement quality

Each requirement must be uniquely identified, attributable to a user or business outcome, unambiguous, testable, solution-neutral unless a fixed constraint is approved, scoped to an actor and condition, and linked to a metric, acceptance criterion, or compliance obligation.

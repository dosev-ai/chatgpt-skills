# ADR Candidate Register

## Purpose

Identify material technical decisions without making them inside the PRD.

## Candidate fields

- candidate ID;
- decision question;
- triggering PRD requirement IDs;
- why the decision is material;
- verified platform constraints;
- known alternatives, without selecting one;
- consequences requiring analysis;
- technical/security/data/operations reviewers;
- status: `candidate`, `not-required`, `deferred`, or `blocked`;
- re-entry or decision condition.

## Materiality tests

Create an ADR candidate when the choice materially affects one or more of:

- architecture or platform boundary;
- security, privacy, identity, or authorization;
- persistent data model or migration;
- integration/API/MCP contract;
- scalability, availability, or performance strategy;
- vendor/platform commitment;
- rollout, rollback, or operational support model;
- cross-project reusable standard.

Routine implementation detail does not require an ADR.

## Cardinality

- one PRD can produce zero ADRs;
- one PRD can produce several ADRs;
- one ADR can satisfy several requirements;
- an ADR can reference several PRDs only when the shared decision and lineage are explicit.

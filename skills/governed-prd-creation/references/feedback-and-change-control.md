# Architecture Feedback and PRD Change Control

## Feedback packet

When architecture analysis cannot satisfy a requirement as written, return:

- affected requirement IDs;
- technical evidence;
- feasibility, security, cost, timing, or supportability concern;
- available options and product consequences;
- recommendation, clearly labelled as a proposal;
- decision deadline and affected ADRs/backlog.

## Product decision

The product owner may:

- retain the requirement and accept higher cost/risk;
- revise the target or constraint;
- split the requirement into phases;
- defer or remove the requirement;
- request further evidence.

Architecture must not silently change the PRD.

## Versioning

For an approved PRD change:

1. create a new PRD version;
2. preserve the prior approved version;
3. record changed requirement IDs and rationale;
4. rerun affected stakeholder and trio review;
5. mark affected ADRs `alignment_review_required`;
6. invalidate backlog acceptance criteria derived from superseded requirements;
7. rebaseline only after PRD-ADR alignment passes.

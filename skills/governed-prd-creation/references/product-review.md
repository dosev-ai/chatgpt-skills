# Product Hunter-Skeptic-Referee Review

## Hunter

Search for missing product intent:

- users, actors, and stakeholders;
- current pain and evidence;
- business outcome and measurable success;
- happy, negative, recovery, and operational journeys;
- accessibility, privacy, compliance, and support needs;
- scope exclusions and deferred work;
- dependencies, adoption, rollout, and change-management needs;
- ambiguous requirements or hidden architecture prescriptions;
- ADR candidates.

Output: additions, evidence gaps, and candidate repairs.

## Skeptic

Challenge:

- whether the problem is real and sufficiently evidenced;
- whether the proposed scope creates user/business value;
- contradictory or untestable requirements;
- success metrics without baseline or measurement path;
- hidden solution bias;
- cost, timing, adoption, support, and compliance feasibility;
- requirements that exceed known constraints;
- stakeholder conflicts;
- unsafe assumptions presented as facts;
- whether architecture feedback would require a product decision.

Classify findings:

- P0: product intent is invalid or unsafe;
- P1: approval blocker;
- P2: material constraint or required follow-up;
- P3: improvement or clarity issue.

## Referee

Decide one verdict:

- `APPROVED`
- `APPROVED_WITH_CONSTRAINTS`
- `REPAIR`
- `DEFER`
- `ESCALATE`

Approval means product intent is stable enough for architecture analysis, not that architecture or implementation is approved.

Record:

- approved scope and outcomes;
- non-bypassable product constraints;
- accepted assumptions;
- required stakeholder decisions;
- ADR candidate set;
- PRD change-control conditions.

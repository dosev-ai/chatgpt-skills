# Output Templates

## PRD review summary

```text
PRD: <id/title/version>
Mode: <standalone|connected-governance|standalone-proposal>
State: <state>
Product owner: <name/authority basis>
Product-owner approval: <approved|pending|rejected|not established, with evidence>
Users: <actors>
Outcome: <measurable outcome>
E2E goal: <product journey>
Requirements: BR <n> | FR <n> | NFR <n> | SEC <n> | OPS <n>
Hunter: <verdict>
Skeptic: <verdict and blockers>
Referee: <verdict and constraints>
Stakeholder approval: <status>
ADR candidates: <count and IDs>
PRD artifact or storage reference: <proposal artifact|review-ready standalone artifact|approved artifact|verified storage ID>
Persistence status: <persisted|not persisted|blocked|write failed>
Evidence limitations: <unknowns or none>
Next gate: <action>
```

## Architecture feedback packet

```text
Affected PRD: <id/version>
Requirement IDs: <ids>
Evidence: <technical facts>
Conflict: <why current requirement cannot safely or affordably be met>
Options: <product consequences>
Recommendation: <proposal, not decision>
Required authority: <product owner/stakeholders>
Downstream impact: <ADRs/stories/tests>
```

## Handoff to architecture lifecycle

```text
Approved PRD artifact or storage reference: <artifact|verified storage reference/version>
Persistence status: <persisted|not persisted|blocked|write failed>
Requirement catalogue: <reference>
Success metrics: <reference>
Fixed constraints: <list>
Architecture questions: <list>
ADR candidate register: <list>
Product-owner approval: <evidence>
Stakeholder approval: <evidence>
Change-control rule: <rule>
Alignment gate: required before ADR acceptance
```

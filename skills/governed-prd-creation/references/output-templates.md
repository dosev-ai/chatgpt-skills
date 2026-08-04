# Output Templates

## PRD review summary

```text
PRD: <id/title/version>
Mode: <standalone-proposal|standalone|connected-governance>
State: <state>
Product owner: <authority basis>
Product-owner approval: <approved|pending|rejected|not established, with evidence>
Stakeholder approval: <status and evidence>
Users: <actors>
Problem: <source-faithful problem statement>
Outcome: <measurable outcome>
E2E goal: <product journey>
Requirements: BR <n> | FR <n> | NFR <n> | SEC <n> | OPS <n> | DATA <n>
Hunter: <findings>
Skeptic: <findings and blockers>
Referee: <verdict and constraints>
Artifact: <proposal|review-ready|approved|verified storage reference>
Persistence: <persisted|not persisted|blocked|write failed>
ADR candidates: <count and IDs>
Evidence limitations: <unknowns or none>
Next gate: <action>
```

## Architecture feedback packet

```text
Affected PRD: <id/version>
Requirement IDs: <ids>
Technical evidence: <facts>
Conflict: <why the requirement cannot safely or affordably be met>
Options: <product consequences>
Recommendation: <proposal, not decision>
Required authority: <product owner and triggered stakeholders>
Downstream impact: <ADRs, stories, tests, and evidence>
```

## Architecture handoff

```text
Approved PRD artifact or verified storage reference: <reference/version>
Persistence: <persisted|not persisted|blocked|write failed>
Requirement catalogue: <reference>
Metrics and E2E goal: <reference>
Fixed constraints: <list>
Open architecture questions: <list>
ADR candidates: <list>
Approval evidence: <product owner and stakeholders>
Change-control rule: <rule>
Alignment gate: required before architecture acceptance
```

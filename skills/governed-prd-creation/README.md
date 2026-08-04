# Governed PRD Creation

Create a measurable, reviewable Product Requirements Document that stabilizes product intent before architecture selection or implementation planning.

## What it does

`governed-prd-creation` turns discovery notes, stakeholder needs, feature ideas, research, or an existing draft into a complete versioned PRD artifact. It provides proposal-first mode selection, stable requirement IDs, measurable success criteria, user and recovery journeys, Hunter-Skeptic-Referee review, explicit approval controls, an ADR-candidate register, four persistence outcomes, and downstream traceability.

## Why it exists

Product work often moves into architecture or implementation while authority, outcomes, boundaries, and success measures remain ambiguous. An ad hoc prompt can produce a plausible document without reliably preserving approval state, evidence limits, repair findings, or the distinction between product intent and technical design. This skill packages those controls into one repeatable workflow.

## Benefits

- Produces a self-contained PRD that can be reviewed and versioned.
- Prevents incomplete evidence or authority from being presented as an approved product decision.
- Converts broad goals into stable, testable requirements and measurable acceptance criteria.
- Identifies architecture questions without choosing technologies prematurely.
- Distinguishes `persisted`, `not persisted`, `blocked`, and `write failed` outcomes.
- Preserves a traceable path from requirements to architecture, delivery, and validation.

## When to use it

Use the skill when creating a new PRD, repairing an ambiguous draft, preparing a product contract for architecture analysis, or recording controlled revisions after stakeholder or feasibility feedback.

Representative requests:

- “Turn these discovery notes into a measurable PRD.”
- “Review this PRD and repair ambiguous or untestable requirements.”
- “Identify which requirements require architecture decisions without selecting technologies.”

## How it works

1. Select `standalone-proposal`, `standalone`, or optional `connected-governance` mode from current evidence and decision authority.
2. Define the problem, users, outcomes, boundaries, requirements, journeys, metrics, constraints, assumptions, dependencies, and risks.
3. Run Hunter, Skeptic, and Referee passes and repair blocking findings.
4. Capture explicit product-owner and triggered stakeholder decisions.
5. Produce the versioned PRD, ADR-candidate register, persistence status, evidence limitations, and next governed action.

## Installation

Download `skill.zip` from this directory and upload it as a single ChatGPT skill. The archive contains the complete public skill bundle, including `SKILL.md`, agent metadata, references, and assets. Verify the archive SHA-256 against the `package_sha256` recorded in the repository manifest before installation.

## Limitations

The skill does not infer product authority from names or titles, invent project or storage identifiers, select implementation technologies, approve architecture decisions, or convert a PRD directly into executable delivery work. Connected systems are optional and may be used only after current-session reads and authorization checks. Legal, security, privacy, accessibility, and regulatory approvals remain with their authorized decision-makers.

## Canonical lineage

- Canonical repository: `deldos/skills`
- Canonical path: `skills/governed-prd-creation`
- Canonical version: `1.1.1`
- Canonical source PR: `#33`
- Canonical final PR HEAD: `eab6db6554841182fe763fc7781a8e8db90feaa2`
- Canonical merge commit: `f218d5ffaddcab12a736420166f3348b31183dac`

## Release status

- Public release state: `public-released`
- Public pull request: `#2`
- Artifact status: `package`
- Package path: `skills/governed-prd-creation/skill.zip`
- Package integrity: `SHA-256 recorded in skills-manifest.yaml`
- Clean-room verification: `PASS: Clean-room mounted installation from public merge ee6c7a853b18e8f3928f1c5a299a0d9750fcfb2c matched all 13 governed skill blobs and passed 10 behavioral contract checks; the installable skill.zip contains the same 13 files, extracted with exact source parity, passed skill-creator validation, and is integrity-bound by the manifest package_sha256.`
- Known residuals: `none`

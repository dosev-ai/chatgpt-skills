# Governed PRD Creation

Create a measurable, reviewable Product Requirements Document that stabilizes product intent before architecture selection or implementation planning.

## What it does

`governed-prd-creation` turns discovery notes, stakeholder needs, feature ideas, research, or an existing draft into a complete versioned PRD artifact. It provides proposal-first mode selection, stable requirement IDs, measurable success criteria, user and recovery journeys, Hunter-Skeptic-Referee review, explicit approval controls, an ADR-candidate register, four persistence outcomes, governed preflight compatibility, specialist-aware downstream routing, and requirement-to-delivery traceability.

## Why it exists

Product work often moves into architecture or implementation while authority, outcomes, boundaries, and success measures remain ambiguous. An ad hoc prompt can produce a plausible document without reliably preserving approval state, evidence limits, repair findings, or the distinction between product intent and technical design. This skill packages those controls into one repeatable workflow.

## Benefits

- Produces a self-contained PRD that can be reviewed and versioned.
- Prevents incomplete evidence or authority from being presented as an approved product decision.
- Reuses verified upstream discovery and preflight context without allowing it to bypass product review or approval.
- Converts broad goals into stable, testable requirements and measurable acceptance criteria.
- Identifies architecture questions without choosing technologies prematurely.
- Distinguishes `persisted`, `not persisted`, `blocked`, and `write failed` outcomes.
- Preserves canonical downstream routing: in the private governed environment, `governed-prd-adr-delivery` is the required post-approval handoff when available; portable equivalent routing is used only when that private specialist is genuinely unavailable.
- Preserves a traceable path from requirements to architecture, delivery, and validation.

## When to use it

Use the skill when creating a new PRD, repairing an ambiguous draft, preparing a product contract for architecture analysis, or recording controlled revisions after stakeholder or feasibility feedback.

Representative requests:

- “Turn these discovery notes into a measurable PRD.”
- “Review this PRD and repair ambiguous or untestable requirements.”
- “Identify which requirements require architecture decisions without selecting technologies.”

## How it works

1. Select `standalone-proposal`, `standalone`, or optional `connected-governance` mode from current evidence and decision authority.
2. Reuse verified upstream `app-delivery-workshop` context when available, without treating a workshop or preflight as PRD approval.
3. Define the problem, users, outcomes, boundaries, requirements, journeys, metrics, constraints, assumptions, dependencies, and risks.
4. Run Hunter, Skeptic, and Referee passes and repair blocking findings.
5. Capture explicit product-owner and triggered stakeholder decisions.
6. Produce the versioned PRD, ADR-candidate register, persistence status, evidence limitations, and next governed action.
7. After approval, preserve the canonical architecture-handoff rule: use `governed-prd-adr-delivery` in the private governed environment when available; use an equivalent portable architecture workflow only when that private specialist is unavailable.

## Public distribution model

This repository is a downstream publishing surface for the same canonical semantic skill. It does not maintain a separately authored public semantic fork.

The public release therefore preserves the canonical instruction body, reference contracts, authority boundaries, optional-capability semantics, and non-bypass rules. Names of optional or private specialists may remain in the public source when they are not themselves sensitive. If such a capability is unavailable in the target runtime, the canonical fallback or fail-closed behavior applies.

Public-only differences are limited to distribution concerns such as MIT licensing, release state, repository lineage, package evidence, and human-facing publication notes.

## Installation

The public 1.2.0 source is being converged through the governed public-release workflow. The previous 1.1.1 `skill.zip` is not a valid 1.2.0 package and was removed from the current skill directory. Build and publish a 1.2.0 package only from the merged and verified public release; until then, package installation remains pending.

## Limitations

The skill does not infer product authority from names or titles, invent project or storage identifiers, select implementation technologies, approve architecture decisions, or convert a PRD directly into executable delivery work. Upstream workshops or preflight results can provide evidence and framing but cannot replace product review or approval. Connected systems are optional and may be used only after current-session reads and authorization checks. Legal, security, privacy, accessibility, and regulatory approvals remain with their authorized decision-makers.

Public availability does not weaken the canonical private-governance path. An available mandatory private delivery transition cannot be bypassed merely because a portable equivalent exists.

## Canonical lineage

- Canonical repository: `deldos/skills`
- Canonical path: `skills/governed-prd-creation`
- Canonical version: `1.2.0`
- Canonical source PR: `#51`
- Canonical final PR HEAD: `a8e3333b9efcdab6621d74312d081c6e1125e8cf`
- Canonical merge commit: `1d734545511227fef25ba131d3fd6e705c248d20`

## Release status

- Public release state: `public-pr-open`
- Public pull request: `#7`
- Artifact status: `none`
- Package path: `pending post-merge rebuild`
- Package integrity: `pending post-merge rebuild and SHA-256 evidence`
- Clean-room verification: `PUBLIC PR #7 OPEN: the recovery projection restores the complete canonical 1.2.0 semantic skill and references; only public licensing, release-state, and lineage documentation remain distribution-specific. Exact-final-HEAD validation/review, merge, merged-tree verification, clean-room invocation, and a new v1.2.0 package remain pending.`
- Known residuals: `Require Public Skill Validation, both required accepted exact-final-HEAD automated reviews, and Bot Comment Closure Rate PASS on public PR #7 before merge.; Verify the merged public source tree and run clean-room invocation before release classification.; Build and publish a v1.2.0 skill.zip only from the merged verified public release, then record package inventory and SHA-256 evidence.`

# Governance

## Authority

1. Merged `deldos/skills` `main` plus its manifest defines the accepted canonical skill source.
2. This repository contains downstream public projections only.
3. Branches, pull requests, local folders, and ZIP archives are proposals until reviewed and merged.
4. Public repository content must not be edited as an independent canonical fork.

## Promotion eligibility

A public projection must originate from a specific reviewed canonical commit. The canonical skill must be either:

- marked `shareable`; or
- replaced by a reviewed public derivative or approved visibility reclassification before projection.

## Public-safety requirements

Every release must remove or abstract:

- credentials, secrets, tokens, and private endpoints;
- personal data and confidential claims;
- private project, action, document, tenant, or environment identifiers;
- mandatory assumptions about unavailable connectors or internal specialist skills.

The safety scan covers the complete tracked public tree, not only registered skill directories. Licensing and attribution must be reviewed before release.

## Trusted review gate

Every public repository change requires automated review of the exact final PR HEAD.

The Bot Comment Gate runs through `pull_request_target` from the protected base branch and never checks out or executes pull-request code. A PR therefore cannot weaken its own required gate while preserving the check name.

Foundation bootstrap exception: the pull request that first installs the protected workflow cannot be validated by that not-yet-merged base-branch workflow. It requires independent exact-head automated review, successful structural validation, resolved findings, and explicit maintainer merge approval. The exception ends immediately after the workflow is merged to `main`.

## Inbound contribution boundary

Until the repository owner approves both a public license and an inbound contribution grant, only maintainer-controlled canonical projections may be merged. Public users may submit public-safe issue reports, but third-party-authored skill content or substantive patches are not accepted.

## Change direction

- Canonical source to public repository: allowed through a reviewed promotion pull request.
- Public defect report: accepted through the public issue tracker and routed by maintainers.
- Public defect to canonical source: record and repair the canonical skill first, then re-promote.
- Direct public-only substantive fixes: prohibited unless a governed exception records why the canonical source is unaffected.

## Pre-merge evidence

Before a public skill projection merges, record:

- skill ID and proposed public version;
- canonical repository and path;
- canonical source pull request, final HEAD, and merge commit;
- sanitization and connector-abstraction record;
- approved license and attribution result;
- validation, tests, exact-head review, finding dispositions, and resolved threads;
- public pull request and final public PR HEAD;
- pre-merge invocation or package evidence when required;
- known residuals and post-merge verification plan.

## Post-merge release evidence

After merge, record:

- public merge commit;
- package or release-artifact status;
- package hash when an artifact is distributed;
- clean-room installation or invocation evidence against merged public content;
- final release state and residuals.

## Allowed release states

- `not-candidate`
- `candidate-needs-sanitization`
- `ready-for-public-pr`
- `public-pr-open`
- `public-merged-verification-pending`
- `public-released`

A public pull request, merge commit, or generated package is not sufficient evidence for `public-released`. A merged projection remains `public-merged-verification-pending` until the clean-room and evidence gates pass.

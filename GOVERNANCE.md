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

Licensing and attribution must be reviewed before release.

## Change direction

- Canonical source to public repository: allowed through a reviewed promotion pull request.
- Public defect to canonical source: record and repair the canonical skill first, then re-promote.
- Direct public-only substantive fixes: prohibited unless a governed exception records why the canonical source is unaffected.

## Release evidence

Record for each public skill:

- skill ID and public version;
- canonical repository and path;
- canonical source pull request, final HEAD, and merge commit;
- sanitization and connector-abstraction record;
- validation, tests, and review dispositions;
- public pull request, final HEAD, and merge commit;
- package hash when a package is distributed;
- clean-room installation or invocation evidence;
- final release state and residuals.

## Allowed release states

- `not-candidate`
- `candidate-needs-sanitization`
- `ready-for-public-pr`
- `public-pr-open`
- `public-released`

A public pull request or generated package is not sufficient evidence for `public-released`.

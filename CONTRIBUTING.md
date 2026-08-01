# Contributing

## Current contribution scope

This repository publishes reviewed downstream projections of skills whose canonical source is maintained in `deldos/skills`.

Until the repository owner approves a public license and an inbound contribution grant, the repository accepts only maintainer-controlled projection pull requests from the canonical source. Do not submit third-party-authored skill content, copied examples, assets, scripts, or substantive patches for inclusion.

Public users may still report defects, documentation gaps, security concerns, or feature requests through the public issue tracker. Maintainers will assess whether the change belongs in the private canonical repository, the public transformation, or both.

Do not open a substantive public-only skill change unless a governed exception explains why the canonical source is unaffected.

## Required projection packet

A public skill projection pull request must include:

- public skill ID and version;
- canonical repository, path, version, and source merge commit;
- canonical source pull request and final reviewed HEAD;
- visibility or public-derivative decision;
- sanitization and connector-abstraction summary;
- approved license and attribution result;
- validation and test evidence;
- pre-merge invocation or inspection evidence when available;
- post-merge clean-room installation or invocation plan;
- known residuals.

## Pre-merge gates

A projection pull request may merge only when:

- the canonical source merge commit is fixed and recorded;
- repository validation passes on the exact final public PR HEAD;
- an automated reviewer has reviewed the exact final public PR HEAD;
- every substantive finding is dispositioned and every review thread is resolved;
- public-safety, secret, personal-data, private-endpoint, internal-ID, license, and attribution checks pass;
- the public documentation and lineage fields match the proposed content;
- the repository license is approved for any PR that introduces or changes a public skill;
- any pre-merge invocation or package test required by the change passes.

The public merge commit and post-merge clean-room verification cannot exist before merge and are therefore not pre-merge requirements.

## Post-merge release gates

After merge, keep the skill in `public-merged-verification-pending` until:

- the public merge commit is recorded;
- any distributed package or release artifact is rebuilt from that merge commit and hashed;
- a clean-room installation or invocation passes against the merged public content;
- final verification evidence, residuals, and release status are recorded.

Only then may the skill enter `public-released`.

## Review rules

- Use pull requests; do not commit substantive changes directly to `main`.
- Keep each skill release bounded and independently reviewable.
- Disposition every substantive review finding.
- Require exact-final-HEAD automated review for every public repository change.
- Do not merge while pre-merge checks, review threads, licensing, source lineage, or public-safety evidence are incomplete.
- Do not describe a merged skill as released until the post-merge gates pass.

## Reporting defects and requests

Public users who cannot access `deldos/skills` should open a public issue in this repository using the appropriate issue form and include only public-safe evidence.

Maintainers will:

1. classify the report as canonical, public-transformation, or both;
2. create or update the private canonical work item when required;
3. repair and review the canonical source first when the defect applies there;
4. re-promote the reviewed canonical result;
5. link a public-safe status or closeout back to the public issue.

Do not include credentials, confidential project data, private repository content, personal data, or internal identifiers in a public issue.

A public-only defect may be repaired directly here only when the public transformation itself is the sole cause and that boundary is documented.

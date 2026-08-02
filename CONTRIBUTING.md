# Contributing

## Current contribution scope

This repository publishes reviewed downstream projections of skills whose canonical source is maintained in `deldos/skills`.

Public skill editions are licensed under the MIT License. The initial contribution model is maintainer-controlled: public users may report defects, documentation gaps, security concerns, installation problems, or feature requests through the public issue tracker, but unsolicited third-party-authored skill content and substantive patches are not accepted at this stage.

Maintainers assess whether a requested change belongs in the private canonical repository, the public transformation, or both. Do not open a substantive public-only skill change unless a governed exception explains why the canonical source is unaffected.

No DCO or CLA is currently required because third-party substantive contributions are disabled. Before enabling them, the repository owner must approve an inbound contribution policy and update this document and `LICENSE-STATUS.md`.

## License and attribution

Repository content is published under the standard MIT License unless a file explicitly states otherwise.

When copying or redistributing the repository or a substantial portion of it, preserve:

- the copyright notice `Copyright (c) 2026 Delyan Dosev`;
- the MIT License text.

The preferred human-readable origin reference is `Delyan Dosev — dosev-ai/chatgpt-skills`.

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

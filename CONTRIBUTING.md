# Contributing

## Scope

This repository accepts reviewed public projections of skills whose canonical source is maintained in `deldos/skills`.

Do not open a substantive public-only skill change unless a governed exception explains why the canonical source is unaffected.

## Required contribution packet

A skill pull request must include:

- public skill ID and version;
- canonical repository, path, version, and source merge commit;
- canonical source pull request and final reviewed HEAD;
- visibility or public-derivative decision;
- sanitization and connector-abstraction summary;
- license and attribution result;
- validation and test evidence;
- clean-room installation or invocation plan;
- known residuals.

## Review rules

- Use pull requests; do not commit substantive changes directly to `main`.
- Keep each skill release bounded and independently reviewable.
- Disposition every substantive review finding.
- Require exact-final-HEAD review for public/private boundaries, workflow logic, security, secrets, or canonical governance changes.
- Do not merge while required checks, threads, licensing, source lineage, or release evidence are incomplete.

## Defects

When a defect applies to the canonical skill, repair it in `deldos/skills` first and re-promote the reviewed result. A public-only defect may be repaired here only when the public transformation itself is the sole cause and that boundary is documented.

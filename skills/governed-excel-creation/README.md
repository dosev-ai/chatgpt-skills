# Governed Excel Creation

Create and maintain professional Excel workbooks with a portable native ChatGPT core, explicit workbook contracts, validation evidence, and safe continuation across sessions.

## What it does

`governed-excel-creation` guides new workbook creation, existing-workbook repair and reformatting, formulas and structured tables, controlled inputs, workbook documentation, `_MCP_META` metadata, repeatable workbook-local workflows, validation, render review, rollback evidence, and bounded connected-source extensions when a suitable connector is available.

## Why it exists

Spreadsheet work often mixes business logic, presentation, hidden assumptions, and manual edits. A reusable governed workflow makes intended changes explicit, preserves undeclared content, separates observed evidence from assumptions, and leaves enough metadata for another reviewer or session to understand what was done.

## Benefits

- Works without a private connector for normal workbook tasks.
- Makes substantive workbooks self-describing through a visible `README` sheet and normalized `_MCP_META` tables.
- Separates planning, mutation, validation, visual review, and distribution readiness instead of treating a saved file as proof of quality.
- Supports bounded modification of existing workbooks with baseline fingerprints and delta checks.
- Supports workbook-local workflows, checklists, run history, and evidence without requiring an external orchestration system.
- Reports recalculation and other environment-dependent capabilities conservatively when they cannot be verified.

## When to use it

Use the skill when ChatGPT needs to create, extend, repair, reformat, inspect, document, or validate an Excel workbook and the result should be maintainable rather than a one-off dump.

Representative requests:

- “Create a driver-based budget workbook with formulas, controlled inputs, a README, and validation evidence.”
- “Inspect this inherited workbook, preserve its design, and add metadata so another session can safely continue the work.”
- “Extend this documented workbook with a new scenario while preserving undeclared formulas and layout.”

## How it works

1. Classify the workbook and lock the target or baseline.
2. Capture requirements and plan bounded workbook changes.
3. Apply changes with native spreadsheet tooling.
4. Validate metadata, formulas, structure, declared deltas, and limitations.
5. Render-review affected workbook surfaces and return evidence, output location, and rollback information.

## Installation

The reviewed public source is published in this directory. An installable `skill.zip` has been built and validated from the same source, but binary publication remains a separate packaging-only gate; do not treat the repository source as evidence that the ZIP is already published. When the package is added, verify its SHA-256 against the release-evidence record before uploading it as a ChatGPT skill.

## Limitations

The skill does not prove native Excel recalculation unless a real native Excel execution supplied that evidence. It does not make business acceptance decisions automatically, infer missing business meaning, or promote contextual data into authoritative truth. Connected systems are optional and connector-specific retrieval logic is outside the portable public core. Environment-specific capabilities such as native Excel automation, pivots, external connections, or advanced fidelity checks may be unavailable.

## Canonical lineage

- Canonical repository: `deldos/skills`
- Canonical path: `skills/governed-excel-creation`
- Canonical version: `1.1.0`
- Canonical source PR: `#57`
- Canonical final PR HEAD: `6380edaf538bc4ec4d7de2666c90f0eff1ab759c`
- Canonical merge commit: `1b98d30f0edd564df165a73b4772505cf94258c1`
- Canonical content-preparation PR: `#54`

## Release status

- Public release state: `public-pr-open`
- Public pull request: `#6`
- Artifact status: `none`
- Clean-room verification: `PUBLIC PR OPEN: the 40-file public-safe projection validates with skill-creator, passes public-safety scanning and Python compilation, and passes representative connector-free workbook metadata/context/workflow preflight. Exact-final-HEAD public review, required repository checks, merge, merged-tree verification, and the separate installable ZIP publication gate remain pending.`
- Known residuals: `Require Public Skill Validation, accepted exact-final-HEAD automated review, and Bot Comment Closure Rate PASS before merging public PR 6.; Verify the merged public source tree before advancing beyond public-merged-verification-pending.; Publish the already-built installable skill.zip through the separate binary packaging gate; do not claim the ZIP is public until its checksum and merged artifact are verified.`

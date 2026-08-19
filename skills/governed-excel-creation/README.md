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
- Fails closed on malformed metadata and on legacy workbook conversions whose required features cannot be verified as preserved.

## When to use it

Use the skill when ChatGPT needs to create, extend, repair, reformat, inspect, document, or validate an OOXML Excel workbook and the result should be maintainable rather than a one-off dump. Legacy binary `.xls` inputs require feature-preserving controlled conversion before bundled deterministic OOXML helpers are used.

Representative requests:

- “Create a driver-based budget workbook with formulas, controlled inputs, a README, and validation evidence.”
- “Inspect this inherited workbook, preserve its design, and add metadata so another session can safely continue the work.”
- “Extend this documented workbook with a new scenario while preserving undeclared formulas and layout.”

## How it works

1. Classify the workbook and lock the target or baseline.
2. Capture requirements and plan bounded workbook changes.
3. Apply changes with native spreadsheet tooling.
4. Validate metadata, formulas, structure, workflow lineage, declared deltas, and limitations.
5. Render-review affected workbook surfaces and return evidence, output location, and rollback information.

## Installation

The public v1.1.1 source candidate is carried by pull request #6. No current v1.1.1 installable `skill.zip` is published yet; the prior local v1.1.0 package is superseded by the canonical repair and must not be treated as current. Binary packaging remains a separate governed gate after the repaired source is merged and verified.

## Limitations

The skill does not prove native Excel recalculation unless a real native Excel execution supplied that evidence. Bundled deterministic helpers inspect OOXML packages such as `.xlsx` and `.xlsm`; they do not parse legacy binary `.xls` directly. For legacy conversion, `.xlsx` is appropriate only when macro-free conversion is established; VBA/macros that are present or cannot be ruled out require a feature-preserving macro-enabled target such as `.xlsm`, and the workflow fails closed if preservation cannot be verified. Connected systems remain optional and connector-specific retrieval logic is outside the portable public core.

## Canonical lineage

- Canonical repository: `deldos/skills`
- Canonical path: `skills/governed-excel-creation`
- Canonical version: `1.1.1`
- Canonical source PR: `#58`
- Canonical final PR HEAD: `fe121804374939f6d07694f67fdc4d90b920c294`
- Canonical merge commit: `4e3c6a3e96712c6476dd9675cdd22264f3d1c049`

## Release status

- Public release state: `public-pr-open`
- Public pull request: `#6`
- Artifact status: `none`
- Clean-room verification: `PUBLIC PR REPAIR: v1.1.1 re-projects canonical PR 58 merge 4e3c6a3e96712c6476dd9675cdd22264f3d1c049, rejects cross-workflow run-step lineage, validates populated blank-ID rows, and preserves fail-closed macro-aware legacy .xls conversion. Exact-final-HEAD public validation/review, merge, merged-tree verification, and a new v1.1.1 installable ZIP publication gate remain pending.`
- Known residuals: `Require Public Skill Validation, accepted exact-final-HEAD automated review, and Bot Comment Closure Rate PASS on the repaired v1.1.1 public PR before merge.; Verify the merged public source tree before advancing beyond public-merged-verification-pending.; Build and publish a new v1.1.1 installable skill.zip through the separate binary packaging gate; the prior v1.1.0 local package is superseded and must not be published as current.`

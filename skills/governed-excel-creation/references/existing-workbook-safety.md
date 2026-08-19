# Existing Workbook Safety

## Before editing

- Resolve the canonical workbook and fingerprint it.
- Inventory sheets, tables, formulas, names, charts, validations, merged cells, hidden objects, print settings, and major styles.
- Render affected output sheets before structural or presentation changes.
- Read `_MCP_META` first when present and compare it with the actual workbook.
- Block ambiguous targets, stale plans, and mismatched active Excel sessions.

## Preservation contract

- Preserve unspecified values, formulas, comments, hyperlinks, names, and validations.
- Preserve unrelated styles, object placement, sheet visibility, print areas, and workbook structure.
- Preserve table names, ranges, filters, and styles unless explicitly included in the plan.
- Treat style components as partial updates; changing bold, fill, or alignment must not reset unrelated properties.
- Prefer bounded patches over broad workbook rewrites.
- Snapshot before material mutation and retain rollback evidence.

## Workbook without `_MCP_META`

1. Record observable structure and formulas.
2. Add draft metadata from verifiable facts.
3. Mark business meaning, ownership, lineage, and refresh instructions as `Unknown` when not evidenced.
4. Separate observed facts from inferred descriptions.
5. Add an onboarding change entry and validation rows.

## Workbook with `_MCP_META`

1. Read metadata and formatting declarations.
2. Identify stale, missing, or contradictory rows.
3. Build a target-locked plan for the bounded change.
4. Update workbook and metadata in the same operation.
5. Validate expected versus observed delta and preservation.
6. Report technical safety and review readiness separately.

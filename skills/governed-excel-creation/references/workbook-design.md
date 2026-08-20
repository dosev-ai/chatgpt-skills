# Workbook Design and Formula Conventions

## Sheet architecture

Prefer a clear flow:

1. `README` as the first visible sheet for standard and governed workbooks;
2. inputs or raw data;
3. mapping or assumptions;
4. calculations;
5. dashboard or outputs;
6. optional `MAINTENANCE` for detailed recurring procedures;
7. `_MCP_META` as the authoritative metadata sheet.

Follow [workbook-documentation.md](workbook-documentation.md) for documentation thresholds, maintenance layout, and metadata projection rules.

Do not mix editable inputs and protected calculations without clear visual and metadata distinction.

## Naming

- Use concise sheet names within Excel limits.
- Use unique, descriptive table and named-range identifiers.
- Use stable field names with consistent case and separators.
- Keep business labels readable and technical identifiers in metadata.

## Formula discipline

- Use formulas for derived totals, variances, shares, statuses, and KPIs.
- Reference assumptions instead of embedding unexplained constants.
- Use absolute references for fixed assumptions and relative references for row logic.
- Prefer widely compatible functions unless the user requires newer Excel features.
- Document material logic in `tbl_meta_rules` and lineage in `tbl_meta_relationships`.
- Distinguish formula presence from recalculated cached values.

## Presentation baseline

- Provide a visible title and purpose on major output sheets.
- Keep README navigation, ownership, refresh, validation, and known-limit information synchronized with `_MCP_META`.
- Style headers consistently and freeze important headers.
- Apply correct date, currency, percentage, and integer formats.
- Keep widths bounded and wrap long descriptions.
- Use Excel Tables for structured data and filtering.
- Use data validation for controlled inputs.
- Use conditional formatting only when it carries operational meaning.
- Use bar or column charts for categorical comparisons and line charts for time series.
- Keep `_MCP_META` functional and readable rather than decorative.

## Minimal export exception

A one-off flat extract may omit `_MCP_META` only when it has no formulas, multi-sheet flow, expected continuation, governance, lineage, or onboarding value. State the exception in the delivery summary.

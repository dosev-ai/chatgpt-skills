# `_MCP_META` Contract

## Contents

- [Authority](#authority)
- [Required tables](#required-tables)
- [Optional tables](#optional-tables)
- [Normalization rules](#normalization-rules)

## Authority

Use normalized Excel Tables on `_MCP_META` as the authoritative workbook metadata source. Generate JSON only for interoperability and always derive it from these tables. Never maintain a parallel JSON truth manually.

## Required tables

### `tbl_meta_workbook`

| Column | Meaning |
|---|---|
| Key | Stable metadata key |
| Value | Current value |
| Description | Meaning and usage |
| Required | Yes/No |

Include workbook purpose, audience, schema version, created/updated dates, authoritative metadata declaration, and refresh or calculation notes.

### `tbl_meta_sheets`

| Column | Meaning |
|---|---|
| Sheet_ID | Stable identifier |
| Sheet_Name | Exact worksheet name |
| Role | Documentation, Maintenance, Input, Raw, Mapping, Calculation, Output, Dashboard, or Metadata |
| Description | Business purpose |
| Grain | Row-level grain or `N/A` |
| Editable | Yes/No |
| Primary_Output | Yes/No |

### `tbl_meta_fields`

| Column | Meaning |
|---|---|
| Field_ID | Stable identifier |
| Sheet_Name | Exact worksheet name |
| Table_Name | Excel Table name or blank |
| Field_Name | Column or field label |
| Data_Type | Text, Integer, Decimal, Currency, Percentage, Date, Boolean, Formula, or Unknown |
| Number_Format | Excel number format or blank |
| Description | Business meaning |
| Source | Input, formula, source object, or Unknown |
| Formula_or_Rule | Formula pattern, rule ID, or blank |
| Editable | Yes/No |
| Required | Yes/No |

### `tbl_meta_rules`

| Column | Meaning |
|---|---|
| Rule_ID | Stable identifier |
| Rule_Name | Short name |
| Output_Object | Target field, range, KPI, validation, or format region |
| Business_Rule | Human-readable logic |
| Implementation | Formula, validation, conditional-format, or process note |
| Severity | Info, Warning, Error, or Critical |

### `tbl_meta_relationships`

| Column | Meaning |
|---|---|
| Relationship_ID | Stable identifier |
| From_Object | Upstream sheet, table, field, range, or external source |
| To_Object | Downstream workbook object |
| Relationship_Type | Feeds, Maps, Calculates, Aggregates, Validates, Formats, or References |
| Description | Bounded lineage note |

### `tbl_meta_validations`

| Column | Meaning |
|---|---|
| Validation_ID | Stable identifier |
| Scope | Workbook object being tested |
| Validation_Type | Structure, Formula, Metadata, Preservation, Input, Visual, Delta, or Readiness |
| Expected_Result | Testable outcome |
| Status | PASS, FAIL, NOT_RUN, or NOT_APPLICABLE |
| Evidence | Inspection, render, script result, plan/snapshot ID, or note |

### `tbl_meta_changes`

| Column | Meaning |
|---|---|
| Change_ID | Stable sequential identifier |
| Changed_At | ISO date or timestamp |
| Changed_By | ChatGPT, user, process, or named operator |
| Change_Type | Create, Update, Repair, Reformat, Onboard, Validate, or Rollback |
| Object | Affected workbook object |
| Description | Bounded change summary including plan/snapshot references when applicable |

## Optional tables

- `tbl_meta_requirements`: reusable business and acceptance requirements; see [planning-and-specs.md](planning-and-specs.md).
- `tbl_meta_maintenance`: ordered refresh, update, validation, publishing, troubleshooting, and rollback procedures; see [workbook-documentation.md](workbook-documentation.md).
- `tbl_meta_workflows`, `tbl_meta_workflow_sources`, `tbl_meta_workflow_inputs`, `tbl_meta_workflow_steps`, `tbl_meta_workflow_outputs`, `tbl_meta_workflow_runs`, and `tbl_meta_workflow_run_steps`: repeatable connected-source workflow definition and execution evidence; see [workflow-metadata-contract.md](workflow-metadata-contract.md).
- `tbl_meta_styles`, `tbl_meta_style_properties`, `tbl_meta_format_regions`, and `tbl_meta_layout`: repeatable formatting contract; see [formatting-metadata.md](formatting-metadata.md).

## Human-facing documentation projection

Use `README` and optional `MAINTENANCE` sheets as user-facing projections of authoritative metadata. See [workbook-documentation.md](workbook-documentation.md). Record those sheets in `tbl_meta_sheets` with role `Documentation` or `Maintenance`. Do not maintain conflicting values manually in the projection and metadata tables.

## Normalization rules

- Store one fact, requirement, relationship, validation, or change per row.
- Use exact workbook object names and stable IDs.
- Keep relationships normalized rather than nesting lineage JSON.
- Use `Unknown` rather than guessed meaning.
- Allow small JSON parameter fields only when a rule genuinely requires nested parameters.
- Keep the sheet readable: clear section titles, filters, frozen headers, wrapped descriptions, and practical widths.

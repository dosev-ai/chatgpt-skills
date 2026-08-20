# Requirements, Typed Specifications, Plans, and Approval

## Requirements table

Use optional `tbl_meta_requirements` for reusable workbook intent.

| Column | Meaning |
|---|---|
| Requirement_ID | Stable identifier such as `REQ-001` |
| Requirement_Type | Business, Data, Formula, Presentation, Control, Preservation, or Evidence |
| Audience | Intended user or reviewer |
| Business_Purpose | Outcome or decision supported |
| Target_Object | Workbook, sheet, table, range, field, chart, or rule |
| Requirement | Concise requirement statement |
| Acceptance_Criterion | Testable pass condition |
| Priority | Critical, High, Medium, or Low |
| Status | Proposed, Approved, Implemented, Deferred, or Rejected |

Store one requirement per row. Keep unverified intent as `Proposed` or `Unknown`; do not invent approval.

## Typed specification families

Use the smallest relevant set:

- `WorkbookPlanSpec`: overall purpose, target identity, constraints, and operation order;
- `SheetSpec`: sheet role, visibility, position, grain, and navigation;
- `RegionSpec`: target range and semantic role;
- `StyleSpec`: declared style properties and inheritance;
- `TableSpec`: table identity, range, columns, style, and filtering behavior;
- `FormulaSpec`: target, formula pattern, dependencies, and expected result class;
- `ChartSpec`: chart type, source data, title, axes, placement, and audience purpose;
- `ValidationSpec`: input control, allowed values, and error behavior;
- `LayoutSpec`: widths, heights, panes, zoom, gridlines, and print area;
- `ProtectionSpec`: locked/unlocked regions and protection expectations;
- `PrintSpec`: page setup, scaling, headers, and export expectations.

Do not use arbitrary operation dictionaries when a typed specification can define the contract more precisely.

## Versioned change plan

A material plan should contain:

- `plan_id`;
- `plan_version`;
- `plan_hash`;
- source workbook identity and fingerprint;
- metadata schema version;
- requirement IDs addressed;
- ordered typed operations;
- prerequisites and blockers;
- exact affected objects;
- predicted structural, formula, data, and formatting delta;
- explicit preservation set;
- validation and render checks;
- rollback strategy and snapshot expectation;
- idempotency expectation.

For any intended OOXML change that is not directly attributable to a worksheet XML part, declare the exact package path in `target.part` or `target.parts` (for example, `xl/styles.xml`, `xl/workbook.xml`, or a worksheet relationship part). Undeclared non-sheet package drift is blocking; only timestamp metadata and calculation-chain churn are treated as volatile.

The detailed plan is a generated machine artifact. Record only stable identifiers, summary, plan hash, result, and evidence in `tbl_meta_changes` and `tbl_meta_validations`.

## Preview contract

Before material mutation, show:

- exact sheets, ranges, tables, names, charts, rules, dimensions, and metadata rows affected;
- values, formulas, formats, or objects that may be replaced;
- objects explicitly preserved;
- new or removed structures;
- validation and rollback steps;
- known limitations.

For reformatting, separate static styles, conditional rules, and layout operations.

## Approval contract

Approval must bind to:

- exact plan ID and hash;
- exact source fingerprint;
- exact target identity;
- exact affected-object set.

Reject as stale when the workbook, metadata, plan, or target set changed. A stale or rejected plan must produce no workbook mutation.

## Example operation

```json
{
  "operation": "apply_region_style",
  "target": {
    "sheet": "Summary",
    "address": "A5:H5",
    "parts": ["xl/styles.xml"]
  },
  "style_id": "section_header",
  "preserve": ["values", "formulas", "comments", "hyperlinks"]
}

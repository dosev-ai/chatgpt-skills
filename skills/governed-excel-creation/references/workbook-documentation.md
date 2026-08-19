# Workbook Documentation and Maintenance Surface

## Purpose

Separate the human onboarding surface from the machine-authoritative metadata layer:

- `README` is the first visible sheet and explains how to use, refresh, review, and maintain the workbook.
- `_MCP_META` remains the authoritative normalized source for workbook purpose, structure, rules, lineage, validations, changes, and maintenance definitions.
- `MAINTENANCE` is optional and is used only when recurring procedures are too detailed for the README sheet.

Do not maintain conflicting facts manually across these sheets. Treat README and MAINTENANCE as user-facing projections of `_MCP_META` plus intentionally authored guidance.

## When to create documentation sheets

| Workbook tier | Documentation rule |
|---|---|
| Minimal flat export | Omit README unless the user requests instructions or the export has non-obvious use constraints. |
| Standard business workbook | Create `README` as the first visible sheet. Keep maintenance guidance in a compact section on the same sheet. |
| Governed or recurring operational workbook | Create `README` first. Add `MAINTENANCE` when procedures are multi-step, scheduled, role-dependent, tool-dependent, or require troubleshooting and evidence. |
| Existing workbook onboarding | Preserve an existing documentation sheet when adequate. Otherwise add `README` without renaming unrelated sheets. |

Use `START_HERE` only when an established workbook convention requires it. Default to `README` for consistency.

## README layout

Place a compact maintenance-status panel at the top, followed by workbook guidance.

### Maintenance-status panel

Include:

- workbook name and version;
- purpose and primary audience;
- owner and maintainer role;
- last updated date;
- refresh frequency or trigger;
- last validation result and date;
- calculation or recalculation requirement;
- known limitations or open warnings;
- hyperlinks to primary outputs, input sheets, `MAINTENANCE` when present, and `_MCP_META`.

### Guidance sections

Include only sections relevant to the workbook:

1. What this workbook does.
2. Who should use it and which decisions it supports.
3. Where users may enter or update data.
4. Key outputs and navigation links.
5. Refresh and calculation sequence.
6. Validation checks before distribution.
7. Known limitations and unsupported uses.
8. Change-history and metadata links.

Avoid technical implementation detail that belongs in `_MCP_META`.

## Linking README to metadata

Prefer formulas or generated values for metadata-backed facts. Use structured references where practical. For broad Excel compatibility, prefer `INDEX` and `MATCH` over newer-only functions when a formula projection is needed.

Examples of metadata-backed README fields:

- purpose, audience, owner, maintainer, version, last updated, refresh frequency, calculation notes, and known limitations from `tbl_meta_workbook`;
- navigation and sheet descriptions from `tbl_meta_sheets`;
- current validation status from `tbl_meta_validations`;
- latest material changes from `tbl_meta_changes`;
- recurring procedures from `tbl_meta_maintenance` when present.

Internal hyperlinks may point to exact sheets, named ranges, tables, or the relevant section on `_MCP_META`.

Do not let a user-facing formula silently become the authority. Update the source metadata row, then recalculate or regenerate the README projection.

## Optional MAINTENANCE sheet

Create a separate `MAINTENANCE` sheet when the workbook needs more than a compact README section. Present procedures in execution order with:

- trigger or frequency;
- responsible role;
- required source or tool;
- target workbook object;
- exact procedure;
- validation check;
- evidence or completion note;
- troubleshooting and rollback guidance.

Keep executable procedures synchronized with `tbl_meta_maintenance`. Put detailed rationale and lineage in `_MCP_META`, not in duplicated prose.

## Maintenance metadata

Use optional table `tbl_meta_maintenance` on `_MCP_META`:

| Column | Meaning |
|---|---|
| Step_ID | Stable identifier |
| Sequence | Integer execution order |
| Maintenance_Type | Refresh, Update, Reconcile, Validate, Publish, Archive, Repair, or Other |
| Trigger_or_Frequency | Event, schedule, or condition |
| Responsible_Role | Owner, maintainer, analyst, reviewer, process, or Unknown |
| Required_Tool | Excel, native ChatGPT, external system, or blank |
| Target_Object | Workbook, sheet, table, range, source, or output |
| Procedure | Bounded maintenance instruction |
| Validation_ID | Related row in `tbl_meta_validations` or blank |
| Evidence_Required | Required evidence or `None` |
| Notes | Limitations, troubleshooting, or rollback note |

Store one procedure step per row. Use `Unknown` for unverified ownership or operating assumptions.

## Documentation validation

Before delivery:

- confirm README is the first visible sheet for standard and governed workbooks;
- verify all internal hyperlinks resolve;
- compare displayed README facts with their metadata sources;
- verify maintenance steps are ordered and actionable;
- confirm the documentation does not expose secrets, local credentials, or sensitive paths;
- render README and MAINTENANCE and inspect wrapping, hierarchy, widths, and print readability;
- record documentation consistency in `tbl_meta_validations`;
- record documentation creation or revision in `tbl_meta_changes`.

Documentation completeness supports `ready_for_review`; it does not by itself establish `ready_to_distribute`.


## Workflow-enabled documentation

When the workbook is intended for repeatable execution or refresh, add human-facing projections described in [workflow-enabled-workbooks.md](workflow-enabled-workbooks.md):

- `WORKFLOW` for the definition summary and latest execution checklist;
- `RUN_HISTORY` for one row per workflow execution;
- `EVIDENCE` for source, reconciliation, validation, and artifact evidence;
- `CHANGE_LOG` for workbook design and contract changes from `tbl_meta_changes`.

Keep run history and change history separate. A routine refresh appends a run record but does not create a workbook change unless design, logic, structure, metadata, or workflow contract changed.

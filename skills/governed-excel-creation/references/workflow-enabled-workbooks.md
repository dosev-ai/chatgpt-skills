# Workflow-Enabled Workbooks

## Purpose

Use this reference when an Excel workbook is generated or refreshed through a repeatable workflow that retrieves data or context from connected systems, transforms it, writes governed workbook regions, validates the result, and records execution evidence.

Keep four responsibilities separate:

- the connected source owns its authoritative records;
- the workflow definition owns orchestration, step order, gates, and source bindings;
- this skill owns workbook design, mutation, validation, and documentation;
- the workbook contains human-readable workflow projections and run evidence, but is not a second workflow runtime or operational source of truth.

A project dashboard is one example. The same contract applies to finance packs, procurement analyses, operating reports, compliance trackers, portfolio reviews, meeting packs, and other repeatable workbook products.

## Load with

- [workflow-metadata-contract.md](workflow-metadata-contract.md) for normalized metadata tables;
- [connector-source-contract.md](connector-source-contract.md) for connector-neutral source packets and manifests;
- [workflow-run-evidence.md](workflow-run-evidence.md) for checklist, run history, evidence, and change-log rules;
- [metadata-contract.md](metadata-contract.md) for the base workbook contract;
- [validation-and-evidence.md](validation-and-evidence.md) for readiness gates;
- [deterministic-scripts.md](deterministic-scripts.md) when code execution is available.

## Source authority

Declare every source with an authority role:

- `Authoritative`: may define workbook facts for its governed domain;
- `Contextual`: may support narrative, rationale, or interpretation but cannot override an authoritative source;
- `Derived`: produced from authoritative or contextual inputs through a declared transform;
- `Manual`: intentionally entered in a controlled workbook region.

Examples:

- A workflow or project system may be authoritative for its governed operational records.
- A document repository may be contextual for supporting documents, rationale, and long-form notes.
- A finance ERP may be authoritative for posted transactions.
- Excel may be authoritative only for explicitly declared manual inputs, assumptions, or approvals.

Use `Unknown` when authority cannot be verified. Never let a workbook refresh silently promote contextual or inferred data into authoritative truth.

## Workflow lifecycle

1. Select the workflow definition and version.
2. Validate source bindings, required connectors, input parameters, permissions, and sensitivity rules.
3. Lock the workbook target, workflow definition hash, input fingerprint, and source snapshot.
4. Retrieve required sources and label optional-source failures explicitly.
5. Normalize each connector response into `source-packet-v1`, validate it, and merge multiple packets into `source-manifest-v1`.
6. Map normalized source records into typed workflow inputs without changing their authority role.
7. Produce or refresh only declared workbook output regions.
8. Preserve manual and formula-managed areas according to metadata.
9. Recalculate when required and actually available.
10. Validate source reconciliation, packet/manifest fingerprints, formulas, metadata, output regions, and undeclared drift.
11. Render-review user-facing sheets.
12. Append workflow run and step evidence.
13. Append a workbook change only when workbook design, logic, structure, metadata, or workflow contract changed.
14. Return separate technical, review, distribution, and rollback states.

## Workbook surfaces

Use these projections when relevant:

| Sheet | Purpose |
|---|---|
| `README` | Human entry point, current workflow status, ownership, limitations, and navigation. |
| `WORKFLOW` | Workflow definition summary and current or latest execution checklist. |
| `PARAMETERS` or `ADMIN` | Controlled non-secret workflow inputs when user-editable parameters are required. |
| Business sheets | Inputs, calculations, dashboards, reports, and other workflow outputs. |
| `EVIDENCE` | Source snapshots, reconciliations, validation results, and artifact references. |
| `RUN_HISTORY` | One row per workflow execution. |
| `CHANGE_LOG` | Workbook design and contract changes projected from `tbl_meta_changes`. |
| `_MCP_META` | Authoritative normalized workbook, workflow, lineage, and evidence metadata. |

Do not create every sheet mechanically. `WORKFLOW`, `RUN_HISTORY`, and the workflow metadata tables are required only when the workbook is intended to be executed or refreshed repeatedly. `EVIDENCE` is strongly recommended for governed connected-source workflows.

## Refresh and regenerate modes

### Refresh

Use when the workbook contract is unchanged and only source data or run evidence changes. Update declared generated regions and append run records. Preserve manual areas and stable workbook design.

### Regenerate

Use when the workbook structure, workflow version, formulas, layout, metadata contract, or output model changed materially. Create a new workbook version or perform a fully planned rework with rollback evidence.

Classify output regions as:

- `generated_replace`
- `generated_append`
- `manual_preserve`
- `formula_managed`
- `system_metadata`
- `evidence_append_only`

A routine refresh is a workflow run, not automatically a workbook change. Record a workbook change only when design or contract changed.

## Workbook-side controls

A workbook may expose workflow parameters or refresh affordances, but it must not bypass the governed runtime or connector controls. Use allowlisted project or workflow choices, explicit confirmation, safe parameter validation, and a copy-request or approved-trigger pattern when direct execution from Excel is unsafe.

Do not store secrets, bearer tokens, connector credentials, or local privileged paths in workbook cells or metadata.

## Cross-skill extraction rule

Keep this contract in the Excel skill during MVP and early UAT. Extract a cross-skill workflow helper only after:

- at least two artifact skills use the same workflow and evidence model;
- at least three workflows have repeated successful runs;
- the metadata schema has remained stable;
- source authority, approval, and failure semantics are proven;
- duplication across specialist skills is material.

The future helper should own workflow discovery, parameter validation, execution state, approvals, and evidence routing. Excel, Word, PowerPoint, and other specialist skills must continue to own their artifact mutation and validation logic.

# Governed Workbook Authoring Lifecycle

## Contents

- [Purpose](#purpose)
- [Workflow tiers](#workflow-tiers)
- [Lifecycle](#lifecycle)

## Purpose

Apply a report-authoring control plane to Excel work: intent -> target lock -> baseline audit -> design plan -> preview -> approval -> typed apply -> observed-delta validation -> render review -> handoff.

## Workflow tiers

### Minimal export

Use for one-off flat data with no formulas, multi-sheet logic, continuation, governance, or lineage value. Metadata and approval may be omitted. Still validate structure, errors, and output readability.

### Standard business workbook

Use a first-sheet README, core metadata, requirements, typed specifications, formula and structure validation, and render review. A lightweight preview is sufficient for new workbook creation when no existing artifact is at risk.

### Governed existing-workbook rework

Use the full lifecycle: target lock, baseline snapshot, technical and usability audits, versioned plan, impact preview, explicit approval for material changes, expected-versus-observed delta, rollback evidence, and distinct readiness states.

## Lifecycle

### 1. Discover and lock the target

Capture:

- canonical workbook path or artifact identity;
- workbook fingerprint or content hash;
- metadata schema version;
- sheet, table, named-range, and protection inventory;
- open-session or active-workbook state when relevant;
- baseline snapshot ID when available.

Block when multiple plausible targets exist, the workbook changed since planning, or the active Excel session points to a different workbook.

### 2. Run two baseline audits

**Technical integrity**

- package opens and core XML is valid;
- formulas and references are structurally valid;
- tables, filters, names, validations, charts, and metadata resolve;
- external links and calculation state are identified;
- metadata agrees with the physical workbook.

**Business usability**

- purpose and audience are clear;
- inputs, calculations, and outputs are distinguishable;
- visual hierarchy and number formats are coherent;
- assumptions, totals, warnings, and navigation are understandable;
- output and print/export areas are readable.

Do not merge these into one result. A workbook may be technically safe but not review-ready.

### 3. Capture intent and requirements

Record purpose, audience, decisions supported, inputs, outputs, grain, non-goals, acceptance criteria, preservation constraints, ownership, refresh expectations, and maintenance needs. Use `tbl_meta_requirements` for substantive reusable requirements and [workbook-documentation.md](workbook-documentation.md) for README and maintenance projections.

### 4. Compile typed specifications

Translate requirements into bounded object specifications such as workbook, sheet, region, table, formula, chart, validation, layout, protection, and print specifications. See [planning-and-specs.md](planning-and-specs.md).

### 5. Produce the plan and preview

Create a versioned plan containing the target fingerprint, typed operations, prerequisites, affected objects, predicted changes, preserved objects, validation checks, and rollback strategy. Preview exact sheets, ranges, objects, and properties that will change and explicitly state what remains unchanged.

### 6. Approve material changes

Bind approval to the plan ID, plan hash, source fingerprint, and affected-object set. Require a new preview when any of these change. Rejection produces no mutation.

Lightweight explicit user instruction may serve as approval for low-risk formatting-only changes. Structural, formula, data, protection, or deletion changes require the full gate.

### 7. Snapshot and apply

Validate every operation before mutation, snapshot the source, verify the target fingerprint again, apply all bounded changes in one in-memory session where possible, save once, and retain the rollback locator.

### 8. Validate observed delta

Compare the plan with the actual output:

- expected objects changed;
- undeclared objects did not change;
- preserved formulas, values, styles, and names remained stable;
- tables, validations, charts, and metadata still resolve;
- repeated application is idempotent where the plan claims idempotency.

### 9. Recalculate and render-review

Use native Excel recalculation only when required and available. Otherwise distinguish formula presence from cached-value refresh. Render README, affected output sheets, optional MAINTENANCE, and `_MCP_META`; inspect clipping, hierarchy, widths, hyperlinks, charts, totals, and usability.

### 10. Handoff

Return separate states:

- `safe_to_open`;
- `metadata_consistent`;
- `ready_for_review`;
- `ready_to_distribute`;
- `rollback_available`.

Also provide output path, validation summary, affected objects, engine used, unresolved limitations, rollback reference, and documentation status.

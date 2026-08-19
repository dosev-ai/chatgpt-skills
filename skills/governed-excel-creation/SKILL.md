---
name: governed-excel-creation
description: Create, extend, repair, reformat, and validate professional Excel workbooks with a connector-independent native ChatGPT core and optional generic connected-source extensions. Use for .xlsx or .xlsm work involving business-ready workbook generation, formulas, tables, charts, dashboards, controlled inputs, metadata-driven formatting, existing-workbook modification, workbook planning and design, preview-and-approval workflows, repeatable workbook-local workflows, workflow checklists and run history, metadata and lineage, user-facing README and maintenance documentation, render review, rollback evidence, or continuation by a later ChatGPT session. Legacy binary .xls inputs require feature-preserving controlled conversion to OOXML before bundled deterministic helpers are used. Default substantive workbooks to a self-describing `_MCP_META` sheet with authoritative normalized Excel Tables.
license: MIT
metadata:
  version: 1.1.1
  canonical_repository: deldos/skills
  canonical_path: skills/governed-excel-creation
---

# Governed Excel Creation

## Control plane

Use native spreadsheet artifact tooling as the default workbook engine. Apply a governed lifecycle around it: identify the target, understand intent, plan typed changes, preview impact, apply bounded operations, validate the observed delta, render-review, and deliver evidence. The portable core must work without private connectors or local Office automation.

## Operating modes

### Portable core — default

Use this mode for normal workbook creation, repair, reformatting, documentation, validation, and workbook-local workflows. Work from files, tables, values, or other inputs supplied in the conversation or available through the active artifact environment. Report unsupported or unverified capabilities as `Unknown`; do not invent an external dependency merely to complete the workbook.

### Connected-source extension — optional

Use a connected source only when the request materially depends on live external records and the required connector is available and authorized. Preserve each source's declared authority, normalize retrieved data before workbook mapping, and keep credentials outside the workbook and skill. Connector absence must never block the portable core.

## Route the task

Load only the references required for the current scope:

| Scope | Required references |
|---|---|
| New substantive workbook | [authoring-lifecycle.md](references/authoring-lifecycle.md), [planning-and-specs.md](references/planning-and-specs.md), [workbook-design.md](references/workbook-design.md), [workbook-documentation.md](references/workbook-documentation.md), [metadata-contract.md](references/metadata-contract.md), [validation-and-evidence.md](references/validation-and-evidence.md), [deterministic-scripts.md](references/deterministic-scripts.md) |
| Existing workbook modification or repair | [authoring-lifecycle.md](references/authoring-lifecycle.md), [existing-workbook-safety.md](references/existing-workbook-safety.md), [workbook-documentation.md](references/workbook-documentation.md), [metadata-contract.md](references/metadata-contract.md), [validation-and-evidence.md](references/validation-and-evidence.md), [deterministic-scripts.md](references/deterministic-scripts.md) |
| Metadata-driven reformatting | [formatting-metadata.md](references/formatting-metadata.md), [reformatting-execution.md](references/reformatting-execution.md), [validation-and-evidence.md](references/validation-and-evidence.md) |
| Workbook requirements, plan, preview, or approval | [planning-and-specs.md](references/planning-and-specs.md), [workbook-documentation.md](references/workbook-documentation.md), [deterministic-scripts.md](references/deterministic-scripts.md) |
| Dry runs, regression, or skill evaluation | [uat-and-dry-runs.md](references/uat-and-dry-runs.md), [deterministic-scripts.md](references/deterministic-scripts.md) |
| README, maintenance guidance, or workbook onboarding | [workbook-documentation.md](references/workbook-documentation.md), [metadata-contract.md](references/metadata-contract.md), [validation-and-evidence.md](references/validation-and-evidence.md) |
| Workbook-local repeatable workflow, checklist, run history, or workflow evidence | [workbook-local-workflows.md](references/workbook-local-workflows.md), [workflow-metadata-contract.md](references/workflow-metadata-contract.md), [workflow-run-evidence.md](references/workflow-run-evidence.md), [metadata-contract.md](references/metadata-contract.md), [validation-and-evidence.md](references/validation-and-evidence.md), [deterministic-scripts.md](references/deterministic-scripts.md) |
| Generic connected-source workflow or refresh | [workflow-enabled-workbooks.md](references/workflow-enabled-workbooks.md), [workflow-metadata-contract.md](references/workflow-metadata-contract.md), [workflow-run-evidence.md](references/workflow-run-evidence.md), [connector-source-contract.md](references/connector-source-contract.md), [connector-extension-guide.md](references/connector-extension-guide.md), [metadata-contract.md](references/metadata-contract.md), [validation-and-evidence.md](references/validation-and-evidence.md), [deterministic-scripts.md](references/deterministic-scripts.md) |
| Minimal flat export | [workbook-design.md](references/workbook-design.md), [validation-and-evidence.md](references/validation-and-evidence.md) |

## Universal rules

- Treat `_MCP_META` normalized Excel Tables as authoritative for substantive workbook metadata.
- Create a user-facing `README` as the first visible sheet for standard and governed workbooks; project metadata-backed facts from `_MCP_META` rather than duplicating truth.
- Read `_MCP_META` before modifying a documented workbook, then compare declarations with the physical workbook.
- Use `Unknown` for unverified meaning, ownership, lineage, or authority.
- Preserve undeclared formulas, values, formats, objects, names, and workbook structure.
- Prefer formulas, structured tables, named objects, and controlled inputs over painted values.
- Separate technical integrity from business usability and distribution readiness.
- Do not claim native Excel recalculation unless it was actually performed.
- Keep plans and JSON manifests derived from authoritative metadata; do not maintain parallel truth manually.
- For workbook-local workflows, keep the workflow definition in `_MCP_META` authoritative for orchestration. Excel may be authoritative only for explicitly declared workbook-local inputs, assumptions, checkpoints, or approvals.
- For connected-source workflows, preserve the declared authority of each source and keep Excel authoritative only for declared workbook-local inputs or approvals.
- Normalize connector responses into fingerprinted source packets only when connected sources are actually used. In workbook-local mode, use workbook/input fingerprints and local evidence instead of synthetic connector packets.
- Keep workflow run history separate from workbook design and contract changes.
- Legacy binary `.xls` workbooks are not OOXML packages. Preserve the original. Before conversion, determine whether VBA/macros or other features that `.xlsx` cannot preserve are present or cannot be ruled out. Use a feature-preserving macro-enabled OOXML target such as `.xlsm` when macros are present or potentially present, and verify the required features survived conversion; use `.xlsx` only when macro-free conversion is established. If feature-preserving conversion cannot be verified, do not establish the converted workbook as a governed target or baseline and do not invoke the bundled deterministic OOXML helpers; report deterministic inspection as blocked or `Unknown` instead.
- Save once after a validated in-memory mutation sequence whenever possible.

## Default lifecycle

1. Classify the workbook tier: minimal export, standard business workbook, or governed existing-workbook rework.
2. Discover and lock the canonical target and baseline fingerprint.
3. Audit technical integrity and business usability separately.
4. Capture requirements and compile typed workbook specifications.
5. Produce a versioned change plan and exact impact preview.
6. Bind approval to the unchanged plan and source fingerprint when the change is material.
7. Snapshot, revalidate, apply bounded operations, and save once.
8. Compare expected versus observed changes and detect undeclared drift.
9. Recalculate when required and available, render affected sheets, and update metadata evidence.
10. Return distinct readiness states, limitations, output path, and rollback evidence.

Use the lighter path defined in [authoring-lifecycle.md](references/authoring-lifecycle.md) when full approval ceremony would exceed the risk or value of the change.

## Deterministic automation

Use [deterministic-scripts.md](references/deterministic-scripts.md) when code execution is available. Prefer the bundled portable scripts for repeatable workbook context extraction, plan hashing, stale-target rejection, metadata validation, delta comparison, workflow-run envelopes, generic source-packet validation/merge, and readiness evidence. Bundled workbook helpers operate on OOXML workbooks such as `.xlsx` and `.xlsm`; apply the feature-preserving legacy `.xls` conversion gate above before invoking them. The scripts inspect workbooks or normalize already-exported generic evidence; they do not call networks or edit workbook business content.

# Workbook-Local Workflows

## Purpose

Use this reference when a repeatable Excel workflow can run entirely from the workbook plus files, tables, values, or instructions supplied in the active artifact environment. This is the connector-free workflow path for the portable core. It must not require a private connector, native desktop automation, or any other external source merely to define, execute, validate, or evidence the workflow.

Use [workflow-enabled-workbooks.md](workflow-enabled-workbooks.md) instead when live connected sources are actually required.

## Load with

- [workflow-metadata-contract.md](workflow-metadata-contract.md) for normalized workflow definition, source, step, output, and run tables;
- [workflow-run-evidence.md](workflow-run-evidence.md) for checklist and run-history evidence;
- [metadata-contract.md](metadata-contract.md) for the base workbook contract;
- [validation-and-evidence.md](validation-and-evidence.md) for technical and review gates;
- [deterministic-scripts.md](deterministic-scripts.md) when code execution is available.

Do not load or require [connector-source-contract.md](connector-source-contract.md) unless the workflow later adds a real external source.

## Authority model

Keep authority explicit without inventing a connected system:

- `_MCP_META` owns the declared workbook workflow definition and orchestration contract.
- Excel may be authoritative for explicitly declared workbook-local inputs, assumptions, checkpoints, or approvals.
- Local workbook tables or supplied files may be `Authoritative`, `Contextual`, `Derived`, `Manual`, or `Unknown` according to the declared workflow scope.
- Formula results are `Derived` unless another declared rule says otherwise.
- User-supplied values are `Manual` unless a different authority role is explicitly evidenced.

Use `Unknown` when authority, ownership, freshness, or lineage cannot be verified. Connector absence is not itself an error in this mode.

## Workbook-local lifecycle

1. Select or define the workbook workflow and version in `_MCP_META`.
2. Lock the workbook target, baseline fingerprint, workflow definition hash, and non-secret input fingerprint.
3. Validate required workbook-local sources, manual inputs, ranges, tables, and preservation zones.
4. Map inputs into typed workflow parameters without fabricating external source identities.
5. Plan the bounded workbook operations and any required confirmation, approval, validation, or review checkpoints.
6. Apply only declared output-region changes while preserving manual and formula-managed areas.
7. Recalculate only when a real calculation engine is available; otherwise report recalculation as unverified.
8. Validate metadata, formulas, target objects, expected-versus-observed delta, and undeclared drift.
9. Render-review affected user-facing sheets.
10. Append one workflow run row and its step evidence.
11. Append a workbook change only when design, logic, structure, metadata, or workflow contract changed materially.
12. Return separate workflow-completion, review-readiness, distribution-readiness, limitation, and rollback states.

A workbook-local run does not require `source-packet-v1` or `source-manifest-v1`. Use workbook, file, table, or input fingerprints as the source/run evidence. If a real connector or external authoritative system enters scope, stop treating the run as purely workbook-local and switch to the connected-source workflow contract before retrieval or refresh.

## Workbook surfaces

Use only the surfaces the workflow needs:

| Sheet | Purpose |
|---|---|
| `README` | Human entry point, workflow purpose, ownership, limitations, and navigation. |
| `WORKFLOW` | Workflow summary, parameters, and current/latest execution checklist. |
| `PARAMETERS` or `ADMIN` | Controlled non-secret workbook-local inputs when needed. |
| Business sheets | Inputs, calculations, dashboards, reports, and outputs. |
| `RUN_HISTORY` | One row per workflow execution when recurrence matters. |
| `CHANGE_LOG` | Material workbook design or contract changes only. |
| `_MCP_META` | Authoritative normalized workbook and workflow metadata. |

`EVIDENCE` is optional for a workbook-local workflow. Add it when the user needs a durable validation or acceptance surface; do not create connector-style evidence rows merely because the sheet exists.

## Clean-room example

A connector-free recurring planning workbook may:

1. read controlled assumptions from `PARAMETERS`;
2. calculate outputs through formulas or declared transformations;
3. require a user confirmation checkpoint before finalizing a scenario;
4. validate expected tables, formulas, and ranges;
5. render-review the result;
6. append a `RUN_HISTORY` record with workbook/input/output fingerprints.

This path is complete without any external source packet. If the same workbook later refreshes ERP or API data, that refresh is a connected-source workflow and must use the connector/source authority contract for that portion of the run.

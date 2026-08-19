# Workflow Metadata Contract

## Purpose

Extend `_MCP_META` with normalized tables for repeatable workbook workflows, whether workbook-local or connected-source. These tables define durable workflow intent and record execution evidence. External WorkflowRuntime or connector definitions may remain canonical for executable orchestration in connected mode; for workbook-local workflows, the workflow definition may be represented by workbook metadata, a skill, prompt, or other local definition reference and no external runtime is required.

All tables in this reference are optional as a bundle. When any workflow table is present, include the complete core bundle unless a documented migration explicitly states otherwise.

## `tbl_meta_workflows`

One row per workbook workflow.

| Column | Meaning |
|---|---|
| Workflow_ID | Stable workflow identifier. |
| Workflow_Name | Human-readable name. |
| Workflow_Version | Contract or definition version. |
| Purpose | Business outcome produced by the workflow. |
| Trigger | Manual, scheduled, event-driven, or conditional trigger. |
| Owner_Role | Responsible business or operational role. |
| Execution_Mode | Refresh, Regenerate, Append, Validate, or Mixed. |
| Definition_Ref | Canonical workflow, skill, prompt, or runtime definition reference. |
| Source_of_Truth | Primary authority statement. |
| Active | Yes or No. |

## `tbl_meta_workflow_sources`

One row per connected or workbook-local source.

| Column | Meaning |
|---|---|
| Source_ID | Stable source identifier. |
| Workflow_ID | Parent workflow. |
| System | ERP, database, document store, file, workbook, API, or other system. |
| Authority_Role | Authoritative, Contextual, Derived, Manual, or Unknown. |
| Connector_or_Tool | Tool, MCP, governed query, API, file import, or manual surface. |
| Retrieval_Contract | Bounded operation, query, document selector, range, or resource reference. |
| Required | Yes or No. |
| Scope_or_Filter | Project, date window, tags, IDs, or other explicit scope. |
| Freshness_Rule | Maximum age, as-of rule, or `Unknown`. |
| Failure_Behavior | Stop, Warn, Skip, or Continue. |

## `tbl_meta_workflow_inputs`

One row per workflow parameter.

| Column | Meaning |
|---|---|
| Input_ID | Stable input identifier. |
| Workflow_ID | Parent workflow. |
| Input_Name | Parameter name. |
| Data_Type | Text, Integer, Decimal, Boolean, Date, DateTime, List, Object, or Unknown. |
| Required | Yes or No. |
| Default_Value | Non-secret default or blank. |
| Allowed_Values_or_Rule | Validation list, pattern, range, or rule reference. |
| Sensitive | Yes or No. |
| Description | Business and execution meaning. |

Never store secret input values in this table.

## `tbl_meta_workflow_steps`

One row per ordered workflow step.

| Column | Meaning |
|---|---|
| Step_ID | Stable step identifier. |
| Workflow_ID | Parent workflow. |
| Sequence | Positive execution order within the workflow. |
| Step_Type | Retrieve, Transform, Plan, Approve, Write, Recalculate, Validate, Review, Evidence, Publish, or Other. |
| Source_ID | Related source or blank. |
| Operation | Bounded operation or outcome. |
| Target_Object | Workflow output, workbook object, or evidence object. |
| Required | Yes or No. |
| Checkpoint_Type | None, Checkbox, Confirmation, Approval, Validation, or Review. |
| Validation_ID | Related `tbl_meta_validations` row or blank. |
| Evidence_Required | Yes or No. |
| Failure_Behavior | Stop, Warn, Skip, or Continue. |

A checkbox is an execution checkpoint, not formal approval. Approval requires approver identity, timestamp, definition or plan hash, and evidence.

## `tbl_meta_workflow_outputs`

One row per declared workbook or external output.

| Column | Meaning |
|---|---|
| Output_ID | Stable output identifier. |
| Workflow_ID | Parent workflow. |
| Output_Name | Human-readable output name. |
| Target_Sheet | Exact worksheet name or blank for an external artifact. |
| Target_Object | Table, range, chart, file, evidence bundle, or other object. |
| Update_Mode | generated_replace, generated_append, manual_preserve, formula_managed, system_metadata, or evidence_append_only. |
| Preserve_Manual_Areas | Yes or No. |
| Validation_ID | Related validation or blank. |
| Evidence_Required | Yes or No. |

## `tbl_meta_workflow_runs`

One row per workflow execution.

| Column | Meaning |
|---|---|
| Run_ID | Stable run identifier. |
| Workflow_ID | Executed workflow. |
| Workflow_Version | Executed version. |
| Started_At | ISO timestamp. |
| Completed_At | ISO timestamp or blank while running. |
| Status | PLANNED, RUNNING, COMPLETED, COMPLETED_WITH_WARNINGS, FAILED, CANCELLED, or ROLLED_BACK. |
| Source_Snapshot | As-of timestamp, snapshot ID, or bounded summary. |
| Input_Fingerprint | Hash of normalized non-secret inputs. |
| Output_Fingerprint | Post-run artifact fingerprint or evidence reference. |
| Plan_or_Definition_Hash | Approved definition or plan hash. |
| Validation_Status | PASS, FAIL, NOT_RUN, or NOT_APPLICABLE. |
| Evidence_Ref | Evidence bundle, workbook sheet, or run-report reference. |
| Executed_By | ChatGPT, user, process, or named operator. |

## `tbl_meta_workflow_run_steps`

One row per workflow step per run.

| Column | Meaning |
|---|---|
| Run_Step_ID | Stable row identifier. |
| Run_ID | Parent run. |
| Step_ID | Executed workflow step. |
| Checked | Yes or No. |
| Status | NOT_STARTED, RUNNING, COMPLETED, SKIPPED, WARNING, FAILED, or ROLLED_BACK. |
| Started_At | ISO timestamp or blank. |
| Completed_At | ISO timestamp or blank. |
| Result_Summary | Bounded non-sensitive outcome. |
| Evidence_Ref | Validation, source, render, or artifact evidence. |
| Error_or_Warning | Bounded failure or warning text. |

## Relationship rules

- Every workflow source, input, step, output, and run must reference an existing `Workflow_ID`.
- Every run-step row must reference an existing `Run_ID` and `Step_ID`.
- Step sequences must be unique and positive within a workflow.
- Validation references must exist in `tbl_meta_validations`.
- Output target sheets must exist unless the output is explicitly external.
- Required sources and required steps default to fail-closed behavior unless the workflow design states a justified alternative.
- `Sensitive=Yes` defines handling requirements; it does not authorize storing the sensitive value.
- Use `Unknown` for unverified freshness, owner, authority, or lineage.

## Visible projections

Project or regenerate these tables into:

- `WORKFLOW` for workflow summary and latest execution checklist;
- `RUN_HISTORY` for run-level history;
- `EVIDENCE` for source, reconciliation, validation, and artifact evidence;
- `CHANGE_LOG` for `tbl_meta_changes` only.

The workflow run log and workbook change log are different records and must remain separate.

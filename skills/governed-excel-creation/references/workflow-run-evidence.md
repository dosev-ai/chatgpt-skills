# Workflow Run, Checklist, and Change Evidence

## Execution checklist

Show the current or latest run on `WORKFLOW`. Include:

- workflow ID, version, purpose, definition reference, and execution mode;
- source snapshot and input fingerprint;
- run ID, status, start, completion, and executor;
- one row per workflow step with sequence, required flag, checkpoint type, checked state, status, result, and evidence.

Use a Boolean or `Yes`/`No` value as the authoritative checkpoint state. A visible `☐` or `☑` symbol may be generated as a projection. Do not rely on floating Form Controls, macros, or ActiveX objects as the default contract.

Checkpoint meanings:

- `Checkbox`: operator or workflow confirms the step occurred;
- `Confirmation`: explicit permission to continue;
- `Approval`: identified approver accepts an unchanged plan or definition hash;
- `Validation`: a test produced a result;
- `Review`: a human or defined reviewer examined the output.

A checked box alone never proves approval or acceptance.

## Run history

Project `tbl_meta_workflow_runs` onto `RUN_HISTORY`. Append rather than overwrite. Keep enough history to understand recurrence and detect failed or degraded runs.

For each run, show:

- run ID and workflow version;
- start and completion timestamps;
- status and validation result;
- source snapshot;
- input and output fingerprints or evidence references;
- executor and evidence location.

Use `COMPLETED_WITH_WARNINGS` when optional sources failed, freshness rules were exceeded, recalculation was unavailable, or other bounded limitations remain.

## Workbook change log

Project `tbl_meta_changes` onto `CHANGE_LOG`. Record only material workbook changes such as:

- creating or onboarding the workbook;
- adding, removing, or renaming sheets, tables, fields, formulas, charts, validations, or workflow definitions;
- changing metadata schemas, source bindings, refresh behavior, or preservation zones;
- repairing a defect;
- rolling back a material change.

Do not record a routine data refresh as a workbook design change unless it changed the workbook contract. The same execution may therefore create a run-history row without creating a change-log row.

Recommended change description content:

- workbook version before and after;
- change type and affected objects;
- reason and requirement reference;
- workflow, plan, or definition hash;
- source and output fingerprints where useful;
- validation and evidence references;
- changed-by identity.

## Evidence surface

Use `EVIDENCE` when the workflow depends on external or connected sources. Capture:

- source ID, system, authority role, retrieval operation, scope, snapshot, result, and row or object count;
- optional-source skips and warnings;
- normalization and reconciliation results;
- metadata, formula, structure, delta, render, and acceptance evidence;
- external artifact paths or IDs without exposing secrets;
- known limitations and next required gate.

## Readiness states

Return separately:

- `workflow_completed`: all required execution steps reached a terminal acceptable state;
- `safe_to_open`: the workbook package is structurally valid;
- `metadata_consistent`: workbook and workflow metadata passed validation;
- `ready_for_review`: user-facing output passed actual render and usability review;
- `ready_to_distribute`: required acceptance, freshness, recalculation, privacy, and evidence gates passed;
- `rollback_available`: a usable source snapshot, prior artifact, or rollback locator exists.

An exploratory MVP run may be `workflow_completed=true` and `ready_for_review=true` while `ready_to_distribute=false` because independent acceptance has not occurred.

## Failure handling

- Stop before workbook mutation when a required authoritative source is unavailable.
- Mark optional contextual-source failure as `SKIPPED` or `WARNING` according to the definition.
- Reject stale definitions, changed source targets, invalid approvals, and unsafe parameters.
- Do not append a successful run record after partial failure.
- Preserve the failed run and step evidence when safe to do so.
- Use rollback or regenerate when a partial mutation cannot be validated.

"""Workflow metadata extension validation."""

from _meta_contract_schema import (
    WORKFLOW_TABLES, WORKFLOW_AUTHORITY_ROLES, WORKFLOW_FAILURE_BEHAVIORS,
    WORKFLOW_CHECKPOINT_TYPES, WORKFLOW_UPDATE_MODES, WORKFLOW_RUN_STATUSES,
    WORKFLOW_STEP_STATUSES, WORKFLOW_VALIDATION_STATUSES,
)
from _meta_contract_utils import _nonblank_rows, _check_unique, _validate_integer, _validate_yes_no

def _validate_workflow_extension(
    rows_by_table: dict[str, list[dict[str, str]]],
    found_tables: set[str],
    workbook_sheets: set[str],
    errors: list[str],
) -> dict[str, object]:
    present = found_tables & WORKFLOW_TABLES
    if not present:
        return {"status": "not_present", "tables_present": [], "workflows": 0, "runs": 0}

    missing = sorted(WORKFLOW_TABLES - found_tables)
    for table in missing:
        errors.append(f"Workflow extension requires missing table: {table}")
    if missing:
        return {"status": "incomplete", "tables_present": sorted(present), "missing_tables": missing}

    workflows = _nonblank_rows(rows_by_table.get("tbl_meta_workflows", []), "Workflow_ID")
    sources = _nonblank_rows(rows_by_table.get("tbl_meta_workflow_sources", []), "Source_ID")
    inputs = _nonblank_rows(rows_by_table.get("tbl_meta_workflow_inputs", []), "Input_ID")
    steps = _nonblank_rows(rows_by_table.get("tbl_meta_workflow_steps", []), "Step_ID")
    outputs = _nonblank_rows(rows_by_table.get("tbl_meta_workflow_outputs", []), "Output_ID")
    runs = _nonblank_rows(rows_by_table.get("tbl_meta_workflow_runs", []), "Run_ID")
    run_steps = _nonblank_rows(rows_by_table.get("tbl_meta_workflow_run_steps", []), "Run_Step_ID")
    validations = _nonblank_rows(rows_by_table.get("tbl_meta_validations", []), "Validation_ID")

    workflow_ids = _check_unique(workflows, "Workflow_ID", "tbl_meta_workflows", errors)
    source_ids = _check_unique(sources, "Source_ID", "tbl_meta_workflow_sources", errors)
    _check_unique(inputs, "Input_ID", "tbl_meta_workflow_inputs", errors)
    _check_unique(steps, "Step_ID", "tbl_meta_workflow_steps", errors)
    _check_unique(outputs, "Output_ID", "tbl_meta_workflow_outputs", errors)
    run_ids = _check_unique(runs, "Run_ID", "tbl_meta_workflow_runs", errors)
    _check_unique(run_steps, "Run_Step_ID", "tbl_meta_workflow_run_steps", errors)
    validation_ids = {row.get("Validation_ID", "").strip() for row in validations}
    step_ids = {row.get("Step_ID", "").strip() for row in steps if row.get("Step_ID", "").strip()}
    run_workflow_ids = {
        row.get("Run_ID", "").strip(): row.get("Workflow_ID", "").strip()
        for row in runs
        if row.get("Run_ID", "").strip()
    }
    step_workflow_ids = {
        row.get("Step_ID", "").strip(): row.get("Workflow_ID", "").strip()
        for row in steps
        if row.get("Step_ID", "").strip()
    }

    for row in workflows:
        workflow_id = row.get("Workflow_ID", "").strip()
        _validate_yes_no(row.get("Active", "").strip(), f"Workflow {workflow_id} Active", errors)
        if not row.get("Workflow_Version", "").strip():
            errors.append(f"Workflow {workflow_id!r} has blank Workflow_Version")
        if not row.get("Purpose", "").strip():
            errors.append(f"Workflow {workflow_id!r} has blank Purpose")

    for row in sources:
        source_id = row.get("Source_ID", "").strip()
        workflow_id = row.get("Workflow_ID", "").strip()
        if workflow_id not in workflow_ids:
            errors.append(f"Workflow source {source_id!r} references missing workflow {workflow_id!r}")
        authority = row.get("Authority_Role", "").strip()
        if authority not in WORKFLOW_AUTHORITY_ROLES:
            errors.append(f"Workflow source {source_id!r} has unsupported Authority_Role {authority!r}")
        _validate_yes_no(row.get("Required", "").strip(), f"Workflow source {source_id} Required", errors)
        failure = row.get("Failure_Behavior", "").strip()
        if failure not in WORKFLOW_FAILURE_BEHAVIORS:
            errors.append(f"Workflow source {source_id!r} has unsupported Failure_Behavior {failure!r}")

    for row in inputs:
        input_id = row.get("Input_ID", "").strip()
        workflow_id = row.get("Workflow_ID", "").strip()
        if workflow_id not in workflow_ids:
            errors.append(f"Workflow input {input_id!r} references missing workflow {workflow_id!r}")
        _validate_yes_no(row.get("Required", "").strip(), f"Workflow input {input_id} Required", errors)
        _validate_yes_no(row.get("Sensitive", "").strip(), f"Workflow input {input_id} Sensitive", errors)

    seen_sequences: dict[str, set[int]] = {}
    for row in steps:
        step_id = row.get("Step_ID", "").strip()
        workflow_id = row.get("Workflow_ID", "").strip()
        if workflow_id not in workflow_ids:
            errors.append(f"Workflow step {step_id!r} references missing workflow {workflow_id!r}")
        raw_sequence = row.get("Sequence", "").strip()
        _validate_integer(raw_sequence, f"Workflow step {step_id} Sequence", errors)
        try:
            sequence = int(raw_sequence)
        except ValueError:
            sequence = 0
        if sequence <= 0:
            errors.append(f"Workflow step {step_id} Sequence must be greater than zero")
        elif sequence in seen_sequences.setdefault(workflow_id, set()):
            errors.append(f"Duplicate workflow Sequence {sequence} in {workflow_id!r}")
        else:
            seen_sequences[workflow_id].add(sequence)
        source_id = row.get("Source_ID", "").strip()
        if source_id and source_id not in source_ids:
            errors.append(f"Workflow step {step_id!r} references missing source {source_id!r}")
        _validate_yes_no(row.get("Required", "").strip(), f"Workflow step {step_id} Required", errors)
        checkpoint = row.get("Checkpoint_Type", "").strip()
        if checkpoint not in WORKFLOW_CHECKPOINT_TYPES:
            errors.append(f"Workflow step {step_id!r} has unsupported Checkpoint_Type {checkpoint!r}")
        validation_id = row.get("Validation_ID", "").strip()
        if validation_id and validation_id not in validation_ids:
            errors.append(f"Workflow step {step_id!r} references missing validation {validation_id!r}")
        _validate_yes_no(row.get("Evidence_Required", "").strip(), f"Workflow step {step_id} Evidence_Required", errors)
        failure = row.get("Failure_Behavior", "").strip()
        if failure not in WORKFLOW_FAILURE_BEHAVIORS:
            errors.append(f"Workflow step {step_id!r} has unsupported Failure_Behavior {failure!r}")

    for row in outputs:
        output_id = row.get("Output_ID", "").strip()
        workflow_id = row.get("Workflow_ID", "").strip()
        if workflow_id not in workflow_ids:
            errors.append(f"Workflow output {output_id!r} references missing workflow {workflow_id!r}")
        target_sheet = row.get("Target_Sheet", "").strip()
        if target_sheet and target_sheet not in workbook_sheets:
            errors.append(f"Workflow output {output_id!r} references missing sheet {target_sheet!r}")
        mode = row.get("Update_Mode", "").strip()
        if mode not in WORKFLOW_UPDATE_MODES:
            errors.append(f"Workflow output {output_id!r} has unsupported Update_Mode {mode!r}")
        _validate_yes_no(
            row.get("Preserve_Manual_Areas", "").strip(),
            f"Workflow output {output_id} Preserve_Manual_Areas",
            errors,
        )
        validation_id = row.get("Validation_ID", "").strip()
        if validation_id and validation_id not in validation_ids:
            errors.append(f"Workflow output {output_id!r} references missing validation {validation_id!r}")
        _validate_yes_no(row.get("Evidence_Required", "").strip(), f"Workflow output {output_id} Evidence_Required", errors)

    for row in runs:
        run_id = row.get("Run_ID", "").strip()
        workflow_id = row.get("Workflow_ID", "").strip()
        if workflow_id not in workflow_ids:
            errors.append(f"Workflow run {run_id!r} references missing workflow {workflow_id!r}")
        status = row.get("Status", "").strip()
        if status not in WORKFLOW_RUN_STATUSES:
            errors.append(f"Workflow run {run_id!r} has unsupported Status {status!r}")
        validation_status = row.get("Validation_Status", "").strip()
        if validation_status not in WORKFLOW_VALIDATION_STATUSES:
            errors.append(f"Workflow run {run_id!r} has unsupported Validation_Status {validation_status!r}")

    seen_run_step_pairs: set[tuple[str, str]] = set()
    for row in run_steps:
        run_step_id = row.get("Run_Step_ID", "").strip()
        run_id = row.get("Run_ID", "").strip()
        step_id = row.get("Step_ID", "").strip()
        if run_id not in run_ids:
            errors.append(f"Workflow run step {run_step_id!r} references missing run {run_id!r}")
        if step_id not in step_ids:
            errors.append(f"Workflow run step {run_step_id!r} references missing step {step_id!r}")
        run_workflow_id = run_workflow_ids.get(run_id)
        step_workflow_id = step_workflow_ids.get(step_id)
        if (
            run_workflow_id is not None
            and step_workflow_id is not None
            and run_workflow_id != step_workflow_id
        ):
            errors.append(
                f"Workflow run step {run_step_id!r} crosses workflows: "
                f"run {run_id!r} belongs to {run_workflow_id!r}, "
                f"step {step_id!r} belongs to {step_workflow_id!r}"
            )
        pair = (run_id, step_id)
        if pair in seen_run_step_pairs:
            errors.append(f"Duplicate workflow run-step pair {run_id!r}/{step_id!r}")
        else:
            seen_run_step_pairs.add(pair)
        _validate_yes_no(row.get("Checked", "").strip(), f"Workflow run step {run_step_id} Checked", errors)
        status = row.get("Status", "").strip()
        if status not in WORKFLOW_STEP_STATUSES:
            errors.append(f"Workflow run step {run_step_id!r} has unsupported Status {status!r}")

    for required_sheet in ("WORKFLOW", "RUN_HISTORY", "CHANGE_LOG"):
        if required_sheet not in workbook_sheets:
            errors.append(f"Workflow-enabled workbook is missing visible projection sheet {required_sheet!r}")

    return {
        "status": "present",
        "tables_present": sorted(present),
        "workflows": len(workflows),
        "sources": len(sources),
        "steps": len(steps),
        "outputs": len(outputs),
        "runs": len(runs),
        "run_steps": len(run_steps),
    }


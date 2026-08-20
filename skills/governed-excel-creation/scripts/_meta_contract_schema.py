"""Schema constants for the governed `_MCP_META` contract."""

from __future__ import annotations

import re

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

REQUIRED_TABLES: dict[str, list[str]] = {
    "tbl_meta_workbook": ["Key", "Value", "Description", "Required"],
    "tbl_meta_sheets": [
        "Sheet_ID", "Sheet_Name", "Role", "Description", "Grain", "Editable", "Primary_Output"
    ],
    "tbl_meta_fields": [
        "Field_ID", "Sheet_Name", "Table_Name", "Field_Name", "Data_Type", "Number_Format",
        "Description", "Source", "Formula_or_Rule", "Editable", "Required"
    ],
    "tbl_meta_rules": [
        "Rule_ID", "Rule_Name", "Output_Object", "Business_Rule", "Implementation", "Severity"
    ],
    "tbl_meta_relationships": [
        "Relationship_ID", "From_Object", "To_Object", "Relationship_Type", "Description"
    ],
    "tbl_meta_validations": [
        "Validation_ID", "Scope", "Validation_Type", "Expected_Result", "Status", "Evidence"
    ],
    "tbl_meta_changes": [
        "Change_ID", "Changed_At", "Changed_By", "Change_Type", "Object", "Description"
    ],
}

OPTIONAL_TABLES: dict[str, list[str]] = {
    "tbl_meta_requirements": [
        "Requirement_ID", "Requirement_Type", "Audience", "Business_Purpose", "Target_Object",
        "Requirement", "Acceptance_Criterion", "Priority", "Status"
    ],
    "tbl_meta_maintenance": [
        "Step_ID", "Sequence", "Maintenance_Type", "Trigger_or_Frequency", "Responsible_Role",
        "Required_Tool", "Target_Object", "Procedure", "Validation_ID", "Evidence_Required", "Notes"
    ],
    "tbl_meta_styles": [
        "Style_ID", "Style_Name", "Semantic_Role", "Description", "Inherits_From", "Active"
    ],
    "tbl_meta_style_properties": [
        "Style_Property_ID", "Style_ID", "Property", "Value", "Value_Type", "Apply_Mode"
    ],
    "tbl_meta_format_regions": [
        "Format_ID", "Sheet_Name", "Target_Type", "Target_Ref", "Style_ID",
        "Conditional_Rule_ID", "Priority", "Preserve_Unspecified", "Active", "Notes"
    ],
    "tbl_meta_layout": [
        "Layout_ID", "Sheet_Name", "Layout_Type", "Target_Ref", "Value", "Priority", "Active", "Notes"
    ],
    "tbl_meta_workflows": [
        "Workflow_ID", "Workflow_Name", "Workflow_Version", "Purpose", "Trigger", "Owner_Role",
        "Execution_Mode", "Definition_Ref", "Source_of_Truth", "Active"
    ],
    "tbl_meta_workflow_sources": [
        "Source_ID", "Workflow_ID", "System", "Authority_Role", "Connector_or_Tool",
        "Retrieval_Contract", "Required", "Scope_or_Filter", "Freshness_Rule", "Failure_Behavior"
    ],
    "tbl_meta_workflow_inputs": [
        "Input_ID", "Workflow_ID", "Input_Name", "Data_Type", "Required", "Default_Value",
        "Allowed_Values_or_Rule", "Sensitive", "Description"
    ],
    "tbl_meta_workflow_steps": [
        "Step_ID", "Workflow_ID", "Sequence", "Step_Type", "Source_ID", "Operation",
        "Target_Object", "Required", "Checkpoint_Type", "Validation_ID", "Evidence_Required",
        "Failure_Behavior"
    ],
    "tbl_meta_workflow_outputs": [
        "Output_ID", "Workflow_ID", "Output_Name", "Target_Sheet", "Target_Object", "Update_Mode",
        "Preserve_Manual_Areas", "Validation_ID", "Evidence_Required"
    ],
    "tbl_meta_workflow_runs": [
        "Run_ID", "Workflow_ID", "Workflow_Version", "Started_At", "Completed_At", "Status",
        "Source_Snapshot", "Input_Fingerprint", "Output_Fingerprint", "Plan_or_Definition_Hash",
        "Validation_Status", "Evidence_Ref", "Executed_By"
    ],
    "tbl_meta_workflow_run_steps": [
        "Run_Step_ID", "Run_ID", "Step_ID", "Checked", "Status", "Started_At", "Completed_At",
        "Result_Summary", "Evidence_Ref", "Error_or_Warning"
    ],
}

FORMAT_CORE_TABLES = {
    "tbl_meta_styles",
    "tbl_meta_style_properties",
    "tbl_meta_format_regions",
}

ALLOWED_STYLE_PROPERTIES = {
    "font_name", "font_size", "bold", "italic", "underline", "font_color", "fill_color",
    "number_format", "horizontal", "vertical", "wrap_text", "shrink_to_fit", "text_rotation",
    "indent", "border_style", "border_color", "table_style",
}
ALLOWED_VALUE_TYPES = {"Text", "Number", "Boolean", "FormatCode"}
ALLOWED_APPLY_MODES = {"set", "preserve_if_blank", "clear"}
ALLOWED_TARGET_TYPES = {"range", "table", "named_range", "row", "column"}
ALLOWED_LAYOUT_TYPES = {
    "column_width", "row_height", "autofit_columns", "freeze_panes", "gridlines", "zoom", "print_area"
}
YES_NO = {"Yes", "No"}

WORKFLOW_TABLES = {
    "tbl_meta_workflows",
    "tbl_meta_workflow_sources",
    "tbl_meta_workflow_inputs",
    "tbl_meta_workflow_steps",
    "tbl_meta_workflow_outputs",
    "tbl_meta_workflow_runs",
    "tbl_meta_workflow_run_steps",
}
WORKFLOW_AUTHORITY_ROLES = {"Authoritative", "Contextual", "Derived", "Manual", "Unknown"}
WORKFLOW_FAILURE_BEHAVIORS = {"Stop", "Warn", "Skip", "Continue"}
WORKFLOW_CHECKPOINT_TYPES = {"None", "Checkbox", "Confirmation", "Approval", "Validation", "Review"}
WORKFLOW_UPDATE_MODES = {
    "generated_replace", "generated_append", "manual_preserve", "formula_managed",
    "system_metadata", "evidence_append_only"
}
WORKFLOW_RUN_STATUSES = {
    "PLANNED", "RUNNING", "COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED",
    "CANCELLED", "ROLLED_BACK"
}
WORKFLOW_STEP_STATUSES = {
    "NOT_STARTED", "RUNNING", "COMPLETED", "SKIPPED", "WARNING", "FAILED", "ROLLED_BACK"
}
WORKFLOW_VALIDATION_STATUSES = {"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"}
A1_RANGE_RE = re.compile(r"^\$?[A-Z]{1,3}\$?[1-9][0-9]*(?::\$?[A-Z]{1,3}\$?[1-9][0-9]*)?$")
CELL_RE = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")

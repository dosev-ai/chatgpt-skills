"""Core `_MCP_META` row validation and workbook-reference checks."""

from _meta_contract_utils import _check_unique, _validate_yes_no

SHEET_ROLES = {
    "Documentation", "Maintenance", "Input", "Raw", "Mapping", "Calculation",
    "Output", "Dashboard", "Metadata",
}
DATA_TYPES = {
    "Text", "Integer", "Decimal", "Currency", "Percentage", "Date", "Boolean",
    "Formula", "Unknown",
}
RULE_SEVERITIES = {"Info", "Warning", "Error", "Critical"}
RELATIONSHIP_TYPES = {"Feeds", "Maps", "Calculates", "Aggregates", "Validates", "Formats", "References"}
VALIDATION_TYPES = {"Structure", "Formula", "Metadata", "Preservation", "Input", "Visual", "Delta", "Readiness"}
VALIDATION_STATUSES = {"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"}
CHANGE_TYPES = {"Create", "Update", "Repair", "Reformat", "Onboard", "Validate", "Rollback"}
NONEMPTY_REQUIRED_TABLES = {
    "tbl_meta_workbook",
    "tbl_meta_sheets",
    "tbl_meta_fields",
    "tbl_meta_validations",
    "tbl_meta_changes",
}


def _required_text(row: dict[str, str], field: str, label: str, errors: list[str]) -> str:
    value = row.get(field, "").strip()
    if not value:
        errors.append(f"{label} has blank {field}")
    return value


def _validate_core_tables(
    rows_by_table: dict[str, list[dict[str, str]]],
    found_tables: set[str],
    workbook_sheets: set[str],
    errors: list[str],
    warnings: list[str],
) -> dict[str, object]:
    for table in sorted(NONEMPTY_REQUIRED_TABLES & found_tables):
        if not rows_by_table.get(table):
            errors.append(f"Required metadata table {table} has no data rows")

    workbook_rows = rows_by_table.get("tbl_meta_workbook", [])
    _check_unique(workbook_rows, "Key", "tbl_meta_workbook", errors)
    for row in workbook_rows:
        key = _required_text(row, "Key", "Workbook metadata row", errors)
        required = row.get("Required", "").strip()
        _validate_yes_no(required, f"Workbook metadata {key!r} Required", errors)
        if required == "Yes" and not row.get("Value", "").strip():
            errors.append(f"Required workbook metadata {key!r} has blank Value")
        _required_text(row, "Description", f"Workbook metadata {key!r}", errors)

    sheet_rows = rows_by_table.get("tbl_meta_sheets", [])
    _check_unique(sheet_rows, "Sheet_ID", "tbl_meta_sheets", errors)
    declared_sheet_names: set[str] = set()
    for row in sheet_rows:
        sheet_id = _required_text(row, "Sheet_ID", "Sheet metadata row", errors)
        sheet_name = _required_text(row, "Sheet_Name", f"Sheet {sheet_id!r}", errors)
        if sheet_name:
            if sheet_name in declared_sheet_names:
                errors.append(f"Duplicate Sheet_Name {sheet_name!r} in tbl_meta_sheets")
            declared_sheet_names.add(sheet_name)
            if sheet_name not in workbook_sheets:
                errors.append(f"Sheet {sheet_id!r} references missing worksheet {sheet_name!r}")
        role = row.get("Role", "").strip()
        if role not in SHEET_ROLES:
            errors.append(f"Sheet {sheet_id!r} has unsupported Role {role!r}")
        _validate_yes_no(row.get("Editable", "").strip(), f"Sheet {sheet_id} Editable", errors)
        _validate_yes_no(row.get("Primary_Output", "").strip(), f"Sheet {sheet_id} Primary_Output", errors)
        _required_text(row, "Description", f"Sheet {sheet_id!r}", errors)
        _required_text(row, "Grain", f"Sheet {sheet_id!r}", errors)

    missing_sheet_metadata = sorted(workbook_sheets - declared_sheet_names)
    if missing_sheet_metadata:
        errors.append(f"Workbook sheets missing from tbl_meta_sheets: {missing_sheet_metadata}")
    extra_sheet_metadata = sorted(declared_sheet_names - workbook_sheets)
    if extra_sheet_metadata:
        errors.append(f"tbl_meta_sheets references absent workbook sheets: {extra_sheet_metadata}")

    field_rows = rows_by_table.get("tbl_meta_fields", [])
    _check_unique(field_rows, "Field_ID", "tbl_meta_fields", errors)
    seen_field_keys: set[tuple[str, str, str]] = set()
    for row in field_rows:
        field_id = _required_text(row, "Field_ID", "Field metadata row", errors)
        sheet_name = _required_text(row, "Sheet_Name", f"Field {field_id!r}", errors)
        field_name = _required_text(row, "Field_Name", f"Field {field_id!r}", errors)
        table_name = row.get("Table_Name", "").strip()
        if sheet_name and sheet_name not in workbook_sheets:
            errors.append(f"Field {field_id!r} references missing worksheet {sheet_name!r}")
        field_key = (sheet_name, table_name, field_name)
        if field_name and field_key in seen_field_keys:
            errors.append(f"Duplicate field identity {field_key!r} in tbl_meta_fields")
        seen_field_keys.add(field_key)
        data_type = row.get("Data_Type", "").strip()
        if data_type not in DATA_TYPES:
            errors.append(f"Field {field_id!r} has unsupported Data_Type {data_type!r}")
        _validate_yes_no(row.get("Editable", "").strip(), f"Field {field_id} Editable", errors)
        _validate_yes_no(row.get("Required", "").strip(), f"Field {field_id} Required", errors)
        _required_text(row, "Description", f"Field {field_id!r}", errors)
        _required_text(row, "Source", f"Field {field_id!r}", errors)

    rule_rows = rows_by_table.get("tbl_meta_rules", [])
    _check_unique(rule_rows, "Rule_ID", "tbl_meta_rules", errors)
    if "tbl_meta_rules" in found_tables and not rule_rows:
        warnings.append("tbl_meta_rules has no rows; no explicit workbook rules are declared")
    for row in rule_rows:
        rule_id = _required_text(row, "Rule_ID", "Rule metadata row", errors)
        for field in ("Rule_Name", "Output_Object", "Business_Rule", "Implementation"):
            _required_text(row, field, f"Rule {rule_id!r}", errors)
        severity = row.get("Severity", "").strip()
        if severity not in RULE_SEVERITIES:
            errors.append(f"Rule {rule_id!r} has unsupported Severity {severity!r}")

    relationship_rows = rows_by_table.get("tbl_meta_relationships", [])
    _check_unique(relationship_rows, "Relationship_ID", "tbl_meta_relationships", errors)
    if "tbl_meta_relationships" in found_tables and not relationship_rows:
        warnings.append("tbl_meta_relationships has no rows; no explicit lineage relationships are declared")
    for row in relationship_rows:
        relationship_id = _required_text(row, "Relationship_ID", "Relationship metadata row", errors)
        for field in ("From_Object", "To_Object", "Description"):
            _required_text(row, field, f"Relationship {relationship_id!r}", errors)
        relationship_type = row.get("Relationship_Type", "").strip()
        if relationship_type not in RELATIONSHIP_TYPES:
            errors.append(
                f"Relationship {relationship_id!r} has unsupported Relationship_Type {relationship_type!r}"
            )

    validation_rows = rows_by_table.get("tbl_meta_validations", [])
    _check_unique(validation_rows, "Validation_ID", "tbl_meta_validations", errors)
    for row in validation_rows:
        validation_id = _required_text(row, "Validation_ID", "Validation metadata row", errors)
        _required_text(row, "Scope", f"Validation {validation_id!r}", errors)
        _required_text(row, "Expected_Result", f"Validation {validation_id!r}", errors)
        validation_type = row.get("Validation_Type", "").strip()
        if validation_type not in VALIDATION_TYPES:
            errors.append(f"Validation {validation_id!r} has unsupported Validation_Type {validation_type!r}")
        status = row.get("Status", "").strip()
        if status not in VALIDATION_STATUSES:
            errors.append(f"Validation {validation_id!r} has unsupported Status {status!r}")
        if status in {"PASS", "FAIL"} and not row.get("Evidence", "").strip():
            errors.append(f"Validation {validation_id!r} with status {status} has blank Evidence")

    change_rows = rows_by_table.get("tbl_meta_changes", [])
    _check_unique(change_rows, "Change_ID", "tbl_meta_changes", errors)
    for row in change_rows:
        change_id = _required_text(row, "Change_ID", "Change metadata row", errors)
        for field in ("Changed_At", "Changed_By", "Object", "Description"):
            _required_text(row, field, f"Change {change_id!r}", errors)
        change_type = row.get("Change_Type", "").strip()
        if change_type not in CHANGE_TYPES:
            errors.append(f"Change {change_id!r} has unsupported Change_Type {change_type!r}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "workbook_rows": len(workbook_rows),
        "sheet_rows": len(sheet_rows),
        "field_rows": len(field_rows),
        "rule_rows": len(rule_rows),
        "relationship_rows": len(relationship_rows),
        "validation_rows": len(validation_rows),
        "change_rows": len(change_rows),
    }

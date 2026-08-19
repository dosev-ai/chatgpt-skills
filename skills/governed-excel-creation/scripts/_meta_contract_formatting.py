"""Formatting metadata extension validation."""

from _meta_contract_schema import (
    FORMAT_CORE_TABLES, ALLOWED_STYLE_PROPERTIES, ALLOWED_VALUE_TYPES,
    ALLOWED_APPLY_MODES, ALLOWED_TARGET_TYPES, ALLOWED_LAYOUT_TYPES, A1_RANGE_RE,
)
from _meta_contract_utils import (
    _nonblank_rows, _check_unique, _validate_integer, _validate_yes_no,
    _validate_inheritance,
)

def _validate_format_extension(
    rows_by_table: dict[str, list[dict[str, str]]],
    found_tables: set[str],
    workbook_sheets: set[str],
    errors: list[str],
) -> dict[str, object]:
    format_tables = FORMAT_CORE_TABLES | {"tbl_meta_layout"}
    present = sorted(found_tables & format_tables)
    result: dict[str, object] = {"status": "not_present", "tables_present": present}
    if not present:
        return result

    result["status"] = "present"
    missing_core = sorted(FORMAT_CORE_TABLES - found_tables)
    for table in missing_core:
        errors.append(f"Formatting extension requires missing table: {table}")
    if missing_core:
        return result

    styles = _nonblank_rows(rows_by_table.get("tbl_meta_styles", []), "Style_ID")
    properties = _nonblank_rows(rows_by_table.get("tbl_meta_style_properties", []), "Style_Property_ID")
    regions = _nonblank_rows(rows_by_table.get("tbl_meta_format_regions", []), "Format_ID")
    layouts = _nonblank_rows(rows_by_table.get("tbl_meta_layout", []), "Layout_ID")
    rules = _nonblank_rows(rows_by_table.get("tbl_meta_rules", []), "Rule_ID")

    style_ids = _check_unique(styles, "Style_ID", "tbl_meta_styles", errors)
    _check_unique(properties, "Style_Property_ID", "tbl_meta_style_properties", errors)
    _check_unique(regions, "Format_ID", "tbl_meta_format_regions", errors)
    _check_unique(layouts, "Layout_ID", "tbl_meta_layout", errors)
    rule_ids = {row["Rule_ID"].strip() for row in rules}

    for row in styles:
        _validate_yes_no(row.get("Active", ""), f"Style {row['Style_ID']} Active", errors)
    _validate_inheritance(styles, style_ids, errors)

    for row in properties:
        prop_id = row["Style_Property_ID"].strip()
        style_id = row.get("Style_ID", "").strip()
        if style_id not in style_ids:
            errors.append(f"Style property {prop_id!r} references missing style {style_id!r}")
        prop = row.get("Property", "").strip()
        if prop not in ALLOWED_STYLE_PROPERTIES:
            errors.append(f"Style property {prop_id!r} has unsupported Property {prop!r}")
        value_type = row.get("Value_Type", "").strip()
        if value_type not in ALLOWED_VALUE_TYPES:
            errors.append(f"Style property {prop_id!r} has unsupported Value_Type {value_type!r}")
        mode = row.get("Apply_Mode", "").strip()
        if mode not in ALLOWED_APPLY_MODES:
            errors.append(f"Style property {prop_id!r} has unsupported Apply_Mode {mode!r}")

    exact_targets: dict[tuple[str, str, str, str], str] = {}
    for row in regions:
        format_id = row["Format_ID"].strip()
        sheet = row.get("Sheet_Name", "").strip()
        if sheet not in workbook_sheets:
            errors.append(f"Format region {format_id!r} references missing sheet {sheet!r}")
        target_type = row.get("Target_Type", "").strip()
        if target_type not in ALLOWED_TARGET_TYPES:
            errors.append(f"Format region {format_id!r} has unsupported Target_Type {target_type!r}")
        target_ref = row.get("Target_Ref", "").strip().upper()
        if not target_ref:
            errors.append(f"Format region {format_id!r} has blank Target_Ref")
        elif target_type == "range" and not A1_RANGE_RE.match(target_ref):
            errors.append(f"Format region {format_id!r} has invalid A1 Target_Ref {target_ref!r}")
        style_id = row.get("Style_ID", "").strip()
        if style_id not in style_ids:
            errors.append(f"Format region {format_id!r} references missing style {style_id!r}")
        conditional = row.get("Conditional_Rule_ID", "").strip()
        if conditional and conditional not in rule_ids:
            errors.append(f"Format region {format_id!r} references missing rule {conditional!r}")
        priority = row.get("Priority", "").strip()
        _validate_integer(priority, f"Format region {format_id} Priority", errors)
        _validate_yes_no(
            row.get("Preserve_Unspecified", ""),
            f"Format region {format_id} Preserve_Unspecified",
            errors,
        )
        _validate_yes_no(row.get("Active", ""), f"Format region {format_id} Active", errors)
        key = (sheet, target_type, target_ref, priority)
        prior_style = exact_targets.get(key)
        if prior_style is not None and prior_style != style_id:
            errors.append(
                f"Equal-priority format conflict on {sheet}!{target_ref}: styles {prior_style!r} and {style_id!r}"
            )
        else:
            exact_targets[key] = style_id

    for row in layouts:
        layout_id = row["Layout_ID"].strip()
        sheet = row.get("Sheet_Name", "").strip()
        if sheet not in workbook_sheets:
            errors.append(f"Layout {layout_id!r} references missing sheet {sheet!r}")
        layout_type = row.get("Layout_Type", "").strip()
        if layout_type not in ALLOWED_LAYOUT_TYPES:
            errors.append(f"Layout {layout_id!r} has unsupported Layout_Type {layout_type!r}")
        _validate_integer(row.get("Priority", "").strip(), f"Layout {layout_id} Priority", errors)
        _validate_yes_no(row.get("Active", ""), f"Layout {layout_id} Active", errors)

    result.update({
        "styles": len(styles),
        "style_properties": len(properties),
        "format_regions": len(regions),
        "layout_rows": len(layouts),
    })
    return result

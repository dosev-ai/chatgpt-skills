"""Maintenance metadata extension validation."""

from _meta_contract_utils import _nonblank_rows, _check_unique, _validate_integer

def _validate_maintenance_extension(
    rows_by_table: dict[str, list[dict[str, str]]],
    found_tables: set[str],
    errors: list[str],
) -> dict[str, object]:
    if "tbl_meta_maintenance" not in found_tables:
        return {"status": "not_present", "steps": 0}

    rows = _nonblank_rows(rows_by_table.get("tbl_meta_maintenance", []), "Step_ID")
    _check_unique(rows, "Step_ID", "tbl_meta_maintenance", errors)
    validation_ids = {
        row.get("Validation_ID", "").strip()
        for row in _nonblank_rows(rows_by_table.get("tbl_meta_validations", []), "Validation_ID")
    }
    sequences: set[int] = set()
    for row in rows:
        step_id = row.get("Step_ID", "").strip()
        raw_sequence = row.get("Sequence", "").strip()
        _validate_integer(raw_sequence, f"Maintenance step {step_id} Sequence", errors)
        try:
            sequence = int(raw_sequence)
        except ValueError:
            continue
        if sequence <= 0:
            errors.append(f"Maintenance step {step_id} Sequence must be greater than zero")
        elif sequence in sequences:
            errors.append(f"Duplicate maintenance Sequence {sequence}")
        else:
            sequences.add(sequence)
        validation_id = row.get("Validation_ID", "").strip()
        if validation_id and validation_id not in validation_ids:
            errors.append(
                f"Maintenance step {step_id!r} references missing validation {validation_id!r}"
            )
        if not row.get("Procedure", "").strip():
            errors.append(f"Maintenance step {step_id!r} has blank Procedure")

    return {"status": "present", "steps": len(rows)}

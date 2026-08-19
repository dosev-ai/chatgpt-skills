#!/usr/bin/env python3
"""Compare before/after XLSX packages and detect undeclared package drift."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from _ooxml import package_part_hashes, sheet_part_to_name, workbook_context
from _shared_strings import SHARED_STRINGS_PART, shared_string_impacted_sheets

VOLATILE_PARTS = {"xl/calcChain.xml"}


def _nonempty_strings(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def declared_sheets(plan: dict[str, object]) -> set[str]:
    result: set[str] = set()
    operations = plan.get("operations", [])
    if not isinstance(operations, list):
        return result
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        target = operation.get("target")
        if not isinstance(target, dict):
            continue
        sheet = target.get("sheet")
        if isinstance(sheet, str) and sheet.strip():
            result.add(sheet.strip())
        result.update(_nonempty_strings(target.get("sheets")))
    return result


def declared_parts(plan: dict[str, object]) -> set[str]:
    result: set[str] = set()
    operations = plan.get("operations", [])
    if not isinstance(operations, list):
        return result
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        target = operation.get("target")
        if not isinstance(target, dict):
            continue
        part = target.get("part")
        if isinstance(part, str) and part.strip():
            result.add(part.strip().lstrip("/"))
        result.update(item.lstrip("/") for item in _nonempty_strings(target.get("parts")))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--allow-meta-update", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.before.is_file() or not args.after.is_file():
        print(json.dumps({"status": "ERROR", "error": "Before or after workbook not found"}, indent=2))
        return 2

    try:
        before_hashes = package_part_hashes(args.before)
        after_hashes = package_part_hashes(args.after)
        before_context = workbook_context(args.before)
        after_context = workbook_context(args.after)
        before_sheet_map = sheet_part_to_name(args.before)
        after_sheet_map = sheet_part_to_name(args.after)
        plan = json.loads(args.plan.read_text(encoding="utf-8")) if args.plan else None
        if plan is not None and not isinstance(plan, dict):
            raise ValueError("Plan must be a JSON object")
    except (json.JSONDecodeError, ValueError, zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as exc:
        payload = {"status": "ERROR", "error": str(exc)}
        code = 2
    else:
        all_parts = sorted(set(before_hashes) | set(after_hashes))
        added_parts = [name for name in all_parts if name not in before_hashes]
        removed_parts = [name for name in all_parts if name not in after_hashes]
        modified_parts = [
            name for name in all_parts
            if name in before_hashes and name in after_hashes and before_hashes[name] != after_hashes[name]
        ]
        changed_parts = sorted(set(added_parts + removed_parts + modified_parts))
        changed_sheets: set[str] = set()
        sheet_bound_parts: set[str] = set()
        for part in changed_parts:
            if part in before_sheet_map:
                changed_sheets.add(before_sheet_map[part])
                sheet_bound_parts.add(part)
            if part in after_sheet_map:
                changed_sheets.add(after_sheet_map[part])
                sheet_bound_parts.add(part)

        shared_string_sheets: set[str] = set()
        if SHARED_STRINGS_PART in changed_parts:
            shared_string_sheets = shared_string_impacted_sheets(args.before, args.after)
            changed_sheets.update(shared_string_sheets)
            if shared_string_sheets:
                sheet_bound_parts.add(SHARED_STRINGS_PART)

        declared = declared_sheets(plan) if plan else set()
        allowed_sheets = set(declared)
        if args.allow_meta_update or plan:
            allowed_sheets.add("_MCP_META")
        declared_package_parts = declared_parts(plan) if plan else set()
        undeclared_sheets = sorted(changed_sheets - allowed_sheets) if plan else []
        non_sheet_changed_parts = set(changed_parts) - sheet_bound_parts
        ignored_volatile_parts = sorted(non_sheet_changed_parts & VOLATILE_PARTS)
        undeclared_parts = sorted(
            non_sheet_changed_parts - declared_package_parts - VOLATILE_PARTS
        ) if plan else []

        before_names = {sheet["name"] for sheet in before_context["sheets"]}
        after_names = {sheet["name"] for sheet in after_context["sheets"]}
        sheet_changes = {
            "added": sorted(after_names - before_names),
            "removed": sorted(before_names - after_names),
            "changed": sorted(changed_sheets),
            "declared": sorted(declared),
            "undeclared": undeclared_sheets,
            "shared_string_impacted": sorted(shared_string_sheets),
        }
        errors: list[str] = []
        if plan and undeclared_sheets:
            errors.append(f"Undeclared changed sheets: {undeclared_sheets}")
        if plan and undeclared_parts:
            errors.append(f"Undeclared changed package parts: {undeclared_parts}")
        payload = {
            "status": "PASS" if not errors else "FAIL",
            "before_fingerprint": before_context["fingerprint"],
            "after_fingerprint": after_context["fingerprint"],
            "changed_part_count": len(changed_parts),
            "added_parts": added_parts,
            "removed_parts": removed_parts,
            "modified_parts": modified_parts,
            "declared_package_parts": sorted(declared_package_parts),
            "ignored_volatile_parts": ignored_volatile_parts,
            "undeclared_changed_parts": undeclared_parts,
            "sheet_changes": sheet_changes,
            "formula_count_before": before_context["formula_count"],
            "formula_count_after": after_context["formula_count"],
            "error_cells_before": before_context["error_cell_count"],
            "error_cells_after": after_context["error_cell_count"],
            "errors": errors,
        }
        code = 0 if not errors else 1

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

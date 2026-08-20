#!/usr/bin/env python3
"""Run repeatable governed workbook checks and emit separated readiness states."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from _ooxml import canonical_json_hash, package_part_hashes, sheet_part_to_name, workbook_context
from _shared_strings import SHARED_STRINGS_PART, shared_string_impacted_sheets
from validate_meta_contract import validate as validate_meta

VOLATILE_PARTS = {"xl/calcChain.xml"}


def load_plan(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Plan must be a JSON object")
    return value


def verify_plan(plan: dict[str, object], source_context: dict[str, object], approved_hash: str | None) -> dict[str, object]:
    stored_hash = str(plan.get("plan_hash", ""))
    hash_input = dict(plan)
    hash_input.pop("plan_hash", None)
    calculated_hash = canonical_json_hash(hash_input)
    target = plan.get("target", {}) if isinstance(plan.get("target"), dict) else {}
    approval_required = bool(plan.get("approval_required", False))
    return {
        "plan_integrity": bool(stored_hash) and stored_hash == calculated_hash,
        "target_unchanged": target.get("fingerprint") == source_context.get("fingerprint"),
        "approval_required": approval_required,
        "approval_bound": not approval_required or (bool(approved_hash) and approved_hash == stored_hash),
        "plan_hash": stored_hash,
    }


def _nonempty_strings(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def declared_sheets(plan: dict[str, object] | None) -> set[str]:
    if not plan:
        return set()
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


def declared_parts(plan: dict[str, object] | None) -> set[str]:
    if not plan:
        return set()
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


def delta_summary(before: Path, after: Path, plan: dict[str, object] | None) -> dict[str, object]:
    before_hashes = package_part_hashes(before)
    after_hashes = package_part_hashes(after)
    all_parts = set(before_hashes) | set(after_hashes)
    changed_parts = sorted(
        part for part in all_parts
        if before_hashes.get(part) != after_hashes.get(part)
    )
    before_map = sheet_part_to_name(before)
    after_map = sheet_part_to_name(after)
    changed_sheets: set[str] = set()
    sheet_bound_parts: set[str] = set()
    for part in changed_parts:
        if part in before_map:
            changed_sheets.add(before_map[part])
            sheet_bound_parts.add(part)
        if part in after_map:
            changed_sheets.add(after_map[part])
            sheet_bound_parts.add(part)

    shared_string_sheets: set[str] = set()
    if SHARED_STRINGS_PART in changed_parts:
        shared_string_sheets = shared_string_impacted_sheets(before, after)
        changed_sheets.update(shared_string_sheets)
        if shared_string_sheets:
            sheet_bound_parts.add(SHARED_STRINGS_PART)

    allowed_sheets = declared_sheets(plan)
    if plan:
        allowed_sheets.add("_MCP_META")
    allowed_parts = declared_parts(plan)
    undeclared_sheets = sorted(changed_sheets - allowed_sheets) if plan else []
    non_sheet_changed_parts = set(changed_parts) - sheet_bound_parts
    ignored_volatile_parts = sorted(non_sheet_changed_parts & VOLATILE_PARTS)
    undeclared_parts = sorted(
        non_sheet_changed_parts - allowed_parts - VOLATILE_PARTS
    ) if plan else []
    return {
        "changed_part_count": len(changed_parts),
        "changed_parts": changed_parts,
        "changed_sheets": sorted(changed_sheets),
        "shared_string_impacted_sheets": sorted(shared_string_sheets),
        "declared_sheets": sorted(declared_sheets(plan)),
        "declared_parts": sorted(allowed_parts),
        "ignored_volatile_parts": ignored_volatile_parts,
        "undeclared_changed_sheets": undeclared_sheets,
        "undeclared_changed_parts": undeclared_parts,
        "conformant": not undeclared_sheets and not undeclared_parts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="Workbook to validate and deliver")
    parser.add_argument("--before", type=Path, help="Optional pre-change workbook")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--approved-plan-hash")
    parser.add_argument("--visual-review-pass", action="store_true")
    parser.add_argument("--block-cached-errors", action="store_true", help="Treat cached OOXML error cells as blocking")
    parser.add_argument("--acceptance-pass", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.workbook.is_file():
        print(json.dumps({"status": "ERROR", "error": "Workbook not found"}, indent=2))
        return 2

    try:
        context = workbook_context(args.workbook)
        metadata = validate_meta(args.workbook)
        plan = load_plan(args.plan)
        source_context = workbook_context(args.before) if args.before else context
        plan_check = verify_plan(plan, source_context, args.approved_plan_hash) if plan else None
        delta = delta_summary(args.before, args.workbook, plan) if args.before else None
    except (json.JSONDecodeError, ValueError, zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as exc:
        payload = {"status": "ERROR", "error": str(exc)}
        code = 2
    else:
        safe_to_open = True
        metadata_consistent = metadata.get("status") == "PASS"
        no_error_cells = context.get("error_cell_count") == 0
        plan_gate = True if plan_check is None else all([
            plan_check["plan_integrity"],
            plan_check["target_unchanged"],
            plan_check["approval_bound"],
        ])
        delta_conformant = True if delta is None else bool(delta["conformant"])
        cached_error_gate = no_error_cells or not args.block_cached_errors
        technical_pass = all([safe_to_open, metadata_consistent, cached_error_gate, plan_gate, delta_conformant])
        ready_for_review: bool | str = bool(args.visual_review_pass and technical_pass)
        if not args.visual_review_pass:
            ready_for_review = "PENDING_VISUAL_REVIEW"
        ready_to_distribute = bool(technical_pass and args.visual_review_pass and args.acceptance_pass)
        payload = {
            "status": "PASS" if technical_pass else "FAIL",
            "workbook": str(args.workbook),
            "fingerprint": context["fingerprint"],
            "safe_to_open": safe_to_open,
            "metadata_consistent": metadata_consistent,
            "no_cached_error_cells": no_error_cells,
            "cached_error_cells_blocking": bool(args.block_cached_errors),
            "plan_gate": plan_gate,
            "delta_conformant": delta_conformant,
            "ready_for_review": ready_for_review,
            "ready_to_distribute": ready_to_distribute,
            "rollback_available": bool(args.before),
            "plan_check": plan_check,
            "delta": delta,
            "metadata_errors": metadata.get("errors", []),
            "limitations": [
                "Cached OOXML error-cell scan does not replace native Excel recalculation.",
                "Business usability and visual quality require explicit render review.",
            ],
        }
        code = 0 if technical_pass else 1

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

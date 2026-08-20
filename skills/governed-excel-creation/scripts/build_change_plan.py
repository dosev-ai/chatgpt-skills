#!/usr/bin/env python3
"""Build a versioned, target-locked workbook change plan from JSON input."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET

from _ooxml import canonical_json_hash, workbook_context

ALLOWED_RISK_TIERS = {"minimal_export", "standard_business_workbook", "governed_existing_workbook_rework"}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_request(value: object) -> tuple[dict[str, object] | None, list[str]]:
    if not isinstance(value, dict):
        return None, ["Plan request must be a JSON object"]
    errors: list[str] = []
    intent = value.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        errors.append("intent must be a non-empty string")
    risk_tier = value.get("risk_tier", "standard_business_workbook")
    if risk_tier not in ALLOWED_RISK_TIERS:
        errors.append(f"risk_tier must be one of {sorted(ALLOWED_RISK_TIERS)}")
    operations = value.get("operations")
    if not isinstance(operations, list) or not operations:
        errors.append("operations must be a non-empty array")
    else:
        seen: set[str] = set()
        for index, operation in enumerate(operations, start=1):
            if not isinstance(operation, dict):
                errors.append(f"operation {index} must be an object")
                continue
            operation_id = operation.get("operation_id")
            if not isinstance(operation_id, str) or not operation_id.strip():
                errors.append(f"operation {index} requires operation_id")
            elif operation_id in seen:
                errors.append(f"duplicate operation_id {operation_id!r}")
            else:
                seen.add(operation_id)
            if not isinstance(operation.get("operation"), str) or not str(operation.get("operation")).strip():
                errors.append(f"operation {index} requires operation")
            if not isinstance(operation.get("target"), dict):
                errors.append(f"operation {index} requires target object")
    for field in ("requirements", "validation_checks", "preservation_rules"):
        if field in value and not isinstance(value[field], list):
            errors.append(f"{field} must be an array when supplied")
    return value, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("request", type=Path, help="JSON plan request")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--created-at", help="ISO timestamp override for deterministic tests")
    args = parser.parse_args()

    if not args.workbook.is_file() or not args.request.is_file():
        print(json.dumps({"status": "ERROR", "error": "Workbook or request not found"}, indent=2))
        return 2

    try:
        request_raw = load_json(args.request)
        request, errors = validate_request(request_raw)
        context = workbook_context(args.workbook)
    except (json.JSONDecodeError, zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2

    if errors or request is None:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
        return 1

    created_at = args.created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    plan_body: dict[str, object] = {
        "schema": "governed-excel-change-plan/v1",
        "plan_version": 1,
        "created_at": created_at,
        "risk_tier": request.get("risk_tier", "standard_business_workbook"),
        "intent": request["intent"],
        "target": {
            "workbook": str(args.workbook),
            "fingerprint": context["fingerprint"],
            "sheet_names": [sheet["name"] for sheet in context["sheets"]],
            "has_meta_sheet": context["has_meta_sheet"],
        },
        "requirements": request.get("requirements", []),
        "operations": request["operations"],
        "preservation_rules": request.get("preservation_rules", [
            "Preserve undeclared values and formulas",
            "Preserve undeclared workbook objects and names",
            "Update _MCP_META evidence after accepted changes",
        ]),
        "validation_checks": request.get("validation_checks", [
            "metadata_contract",
            "expected_vs_observed_delta",
            "formula_error_scan",
            "visual_review",
        ]),
        "approval_required": bool(request.get("approval_required", request.get("risk_tier") == "governed_existing_workbook_rework")),
        "rollback_required": bool(request.get("rollback_required", True)),
    }
    plan_body["status"] = "awaiting_approval" if plan_body["approval_required"] else "plan_ready"
    seed_hash = canonical_json_hash(plan_body)
    plan_body["plan_id"] = f"excel-plan-{seed_hash[:16]}"
    plan_hash = canonical_json_hash(plan_body)
    plan_body["plan_hash"] = plan_hash

    text = json.dumps(plan_body, indent=2, ensure_ascii=False)
    args.output.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "plan_id": plan_body["plan_id"],
        "plan_hash": plan_hash,
        "output": str(args.output),
        "approval_required": plan_body["approval_required"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

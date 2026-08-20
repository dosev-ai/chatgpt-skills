#!/usr/bin/env python3
"""Verify workbook target identity, plan integrity, and optional approval binding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from _ooxml import canonical_json_hash, workbook_context


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="Source workbook the plan was built against")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--approved-plan-hash", help="Approval record hash to bind to this plan")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.workbook.is_file() or not args.plan.is_file():
        print(json.dumps({"status": "ERROR", "error": "Workbook or plan not found"}, indent=2))
        return 2

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a JSON object")
        stored_hash = str(plan.get("plan_hash", ""))
        hash_input = dict(plan)
        hash_input.pop("plan_hash", None)
        calculated_hash = canonical_json_hash(hash_input)
        context = workbook_context(args.workbook)
    except (json.JSONDecodeError, ValueError, zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as exc:
        payload = {"status": "ERROR", "error": str(exc)}
        code = 2
    else:
        target = plan.get("target", {}) if isinstance(plan.get("target"), dict) else {}
        plan_integrity = bool(stored_hash) and stored_hash == calculated_hash
        target_unchanged = target.get("fingerprint") == context.get("fingerprint")
        approval_required = bool(plan.get("approval_required", False))
        approval_bound = (
            not approval_required
            or (bool(args.approved_plan_hash) and args.approved_plan_hash == stored_hash)
        )
        errors: list[str] = []
        if not plan_integrity:
            errors.append("Plan hash mismatch")
        if not target_unchanged:
            errors.append("Workbook fingerprint changed since plan creation")
        if not approval_bound:
            errors.append("Approval is missing or not bound to the current plan hash")
        payload = {
            "status": "PASS" if not errors else "FAIL",
            "plan_id": plan.get("plan_id"),
            "stored_plan_hash": stored_hash,
            "calculated_plan_hash": calculated_hash,
            "plan_integrity": plan_integrity,
            "target_unchanged": target_unchanged,
            "approval_required": approval_required,
            "approval_bound": approval_bound,
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

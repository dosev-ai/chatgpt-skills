#!/usr/bin/env python3
"""Validate the governed `_MCP_META` contract in an XLSX OOXML package.

Read-only. Uses only the Python standard library. Prints a JSON report and exits
0 on pass, 1 on contract failure, 2 on input/package error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from _meta_contract_schema import NS_MAIN, NS_REL_DOC, NS_REL_PKG, OPTIONAL_TABLES, REQUIRED_TABLES
from _meta_contract_utils import _extract_rows, _read_xml, _rels_path, _resolve, _shared_strings, _sheet_cells
from _meta_contract_core import _validate_core_tables
from _meta_contract_maintenance import _validate_maintenance_extension
from _meta_contract_workflow import _validate_workflow_extension
from _meta_contract_formatting import _validate_format_extension


def validate(path: Path) -> dict[str, object]:
    report: dict[str, object] = {
        "workbook": str(path),
        "meta_sheet": "_MCP_META",
        "status": "FAIL",
        "errors": [],
        "warnings": [],
        "tables": {},
        "core_contract": {"status": "not_checked"},
        "formatting_extension": {"status": "not_checked"},
        "maintenance_extension": {"status": "not_checked"},
        "workflow_extension": {"status": "not_checked"},
    }
    errors: list[str] = report["errors"]  # type: ignore[assignment]
    warnings: list[str] = report["warnings"]  # type: ignore[assignment]

    with zipfile.ZipFile(path) as zf:
        workbook_part = "xl/workbook.xml"
        workbook = _read_xml(zf, workbook_part)
        rels = _read_xml(zf, _rels_path(workbook_part))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(f"{{{NS_REL_PKG}}}Relationship")
        }

        workbook_sheets: set[str] = set()
        meta_sheet_part: str | None = None
        for sheet in workbook.findall(f".//{{{NS_MAIN}}}sheet"):
            name = sheet.attrib.get("name", "")
            workbook_sheets.add(name)
            if name == "_MCP_META":
                rid = sheet.attrib.get(f"{{{NS_REL_DOC}}}id")
                if rid and rid in rel_map:
                    meta_sheet_part = _resolve(workbook_part, rel_map[rid])

        if not meta_sheet_part:
            errors.append("Missing `_MCP_META` worksheet")
            return report

        sheet_root = _read_xml(zf, meta_sheet_part)
        cells = _sheet_cells(sheet_root, _shared_strings(zf))
        sheet_rels_name = _rels_path(meta_sheet_part)
        if sheet_rels_name not in zf.namelist():
            errors.append("`_MCP_META` has no table relationships")
            return report

        sheet_rels = _read_xml(zf, sheet_rels_name)
        sheet_rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in sheet_rels.findall(f"{{{NS_REL_PKG}}}Relationship")
        }

        found_headers: dict[str, list[str]] = {}
        rows_by_table: dict[str, list[dict[str, str]]] = {}
        for table_part in sheet_root.findall(f".//{{{NS_MAIN}}}tablePart"):
            rid = table_part.attrib.get(f"{{{NS_REL_DOC}}}id")
            if not rid or rid not in sheet_rel_map:
                continue
            table_path = _resolve(meta_sheet_part, sheet_rel_map[rid])
            table_root = _read_xml(zf, table_path)
            name = table_root.attrib.get("displayName") or table_root.attrib.get("name") or ""
            headers = [
                col.attrib.get("name", "")
                for col in table_root.findall(f".//{{{NS_MAIN}}}tableColumn")
            ]
            found_headers[name] = headers
            table_ref = table_root.attrib.get("ref", "")
            try:
                rows_by_table[name] = _extract_rows(cells, table_ref, headers)
            except ValueError as exc:
                errors.append(f"Invalid table range for {name}: {exc}")
                rows_by_table[name] = []

        report["tables"] = found_headers
        for table_name, expected_headers in REQUIRED_TABLES.items():
            actual = found_headers.get(table_name)
            if actual is None:
                errors.append(f"Missing required table: {table_name}")
                continue
            if actual != expected_headers:
                errors.append(
                    f"Header mismatch for {table_name}: expected {expected_headers}, found {actual}"
                )

        for table_name, expected_headers in OPTIONAL_TABLES.items():
            actual = found_headers.get(table_name)
            if actual is not None and actual != expected_headers:
                errors.append(
                    f"Header mismatch for {table_name}: expected {expected_headers}, found {actual}"
                )

        known = set(REQUIRED_TABLES) | set(OPTIONAL_TABLES)
        unexpected = sorted(set(found_headers) - known)
        if unexpected:
            warnings.append(f"Additional metadata tables present: {unexpected}")

        report["core_contract"] = _validate_core_tables(
            rows_by_table,
            set(found_headers),
            workbook_sheets,
            errors,
            warnings,
        )
        report["maintenance_extension"] = _validate_maintenance_extension(
            rows_by_table,
            set(found_headers),
            errors,
        )
        report["workflow_extension"] = _validate_workflow_extension(
            rows_by_table,
            set(found_headers),
            workbook_sheets,
            errors,
        )
        report["formatting_extension"] = _validate_format_extension(
            rows_by_table,
            set(found_headers),
            workbook_sheets,
            errors,
        )

    report["status"] = "PASS" if not errors else "FAIL"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    if not args.workbook.is_file():
        print(json.dumps({"status": "ERROR", "error": "Workbook not found"}, indent=2))
        return 2

    try:
        report = validate(args.workbook)
    except (zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as exc:
        report = {"status": "ERROR", "workbook": str(args.workbook), "error": str(exc)}
        code = 2
    else:
        code = 0 if report["status"] == "PASS" else 1

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    print(payload)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

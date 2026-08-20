#!/usr/bin/env python3
"""Shared read-only OOXML helpers for governed Excel skill scripts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CELL_RE = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")

VOLATILE_PREFIXES = (
    "xl/printerSettings/",
)
VOLATILE_PARTS = {
    "xl/calcChain.xml",
}


def resolve_part(base: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base_dir = PurePosixPath(base).parent
    combined = base_dir.joinpath(target)
    parts: list[str] = []
    for part in combined.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


def rels_path(part_path: str) -> str:
    p = PurePosixPath(part_path)
    return str(p.parent / "_rels" / f"{p.name}.rels")


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    with zf.open(name) as handle:
        return ET.parse(handle).getroot()


def canonical_json_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_part_bytes(name: str, raw: bytes) -> bytes:
    if name.lower().endswith((".xml", ".rels")):
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return raw
        if name == "docProps/core.xml":
            volatile_core_fields = {"created", "modified", "lastPrinted"}
            for child in list(root):
                local_name = child.tag.rsplit("}", 1)[-1]
                if local_name in volatile_core_fields:
                    root.remove(child)
        return ET.tostring(root, encoding="utf-8")
    return raw


def is_volatile_part(name: str) -> bool:
    return name in VOLATILE_PARTS or any(name.startswith(prefix) for prefix in VOLATILE_PREFIXES)


def package_part_hashes(path: Path, *, include_volatile: bool = False) -> dict[str, str]:
    hashes: dict[str, str] = {}
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if name.endswith("/"):
                continue
            if not include_volatile and is_volatile_part(name):
                continue
            raw = zf.read(name)
            hashes[name] = hashlib.sha256(canonical_part_bytes(name, raw)).hexdigest()
    return hashes


def package_fingerprint(path: Path, *, include_volatile: bool = False) -> str:
    return canonical_json_hash(package_part_hashes(path, include_volatile=include_volatile))


def workbook_sheet_parts(zf: zipfile.ZipFile) -> dict[str, dict[str, str]]:
    workbook_part = "xl/workbook.xml"
    workbook = read_xml(zf, workbook_part)
    rels = read_xml(zf, rels_path(workbook_part))
    rel_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{NS_REL_PKG}}}Relationship")
    }
    result: dict[str, dict[str, str]] = {}
    for sheet in workbook.findall(f".//{{{NS_MAIN}}}sheet"):
        name = sheet.attrib.get("name", "")
        rid = sheet.attrib.get(f"{{{NS_REL_DOC}}}id", "")
        target = rel_map.get(rid, "")
        if not name or not target:
            continue
        result[name] = {
            "part": resolve_part(workbook_part, target),
            "state": sheet.attrib.get("state", "visible"),
            "sheet_id": sheet.attrib.get("sheetId", ""),
        }
    return result


def workbook_defined_names(zf: zipfile.ZipFile) -> list[dict[str, str]]:
    workbook = read_xml(zf, "xl/workbook.xml")
    names: list[dict[str, str]] = []
    for node in workbook.findall(f".//{{{NS_MAIN}}}definedName"):
        names.append({
            "name": node.attrib.get("name", ""),
            "local_sheet_id": node.attrib.get("localSheetId", ""),
            "hidden": node.attrib.get("hidden", "0"),
            "refers_to": node.text or "",
        })
    return names


def shared_strings(zf: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in zf.namelist():
        return []
    root = read_xml(zf, name)
    values: list[str] = []
    for si in root.findall(f"{{{NS_MAIN}}}si"):
        values.append("".join(node.text or "" for node in si.iter(f"{{{NS_MAIN}}}t")))
    return values


def cell_value(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{{{NS_MAIN}}}t"))
    value_node = cell.find(f"{{{NS_MAIN}}}v")
    raw = "" if value_node is None or value_node.text is None else value_node.text
    if cell_type == "s" and raw:
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return raw
    return raw


def worksheet_tables(zf: zipfile.ZipFile, sheet_part: str) -> list[dict[str, str]]:
    root = read_xml(zf, sheet_part)
    rel_name = rels_path(sheet_part)
    if rel_name not in zf.namelist():
        return []
    rels = read_xml(zf, rel_name)
    rel_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{NS_REL_PKG}}}Relationship")
    }
    tables: list[dict[str, str]] = []
    for table_part in root.findall(f".//{{{NS_MAIN}}}tablePart"):
        rid = table_part.attrib.get(f"{{{NS_REL_DOC}}}id", "")
        target = rel_map.get(rid, "")
        if not target:
            continue
        table_path = resolve_part(sheet_part, target)
        table_root = read_xml(zf, table_path)
        tables.append({
            "name": table_root.attrib.get("displayName") or table_root.attrib.get("name") or "",
            "ref": table_root.attrib.get("ref", ""),
            "part": table_path,
        })
    return tables


def workbook_context(path: Path) -> dict[str, object]:
    part_hashes = package_part_hashes(path)
    with zipfile.ZipFile(path) as zf:
        shared = shared_strings(zf)
        sheet_map = workbook_sheet_parts(zf)
        sheet_summaries: list[dict[str, object]] = []
        total_formulas = 0
        total_error_cells = 0
        for sheet_name, info in sheet_map.items():
            root = read_xml(zf, info["part"])
            dimension = root.find(f"{{{NS_MAIN}}}dimension")
            formulas = root.findall(f".//{{{NS_MAIN}}}f")
            error_cells = [
                cell for cell in root.findall(f".//{{{NS_MAIN}}}c")
                if cell.attrib.get("t") == "e"
            ]
            cells = root.findall(f".//{{{NS_MAIN}}}c")
            total_formulas += len(formulas)
            total_error_cells += len(error_cells)
            tables = worksheet_tables(zf, info["part"])
            sheet_summaries.append({
                "name": sheet_name,
                "state": info["state"],
                "sheet_id": info["sheet_id"],
                "part": info["part"],
                "dimension": "" if dimension is None else dimension.attrib.get("ref", ""),
                "cell_count": len(cells),
                "formula_count": len(formulas),
                "error_cell_count": len(error_cells),
                "tables": tables,
            })

        chart_parts = sorted(name for name in zf.namelist() if name.startswith("xl/charts/") and name.endswith(".xml"))
        drawing_parts = sorted(name for name in zf.namelist() if name.startswith("xl/drawings/") and name.endswith(".xml"))
        pivot_parts = sorted(name for name in zf.namelist() if name.startswith("xl/pivot") and name.endswith(".xml"))

    return {
        "workbook": str(path),
        "fingerprint": package_fingerprint(path),
        "part_count": len(part_hashes),
        "sheet_count": len(sheet_summaries),
        "sheets": sheet_summaries,
        "defined_names": workbook_defined_names_from_path(path),
        "formula_count": total_formulas,
        "error_cell_count": total_error_cells,
        "chart_count": len(chart_parts),
        "drawing_count": len(drawing_parts),
        "pivot_part_count": len(pivot_parts),
        "has_meta_sheet": any(sheet["name"] == "_MCP_META" for sheet in sheet_summaries),
    }


def workbook_defined_names_from_path(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as zf:
        return workbook_defined_names(zf)


def sheet_part_to_name(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as zf:
        return {info["part"]: name for name, info in workbook_sheet_parts(zf).items()}

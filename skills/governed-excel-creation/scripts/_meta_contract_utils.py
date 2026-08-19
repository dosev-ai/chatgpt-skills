"""OOXML and normalized-table helpers for metadata validation."""

from pathlib import PurePosixPath
import zipfile
import xml.etree.ElementTree as ET

from _meta_contract_schema import CELL_RE, NS_MAIN, YES_NO


def _resolve(base: str, target: str) -> str:
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


def _rels_path(part_path: str) -> str:
    p = PurePosixPath(part_path)
    return str(p.parent / "_rels" / f"{p.name}.rels")


def _read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    with zf.open(name) as f:
        return ET.parse(f).getroot()


def _col_number(letters: str) -> int:
    value = 0
    for ch in letters:
        value = value * 26 + ord(ch) - 64
    return value


def _range_bounds(ref: str) -> tuple[int, int, int, int]:
    clean = ref.replace("$", "").upper()
    parts = clean.split(":")
    if len(parts) == 1:
        parts.append(parts[0])
    if len(parts) != 2:
        raise ValueError(f"Invalid range: {ref}")
    m1 = CELL_RE.match(parts[0])
    m2 = CELL_RE.match(parts[1])
    if not m1 or not m2:
        raise ValueError(f"Invalid range: {ref}")
    return _col_number(m1.group(1)), int(m1.group(2)), _col_number(m2.group(1)), int(m2.group(2))


def _shared_strings(zf: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in zf.namelist():
        return []
    root = _read_xml(zf, name)
    values: list[str] = []
    for si in root.findall(f"{{{NS_MAIN}}}si"):
        text = "".join(node.text or "" for node in si.iter(f"{{{NS_MAIN}}}t"))
        values.append(text)
    return values


def _sheet_cells(sheet_root: ET.Element, shared: list[str]) -> dict[tuple[int, int], str]:
    cells: dict[tuple[int, int], str] = {}
    for cell in sheet_root.findall(f".//{{{NS_MAIN}}}c"):
        ref = cell.attrib.get("r", "").replace("$", "").upper()
        match = CELL_RE.match(ref)
        if not match:
            continue
        key = (_col_number(match.group(1)), int(match.group(2)))
        cell_type = cell.attrib.get("t")
        if cell_type == "inlineStr":
            value = "".join(node.text or "" for node in cell.iter(f"{{{NS_MAIN}}}t"))
        else:
            v = cell.find(f"{{{NS_MAIN}}}v")
            raw = "" if v is None or v.text is None else v.text
            if cell_type == "s" and raw:
                try:
                    value = shared[int(raw)]
                except (ValueError, IndexError):
                    value = raw
            elif cell_type == "b":
                value = "Yes" if raw == "1" else "No"
            else:
                value = raw
        cells[key] = value
    return cells


def _extract_rows(cells: dict[tuple[int, int], str], ref: str, headers: list[str]) -> list[dict[str, str]]:
    min_col, min_row, max_col, max_row = _range_bounds(ref)
    rows: list[dict[str, str]] = []
    for row_num in range(min_row + 1, max_row + 1):
        values = [cells.get((col_num, row_num), "") for col_num in range(min_col, max_col + 1)]
        if not any(str(value).strip() for value in values):
            continue
        rows.append({header: values[idx] if idx < len(values) else "" for idx, header in enumerate(headers)})
    return rows


def _nonblank_rows(rows: list[dict[str, str]], id_field: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get(id_field, "").strip()]


def _check_unique(rows: list[dict[str, str]], field: str, table: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        value = row.get(field, "").strip()
        if not value:
            errors.append(f"Blank {field} in {table}")
        elif value in seen:
            errors.append(f"Duplicate {field} {value!r} in {table}")
        else:
            seen.add(value)
    return seen


def _validate_integer(value: str, label: str, errors: list[str]) -> None:
    try:
        int(value)
    except ValueError:
        errors.append(f"{label} must be an integer, found {value!r}")


def _validate_yes_no(value: str, label: str, errors: list[str]) -> None:
    if value not in YES_NO:
        errors.append(f"{label} must be Yes or No, found {value!r}")


def _validate_inheritance(styles: list[dict[str, str]], style_ids: set[str], errors: list[str]) -> None:
    parents: dict[str, str] = {}
    for row in styles:
        style_id = row["Style_ID"].strip()
        parent = row.get("Inherits_From", "").strip()
        if parent:
            if parent not in style_ids:
                errors.append(f"Style {style_id!r} inherits from missing style {parent!r}")
            parents[style_id] = parent

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, path: list[str]) -> None:
        if node in visited:
            return
        if node in visiting:
            cycle = " -> ".join(path + [node])
            errors.append(f"Style inheritance cycle: {cycle}")
            return
        visiting.add(node)
        parent = parents.get(node)
        if parent in style_ids:
            visit(parent, path + [node])
        visiting.remove(node)
        visited.add(node)

    for style_id in style_ids:
        visit(style_id, [])

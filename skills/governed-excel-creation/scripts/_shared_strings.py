"""Attribute shared-string table changes to worksheet names that reference them."""

from __future__ import annotations

from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from _ooxml import sheet_part_to_name

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
SHARED_STRINGS_PART = "xl/sharedStrings.xml"


def _shared_string_entries(workbook: Path) -> list[bytes]:
    with zipfile.ZipFile(workbook) as archive:
        if SHARED_STRINGS_PART not in archive.namelist():
            return []
        root = ET.fromstring(archive.read(SHARED_STRINGS_PART))
    return [ET.tostring(item, encoding="utf-8") for item in root.findall(f"{{{MAIN_NS}}}si")]


def changed_shared_string_indices(before: Path, after: Path) -> set[int]:
    """Return shared-string indices whose serialized `<si>` entries changed."""
    before_entries = _shared_string_entries(before)
    after_entries = _shared_string_entries(after)
    return {
        index
        for index in range(max(len(before_entries), len(after_entries)))
        if (before_entries[index] if index < len(before_entries) else None)
        != (after_entries[index] if index < len(after_entries) else None)
    }


def _reference_map(workbook: Path, indices: set[int]) -> dict[int, set[str]]:
    references = {index: set() for index in indices}
    if not indices:
        return references
    part_to_name = sheet_part_to_name(workbook)
    with zipfile.ZipFile(workbook) as archive:
        names = set(archive.namelist())
        for part, sheet_name in part_to_name.items():
            if part not in names:
                continue
            root = ET.fromstring(archive.read(part))
            for cell in root.findall(f".//{{{MAIN_NS}}}c[@t='s']"):
                value = cell.find(f"{{{MAIN_NS}}}v")
                if value is None or value.text is None:
                    continue
                try:
                    index = int(value.text)
                except ValueError:
                    continue
                if index in references:
                    references[index].add(sheet_name)
    return references


def shared_string_change_attribution(before: Path, after: Path) -> dict[int, set[str]]:
    """Map each changed shared-string index to sheets referencing it before or after."""
    indices = changed_shared_string_indices(before, after)
    before_refs = _reference_map(before, indices)
    after_refs = _reference_map(after, indices)
    return {
        index: before_refs.get(index, set()) | after_refs.get(index, set())
        for index in sorted(indices)
    }


def shared_string_impacted_sheets(before: Path, after: Path) -> set[str]:
    """Return impacted sheets only when every changed index is attributable."""
    attribution = shared_string_change_attribution(before, after)
    if not attribution or any(not sheets for sheets in attribution.values()):
        return set()
    return set().union(*attribution.values())


__all__ = [
    "SHARED_STRINGS_PART",
    "changed_shared_string_indices",
    "shared_string_change_attribution",
    "shared_string_impacted_sheets",
]

#!/usr/bin/env python3
"""Hardened entrypoint for downstream public skill validation.

The reviewed baseline implementation is retained in ``validate_public_skills_base``.
This entrypoint adds alignment-safe binary scanning and section-scoped canonical
lineage validation while preserving the established validation API used by tests.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_BASE_PATH = Path(__file__).with_name("validate_public_skills_base.py")
_SPEC = importlib.util.spec_from_file_location("_validate_public_skills_base", _BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to load public skill validator baseline")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

ROOT = _base.ROOT
MANIFEST = _base.MANIFEST
SCHEMA = _base.SCHEMA
SKILLS_DIR = _base.SKILLS_DIR

_original_validate_skill = _base.validate_skill

CANONICAL_LINEAGE_PREFIXES = (
    "- Canonical repository:",
    "- Canonical path:",
    "- Canonical version:",
    "- Canonical source PR:",
    "- Canonical final PR HEAD:",
    "- Canonical merge commit:",
)


def _sync_paths() -> None:
    """Propagate test-patched path globals into the baseline module."""

    _base.ROOT = ROOT
    _base.MANIFEST = MANIFEST
    _base.SCHEMA = SCHEMA
    _base.SKILLS_DIR = SKILLS_DIR


def scan_bytes_for_forbidden(data: bytes, source: str) -> None:
    """Scan ASCII and both UTF-16 byte orders at both possible alignments."""

    _base.scan_text(data.decode("latin-1"), source)
    for offset in (0, 1):
        aligned = data[offset:]
        _base.scan_text(aligned.decode("utf-16-le", errors="ignore"), source)
        _base.scan_text(aligned.decode("utf-16-be", errors="ignore"), source)


def _section_indices(lines: list[str], heading: str, skill_id: str) -> set[int]:
    matches = [index for index, line in enumerate(lines) if line == heading]
    if len(matches) != 1:
        _base.fail(f"README.md requires exactly one {heading!r} section for {skill_id}")
    start = matches[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return set(range(start, end))


def validate_canonical_lineage(
    lines: list[str], canonical: dict[str, Any], skill_id: str
) -> None:
    """Bind canonical lineage exactly and uniquely to its README section."""

    section_indices = _section_indices(lines, "## Canonical lineage", skill_id)
    expected_lines = (
        f"- Canonical repository: `{canonical['repository']}`",
        f"- Canonical path: `{canonical['path']}`",
        f"- Canonical version: `{canonical['version']}`",
        f"- Canonical source PR: `#{canonical['source_pr']}`",
        f"- Canonical final PR HEAD: `{canonical['final_pr_head']}`",
        f"- Canonical merge commit: `{canonical['merge_commit']}`",
    )

    for prefix, expected in zip(CANONICAL_LINEAGE_PREFIXES, expected_lines):
        matches = [
            (index, line)
            for index, line in enumerate(lines)
            if line.startswith(prefix)
        ]
        if len(matches) != 1:
            _base.fail(
                f"README.md requires exactly one {prefix!r} field for {skill_id}; "
                f"found {len(matches)}"
            )
        index, actual = matches[0]
        if index not in section_indices:
            _base.fail(
                f"README.md field {prefix!r} must appear inside the Canonical lineage "
                f"section for {skill_id}"
            )
        if actual != expected:
            _base.fail(
                f"README.md canonical lineage differs from manifest for {skill_id}: "
                f"expected {expected!r}, found {actual!r}"
            )


def validate_skill(entry: dict[str, Any], repository_license_status: str) -> None:
    _sync_paths()
    _original_validate_skill(entry, repository_license_status)

    skill_dir = ROOT / entry["path"]
    if entry["release_state"] == "not-candidate" and not skill_dir.exists():
        return

    lines = (skill_dir / "README.md").read_text(encoding="utf-8").splitlines()
    validate_canonical_lineage(lines, entry["canonical"], entry["id"])


_base.scan_bytes_for_forbidden = scan_bytes_for_forbidden
_base.validate_skill = validate_skill


def main() -> int:
    _sync_paths()
    return _base.main()


def __getattr__(name: str) -> Any:
    return getattr(_base, name)


if __name__ == "__main__":
    raise SystemExit(main())

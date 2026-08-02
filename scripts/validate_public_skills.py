#!/usr/bin/env python3
"""Hardened entrypoint for downstream public skill validation.

The reviewed baseline implementation is retained in ``validate_public_skills_base``.
This entrypoint adds alignment-safe binary scanning, section-scoped canonical
lineage validation, cache-path scanning, MIT-only public licensing, and
nonblank release residuals while preserving the established validation API.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# Loading the baseline must not generate untracked bytecode inside a cache-named
# directory before the complete-tree scan runs. Tracked files in those paths are
# still scanned because ``should_ignore`` excludes Git metadata only.
sys.dont_write_bytecode = True

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
_original_validate_release_evidence = _base.validate_release_evidence

CANONICAL_LINEAGE_PREFIXES = (
    "- Canonical repository:",
    "- Canonical path:",
    "- Canonical version:",
    "- Canonical source PR:",
    "- Canonical final PR HEAD:",
    "- Canonical merge commit:",
)
APPROVED_PUBLIC_SKILL_LICENSE = "MIT"


def _sync_paths() -> None:
    """Propagate test-patched path globals into the baseline module."""

    _base.ROOT = ROOT
    _base.MANIFEST = MANIFEST
    _base.SCHEMA = SCHEMA
    _base.SKILLS_DIR = SKILLS_DIR


def should_ignore(path: Path) -> bool:
    """Ignore Git metadata only; cache-named paths may contain tracked public files."""

    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True
    return ".git" in relative.parts


def scan_bytes_for_forbidden(data: bytes, source: str) -> None:
    """Scan ASCII and both UTF-16 byte orders at both possible alignments."""

    _base.scan_text(data.decode("latin-1"), source)
    for offset in (0, 1):
        aligned = data[offset:]
        _base.scan_text(aligned.decode("utf-16-le", errors="ignore"), source)
        _base.scan_text(aligned.decode("utf-16-be", errors="ignore"), source)


def validate_release_evidence(
    entry: dict[str, Any], repository_license_status: str, has_public_directory: bool
) -> None:
    """Apply baseline evidence checks plus the approved MIT and residual contracts."""

    _original_validate_release_evidence(entry, repository_license_status, has_public_directory)

    release_state = entry["release_state"]
    licensed_states = {
        "public-pr-open",
        "public-merged-verification-pending",
        "public-released",
    }
    if has_public_directory or release_state in licensed_states:
        if entry["license"].strip() != APPROVED_PUBLIC_SKILL_LICENSE:
            _base.fail(
                f"public skill directory requires per-skill license "
                f"{APPROVED_PUBLIC_SKILL_LICENSE}: {entry['id']}"
            )

    if release_state == "public-released":
        residuals = entry.get("residuals")
        if not isinstance(residuals, list) or any(
            not isinstance(residual, str) or not residual.strip()
            for residual in residuals
        ):
            _base.fail(
                f"public-released skill residuals must contain only nonblank text: "
                f"{entry['id']}"
            )


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


_base.should_ignore = should_ignore
_base.scan_bytes_for_forbidden = scan_bytes_for_forbidden
_base.validate_release_evidence = validate_release_evidence
_base.validate_skill = validate_skill


def main() -> int:
    _sync_paths()
    return _base.main()


def __getattr__(name: str) -> Any:
    return getattr(_base, name)


if __name__ == "__main__":
    raise SystemExit(main())

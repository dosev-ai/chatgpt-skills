#!/usr/bin/env python3
"""Validate that every public skill has useful reader-facing documentation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

REQUIRED_HEADINGS = (
    "## What it does",
    "## Why it exists",
    "## Benefits",
    "## When to use it",
    "## How it works",
    "## Limitations",
    "## Canonical lineage",
    "## Release status",
)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def section_body(lines: list[str], heading_index: int) -> str:
    body: list[str] = []
    for line in lines[heading_index + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


def validate_readme(skill_dir: Path) -> None:
    readme = skill_dir / "README.md"
    if not readme.is_file() or readme.is_symlink():
        fail(f"public skill requires a regular README.md: {skill_dir.name}")

    text = readme.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or not lines[0].startswith("# "):
        fail(f"README.md requires an H1 title: {skill_dir.name}")

    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        matches = [index for index, line in enumerate(lines) if line == heading]
        if len(matches) != 1:
            fail(
                f"README.md requires exactly one {heading!r} section: {skill_dir.name}"
            )
        heading_index = matches[0]
        positions.append(heading_index)
        if not section_body(lines, heading_index):
            fail(f"README.md section {heading!r} must not be empty: {skill_dir.name}")

    if positions != sorted(positions):
        fail(f"README.md required sections are out of order: {skill_dir.name}")


def main() -> int:
    skill_dirs = (
        sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
        if SKILLS_DIR.exists()
        else []
    )

    for skill_dir in skill_dirs:
        validate_readme(skill_dir)

    print(f"Public Skill README Validation PASS: {len(skill_dirs)} skill README(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

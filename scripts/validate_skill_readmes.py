#!/usr/bin/env python3
"""Validate that every public skill has useful, manifest-aligned documentation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MANIFEST = ROOT / "skills-manifest.yaml"

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


def expected_release_lines(entry: dict[str, Any]) -> tuple[str, ...]:
    public_pr = f"#{entry['public_pr']}" if "public_pr" in entry else "not yet opened"
    verification = entry.get("verification", "pending").strip()
    residuals = entry.get("residuals")
    if residuals is None:
        residual_text = "pending"
    elif not residuals:
        residual_text = "none"
    else:
        residual_text = "; ".join(residuals)

    return (
        f"- Public release state: `{entry['release_state']}`",
        f"- Public pull request: `{public_pr}`",
        f"- Artifact status: `{entry['artifact_status']}`",
        f"- Clean-room verification: `{verification}`",
        f"- Known residuals: `{residual_text}`",
    )


def validate_readme(skill_dir: Path, entry: dict[str, Any]) -> None:
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

    line_set = set(lines)
    for expected in expected_release_lines(entry):
        if expected not in line_set:
            fail(
                f"README.md release status differs from manifest for {skill_dir.name}: "
                f"missing {expected!r}"
            )


def load_manifest_entries() -> dict[str, dict[str, Any]]:
    if not MANIFEST.is_file():
        fail("skills-manifest.yaml is missing")
    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        fail(f"invalid YAML in skills-manifest.yaml: {exc}")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("skills"), list):
        fail("skills-manifest.yaml requires a skills list")
    entries: dict[str, dict[str, Any]] = {}
    for entry in manifest["skills"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            fail("skills-manifest.yaml contains an invalid skill entry")
        entries[entry["id"]] = entry
    return entries


def main() -> int:
    entries = load_manifest_entries()
    skill_dirs = (
        sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
        if SKILLS_DIR.exists()
        else []
    )

    for skill_dir in skill_dirs:
        entry = entries.get(skill_dir.name)
        if entry is None:
            fail(f"public skill README has no manifest entry: {skill_dir.name}")
        validate_readme(skill_dir, entry)

    print(f"Public Skill README Validation PASS: {len(skill_dirs)} skill README(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

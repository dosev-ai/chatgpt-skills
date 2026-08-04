#!/usr/bin/env python3
"""Require PR-open public skill packages to exist and match their source tree."""

from __future__ import annotations

import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills-manifest.yaml"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_entries() -> list[dict[str, Any]]:
    if not MANIFEST.is_file():
        fail("skills-manifest.yaml is missing")
    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        fail(f"invalid YAML in skills-manifest.yaml: {exc}")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("skills"), list):
        fail("skills-manifest.yaml requires a skills list")
    entries = manifest["skills"]
    if any(not isinstance(entry, dict) for entry in entries):
        fail("skills-manifest.yaml contains an invalid skill entry")
    return entries


def safe_member_name(name: str, skill_id: str) -> str:
    if not name or "\\" in name:
        fail(f"invalid package member path for {skill_id}: {name!r}")
    member = PurePosixPath(name)
    if member.is_absolute() or any(part in {"", ".", ".."} for part in member.parts):
        fail(f"invalid package member path for {skill_id}: {name!r}")
    return member.as_posix()


def expected_source(skill_dir: Path, package_path: Path, skill_id: str) -> dict[str, bytes]:
    expected: dict[str, bytes] = {}
    for path in sorted(skill_dir.rglob("*")):
        if path == package_path or path.is_dir():
            continue
        if path.is_symlink() or not path.is_file():
            fail(f"public package source requires regular files for {skill_id}: {path}")
        expected[path.relative_to(skill_dir).as_posix()] = path.read_bytes()
    return expected


def actual_package(package_path: Path, skill_id: str) -> dict[str, bytes]:
    actual: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(package_path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                name = safe_member_name(info.filename, skill_id)
                if name in actual:
                    fail(f"duplicate package member for {skill_id}: {name}")
                mode = (info.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                if file_type not in (0, stat.S_IFREG):
                    fail(f"non-regular package member for {skill_id}: {name}")
                actual[name] = archive.read(info)
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        fail(f"invalid skill.zip for {skill_id}: {exc}")
    return actual


def validate_entry(entry: dict[str, Any]) -> None:
    skill_id = entry.get("id")
    skill_path = entry.get("path")
    if not isinstance(skill_id, str) or not isinstance(skill_path, str):
        fail("package entry requires text id and path")
    skill_dir = ROOT / skill_path
    package_path = skill_dir / "skill.zip"
    try:
        skill_dir.resolve().relative_to(ROOT.resolve())
        package_path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        fail(f"public package path escapes repository root: {skill_id}")
    if package_path.is_symlink() or not package_path.is_file():
        fail(f"public-pr-open package requires regular artifact {skill_path}/skill.zip: {skill_id}")

    expected = expected_source(skill_dir, package_path, skill_id)
    actual = actual_package(package_path, skill_id)
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        fail(
            f"PR-open package contents differ from public skill tree for {skill_id}; "
            f"missing={missing}, extra={extra}"
        )
    for name, expected_bytes in expected.items():
        if actual[name] != expected_bytes:
            fail(f"PR-open package member differs from public skill tree for {skill_id}: {name}")


def main() -> int:
    validated = 0
    for entry in load_entries():
        if entry.get("release_state") == "public-pr-open" and entry.get("artifact_status") == "package":
            validate_entry(entry)
            validated += 1
    print(f"PR-open Package Parity PASS: {validated} package(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

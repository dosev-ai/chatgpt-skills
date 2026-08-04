#!/usr/bin/env python3
"""Require PR-open public skill packages and evidence to match their source tree."""

from __future__ import annotations

import hashlib
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills-manifest.yaml"
SHA256_PATTERN = re.compile(r"^([0-9a-f]{64})  (.+)$")


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


def regular_evidence_file(path: Path, skill_id: str) -> Path:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        fail(f"package evidence path escapes repository root: {skill_id}")
    if path.is_symlink() or not path.is_file():
        fail(f"PR-open package requires regular evidence file for {skill_id}: {path.relative_to(ROOT)}")
    return path


def validate_external_evidence(
    entry: dict[str, Any], package_path: Path, expected_paths: list[str]
) -> None:
    skill_id = entry["id"]
    skill_path = entry["path"]
    version = entry.get("version")
    if not isinstance(version, str) or not version.strip():
        fail(f"package entry requires text version: {skill_id}")
    evidence_base = ROOT / "release-evidence" / f"{skill_id}-v{version}-package"
    checksum_path = regular_evidence_file(
        Path(f"{evidence_base}.sha256"), skill_id
    )
    size_path = regular_evidence_file(Path(f"{evidence_base}.size"), skill_id)
    inventory_path = regular_evidence_file(
        Path(f"{evidence_base}.inventory"), skill_id
    )

    checksum_text = checksum_path.read_text(encoding="utf-8").strip()
    match = SHA256_PATTERN.fullmatch(checksum_text)
    expected_package_path = f"{skill_path}/skill.zip"
    if match is None or match.group(2) != expected_package_path:
        fail(f"invalid PR-open package checksum record for {skill_id}")
    expected_sha256 = match.group(1)
    actual_sha256 = hashlib.sha256(package_path.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        fail(
            f"PR-open package checksum differs from release evidence for {skill_id}: "
            f"expected={expected_sha256}, actual={actual_sha256}"
        )

    size_text = size_path.read_text(encoding="utf-8").strip()
    if not size_text.isdigit():
        fail(f"invalid PR-open package size record for {skill_id}")
    expected_size = int(size_text)
    actual_size = package_path.stat().st_size
    if actual_size != expected_size:
        fail(
            f"PR-open package size differs from release evidence for {skill_id}: "
            f"expected={expected_size}, actual={actual_size}"
        )

    inventory = [
        line.strip()
        for line in inventory_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if inventory != sorted(expected_paths):
        fail(
            f"PR-open package inventory differs from public skill tree for {skill_id}: "
            f"expected={sorted(expected_paths)}, actual={inventory}"
        )


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

    validate_external_evidence(entry, package_path, sorted(expected))


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

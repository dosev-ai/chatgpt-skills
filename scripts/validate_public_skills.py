#!/usr/bin/env python3
"""Hardened entrypoint for downstream public skill validation.

The reviewed baseline implementation is retained in ``validate_public_skills_base``.
This entrypoint adds complete byte and path scanning, exact MIT validation,
section-scoped lineage, structured release evidence, and deterministic package
parity while preserving the established validation API.
"""

from __future__ import annotations

import bz2
import hashlib
import importlib.util
import io
import lzma
import struct
import sys
import tarfile
import zipfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Any

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

_original_scan_zip_archive = _base.scan_zip_archive
_original_scan_tar_archive = _base.scan_tar_archive
_original_validate_archive_member_name = _base.validate_archive_member_name
_original_validate_root_contract = _base.validate_root_contract
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
RAW_TAR_OVERHEAD_BYTES = (_base.MAX_ARCHIVE_ENTRIES + 8) * 1024
EXPECTED_MIT_LICENSE = """MIT License

Copyright (c) 2026 Delyan Dosev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def _sync_paths() -> None:
    _base.ROOT = ROOT
    _base.MANIFEST = MANIFEST
    _base.SCHEMA = SCHEMA
    _base.SKILLS_DIR = SKILLS_DIR


def should_ignore(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True
    return ".git" in relative.parts


def scan_bytes_for_forbidden(data: bytes, source: str) -> None:
    _base.scan_text(data.decode("latin-1"), source)
    for offset in (0, 1):
        aligned = data[offset:]
        _base.scan_text(aligned.decode("utf-16-le", errors="ignore"), source)
        _base.scan_text(aligned.decode("utf-16-be", errors="ignore"), source)


def scan_public_path(relative: Path) -> None:
    _base.scan_text(relative.as_posix(), f"public path {relative.as_posix()}")


def validate_archive_member_name(name: str, archive_source: str) -> PurePosixPath:
    member_path = _original_validate_archive_member_name(name, archive_source)
    _base.scan_text(name, f"archive member path {archive_source}!{name}")
    return member_path


def scan_archive_member(data: bytes, name: str, archive_source: str) -> None:
    member_path = validate_archive_member_name(name, archive_source)
    source = f"{archive_source}!{name}"
    suffix = member_path.suffix.lower()
    if suffix in _base.BINARY_SUFFIXES:
        _base.scan_binary(data, suffix, source)
        return
    scan_bytes_for_forbidden(data, source)
    if b"\x00" in data:
        _base.fail(f"unapproved binary artifact in archive: {source}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        _base.fail(f"archive member is not UTF-8 text or an approved binary type: {source}")
    _base.scan_text(text, source)


def scan_zip_archive(data: bytes, archive_source: str) -> None:
    """Scan ZIP metadata before the baseline bounded content inspection."""

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            scan_bytes_for_forbidden(archive.comment, f"{archive_source}!archive-comment")
            for info in archive.infolist():
                scan_bytes_for_forbidden(
                    info.comment, f"{archive_source}!{info.filename}:entry-comment"
                )
                scan_bytes_for_forbidden(
                    info.extra, f"{archive_source}!{info.filename}:extra-field"
                )
    except (zipfile.BadZipFile, RuntimeError) as exc:
        _base.fail(f"invalid ZIP archive {archive_source}: {exc}")
    _original_scan_zip_archive(data, archive_source)


def _scan_tar_metadata_value(value: Any, source: str) -> None:
    if value is None:
        return
    if isinstance(value, bytes):
        scan_bytes_for_forbidden(value, source)
        return
    _base.scan_text(str(value), source)


def _scan_tar_metadata_mapping(mapping: Any, source: str) -> None:
    if not isinstance(mapping, dict):
        return
    for key, value in mapping.items():
        _scan_tar_metadata_value(key, f"{source}:key")
        _scan_tar_metadata_value(value, f"{source}:{key}")


def _read_gzip_c_string(data: bytes, index: int, source: str) -> int:
    end = data.find(b"\x00", index)
    if end < 0:
        _base.fail(f"unterminated gzip metadata field in {source}")
    scan_bytes_for_forbidden(data[index:end], source)
    return end + 1


def _parse_gzip_member_header(
    data: bytes, index: int, archive_source: str, member_number: int
) -> int:
    """Scan one gzip member header and return the raw DEFLATE start offset."""

    member_source = f"{archive_source}!gzip-member-{member_number}"
    if index + 10 > len(data) or data[index : index + 2] != b"\x1f\x8b":
        _base.fail(f"invalid gzip member header in {member_source}")
    if data[index + 2] != 8:
        _base.fail(f"unsupported gzip compression method in {member_source}")
    flags = data[index + 3]
    if flags & 0xE0:
        _base.fail(f"reserved gzip flags are set in {member_source}")
    cursor = index + 10
    if flags & 0x04:
        if cursor + 2 > len(data):
            _base.fail(f"truncated gzip extra-length field in {member_source}")
        extra_length = int.from_bytes(data[cursor : cursor + 2], "little")
        cursor += 2
        if cursor + extra_length > len(data):
            _base.fail(f"truncated gzip extra field in {member_source}")
        scan_bytes_for_forbidden(
            data[cursor : cursor + extra_length],
            f"{member_source}:extra",
        )
        cursor += extra_length
    if flags & 0x08:
        cursor = _read_gzip_c_string(
            data,
            cursor,
            f"{member_source}:filename",
        )
    if flags & 0x10:
        cursor = _read_gzip_c_string(
            data,
            cursor,
            f"{member_source}:comment",
        )
    if flags & 0x02:
        if cursor + 2 > len(data):
            _base.fail(f"truncated gzip header CRC in {member_source}")
        cursor += 2
    return cursor


def _scan_and_decompress_gzip_members(
    data: bytes, archive_source: str, limit: int
) -> bytes:
    """Scan and bounded-decompress every concatenated gzip member."""

    output = bytearray()
    index = 0
    member_number = 0
    while index < len(data):
        if data[index : index + 2] != b"\x1f\x8b":
            trailing = data[index:]
            scan_bytes_for_forbidden(trailing, f"{archive_source}!gzip-trailing-data")
            if trailing and all(byte == 0 for byte in trailing):
                break
            _base.fail(f"unexpected trailing data after gzip members in {archive_source}")
        member_number += 1
        payload_start = _parse_gzip_member_header(
            data, index, archive_source, member_number
        )
        remaining = limit - len(output)
        if remaining < 0:
            _base.fail(f"archive raw TAR stream exceeds size limit: {archive_source}")
        compressed = data[payload_start:]
        decompressor = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
        try:
            member_output = decompressor.decompress(compressed, remaining + 1)
        except zlib.error as exc:
            _base.fail(f"invalid gzip member in {archive_source}: {exc}")
        if len(member_output) > remaining or decompressor.unconsumed_tail:
            _base.fail(f"archive raw TAR stream exceeds size limit: {archive_source}")
        if not decompressor.eof:
            _base.fail(f"truncated gzip member in {archive_source}")
        consumed_deflate = len(compressed) - len(decompressor.unused_data)
        trailer_start = payload_start + consumed_deflate
        if trailer_start + 8 > len(data):
            _base.fail(f"truncated gzip trailer in {archive_source}")
        expected_crc, expected_size = struct.unpack(
            "<II", data[trailer_start : trailer_start + 8]
        )
        actual_crc = zlib.crc32(member_output) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            _base.fail(f"gzip member CRC mismatch in {archive_source}")
        if expected_size != (len(member_output) & 0xFFFFFFFF):
            _base.fail(f"gzip member size mismatch in {archive_source}")
        output.extend(member_output)
        index = trailer_start + 8
    if member_number == 0:
        _base.fail(f"gzip archive contains no members: {archive_source}")
    return bytes(output)


def _bounded_raw_tar_bytes(data: bytes, archive_source: str) -> bytes:
    """Return bounded uncompressed TAR bytes so raw PAX records remain visible."""

    limit = _base.MAX_ARCHIVE_UNCOMPRESSED_BYTES + RAW_TAR_OVERHEAD_BYTES
    try:
        if data.startswith(b"\x1f\x8b"):
            raw = _scan_and_decompress_gzip_members(data, archive_source, limit)
        elif data.startswith(b"BZh"):
            with bz2.BZ2File(io.BytesIO(data)) as stream:
                raw = stream.read(limit + 1)
        elif data.startswith(b"\xfd7zXZ\x00"):
            with lzma.LZMAFile(io.BytesIO(data)) as stream:
                raw = stream.read(limit + 1)
        else:
            raw = data
    except (EOFError, OSError, lzma.LZMAError) as exc:
        _base.fail(f"invalid compressed TAR archive {archive_source}: {exc}")
    if len(raw) > limit:
        _base.fail(f"archive raw TAR stream exceeds size limit: {archive_source}")
    return raw


def scan_tar_archive(data: bytes, archive_source: str) -> None:
    """Scan raw TAR records plus parsed PAX, ownership, and link metadata."""

    raw = _bounded_raw_tar_bytes(data, archive_source)
    scan_bytes_for_forbidden(raw, f"{archive_source}!raw-tar-stream")
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            _scan_tar_metadata_mapping(
                getattr(archive, "pax_headers", {}),
                f"{archive_source}!global-pax",
            )
            for member in archive.getmembers():
                member_source = f"{archive_source}!{member.name}"
                for field in ("name", "linkname", "uname", "gname"):
                    _scan_tar_metadata_value(
                        getattr(member, field, None),
                        f"{member_source}:{field}",
                    )
                _scan_tar_metadata_mapping(
                    getattr(member, "pax_headers", {}),
                    f"{member_source}:pax",
                )
    except (tarfile.TarError, EOFError) as exc:
        _base.fail(f"invalid TAR archive {archive_source}: {exc}")
    _original_scan_tar_archive(data, archive_source)


def scan_public_tree() -> None:
    for path in sorted(ROOT.rglob("*")):
        if should_ignore(path):
            continue
        relative = path.relative_to(ROOT)
        scan_public_path(relative)
        if path.is_symlink():
            _base.fail(f"symlinks are not allowed in the public tree: {relative}")
        if not path.is_file():
            continue
        if path.name.lower() in _base.FORBIDDEN_FILENAMES:
            _base.fail(f"forbidden sensitive filename in public tree: {relative}")
        if _base.is_supported_archive_name(path.name):
            _base.scan_archive(path, relative)
            continue
        if path.suffix.lower() == ".gz":
            _base.fail(f"unsupported compressed artifact in public tree: {relative}")
        data = path.read_bytes()
        suffix = path.suffix.lower()
        if suffix in _base.BINARY_SUFFIXES:
            _base.scan_binary(data, suffix, str(relative))
            continue
        scan_bytes_for_forbidden(data, str(relative))
        if b"\x00" in data:
            _base.fail(f"unapproved binary artifact in public tree: {relative}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            _base.fail(f"public artifact is not UTF-8 text or an approved binary type: {relative}")
        _base.scan_text(text, str(relative))


def validate_root_contract(manifest: dict[str, Any]) -> None:
    _original_validate_root_contract(manifest)
    if manifest["license_status"] != "approved":
        return
    documents = [ROOT / name for name in _base.APPROVED_LICENSE_FILES if (ROOT / name).exists()]
    if len(documents) != 1:
        _base.fail("approved license_status requires exactly one repository MIT LICENSE file")
    license_path = documents[0]
    if license_path.is_symlink() or not license_path.is_file():
        _base.fail(f"repository MIT license must be a regular file: {license_path.name}")
    try:
        actual = license_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    except UnicodeDecodeError:
        _base.fail(f"repository MIT license must be UTF-8 text: {license_path.name}")
    expected = EXPECTED_MIT_LICENSE.replace("\r\n", "\n").strip()
    if actual != expected:
        _base.fail("approved repository LICENSE does not match the governed MIT terms")


def package_path_for(entry: dict[str, Any]) -> Path:
    package_path = ROOT / entry["path"] / "skill.zip"
    try:
        package_path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        _base.fail(f"public package path escapes repository root: {entry['id']}")
    return package_path


def archive_artifacts(skill_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file() and _base.is_supported_archive_name(path.name)
    )


def validate_package_contents(entry: dict[str, Any], package_path: Path) -> None:
    """Require a flat deterministic package equal to the governed public skill tree."""

    skill_dir = ROOT / entry["path"]
    expected: dict[str, bytes] = {}
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path == package_path:
            continue
        relative = path.relative_to(skill_dir).as_posix()
        expected[relative] = path.read_bytes()

    try:
        with zipfile.ZipFile(package_path) as archive:
            actual: dict[str, bytes] = {}
            for info in archive.infolist():
                validate_archive_member_name(info.filename, str(package_path.relative_to(ROOT)))
                if info.is_dir():
                    continue
                if info.filename in actual:
                    _base.fail(
                        f"duplicate package member in {entry['path']}/skill.zip: {info.filename}"
                    )
                actual[info.filename] = archive.read(info)
    except (zipfile.BadZipFile, RuntimeError) as exc:
        _base.fail(f"invalid deterministic package for {entry['id']}: {exc}")

    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        _base.fail(
            f"package contents differ from public skill tree for {entry['id']}; "
            f"missing={missing}, extra={extra}"
        )
    for name, expected_bytes in expected.items():
        if actual[name] != expected_bytes:
            _base.fail(
                f"package member differs from public skill tree for {entry['id']}: {name}"
            )


def validate_package_evidence(entry: dict[str, Any]) -> None:
    package_path = package_path_for(entry)
    if package_path.is_symlink() or not package_path.is_file():
        _base.fail(
            f"recorded public package requires regular artifact "
            f"{entry['path']}/skill.zip: {entry['id']}"
        )
    actual_hash = hashlib.sha256(package_path.read_bytes()).hexdigest()
    if entry.get("package_sha256") != actual_hash:
        _base.fail(f"package_sha256 does not match {entry['path']}/skill.zip: {entry['id']}")
    validate_package_contents(entry, package_path)


def has_affirmative_verification(value: Any) -> bool:
    """Accept only a structured positive result with non-empty evidence."""

    if not isinstance(value, str):
        return False
    normalized = " ".join(value.strip().split())
    return normalized.startswith("PASS: ") and bool(normalized[6:].strip())


def validate_release_evidence(
    entry: dict[str, Any], repository_license_status: str, has_public_directory: bool
) -> None:
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

    skill_dir = ROOT / entry["path"]
    archives = archive_artifacts(skill_dir) if skill_dir.exists() else []
    if entry["artifact_status"] == "none" and archives:
        relative_archives = [str(path.relative_to(ROOT)) for path in archives]
        _base.fail(
            f"artifact_status none requires no archive artifacts for {entry['id']}: "
            f"{relative_archives}"
        )
    if "package_sha256" in entry:
        validate_package_evidence(entry)

    if release_state == "public-released":
        if not has_affirmative_verification(entry.get("verification")):
            _base.fail(
                f"public-released skill requires structured PASS verification evidence: "
                f"{entry['id']}"
            )
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
        matches = [(index, line) for index, line in enumerate(lines) if line.startswith(prefix)]
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
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter_text = _base.extract_frontmatter(skill_text)
    if frontmatter_text is None:
        _base.fail(f"SKILL.md requires opening YAML frontmatter for {entry['id']}")
    frontmatter = _base.load_yaml(
        frontmatter_text,
        f"skills/{entry['id']}/SKILL.md frontmatter",
    )
    declared_license = frontmatter.get("license") if isinstance(frontmatter, dict) else None
    if declared_license is not None and declared_license != entry["license"]:
        _base.fail(
            f"SKILL.md license differs from manifest for {entry['id']}: "
            f"expected {entry['license']!r}, found {declared_license!r}"
        )
    lines = (skill_dir / "README.md").read_text(encoding="utf-8").splitlines()
    validate_canonical_lineage(lines, entry["canonical"], entry["id"])


_base.should_ignore = should_ignore
_base.scan_bytes_for_forbidden = scan_bytes_for_forbidden
_base.validate_archive_member_name = validate_archive_member_name
_base.scan_archive_member = scan_archive_member
_base.scan_zip_archive = scan_zip_archive
_base.scan_tar_archive = scan_tar_archive
_base.scan_public_tree = scan_public_tree
_base.validate_root_contract = validate_root_contract
_base.validate_release_evidence = validate_release_evidence
_base.validate_skill = validate_skill


def main() -> int:
    _sync_paths()
    return _base.main()


def __getattr__(name: str) -> Any:
    return getattr(_base, name)


if __name__ == "__main__":
    raise SystemExit(main())
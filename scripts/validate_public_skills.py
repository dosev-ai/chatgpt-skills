#!/usr/bin/env python3
"""Validate downstream public ChatGPT skill projections and release lineage."""

from __future__ import annotations

import io
import json
import re
import stat
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from yaml.constructor import ConstructorError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills-manifest.yaml"
SCHEMA = ROOT / "schemas" / "public-skills-manifest.schema.json"
SKILLS_DIR = ROOT / "skills"

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:(?:0|[1-9]\d*)|(?:\d*[A-Za-z-][0-9A-Za-z-]*))"
    r"(?:\.(?:(?:0|[1-9]\d*)|(?:\d*[A-Za-z-][0-9A-Za-z-]*)))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
ALLOWED_SKILL_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
REQUIRED_ROOT_FILES = (
    "README.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "PUBLICATION_WORKFLOW.md",
    "SKILL_README_TEMPLATE.md",
    "LICENSE-STATUS.md",
    "skills-manifest.yaml",
    "schemas/public-skills-manifest.schema.json",
    "scripts/validate_public_skills.py",
    "scripts/validate_skill_readmes.py",
    "tests/test_validate_public_skills.py",
    "tests/test_validate_skill_readmes.py",
    ".github/workflows/public-skill-validation.yml",
    ".github/workflows/bot-comment-gate.yml",
    ".github/ISSUE_TEMPLATE/public-skill-defect.yml",
)
APPROVED_LICENSE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt")
FORBIDDEN_FILENAMES = {
    ".env",
    "credentials.json",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
}
IGNORED_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
BINARY_SUFFIXES = {
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".otf",
    ".pdf",
    ".png",
    ".ttf",
    ".wav",
    ".webp",
    ".woff",
    ".woff2",
}
MAX_ARCHIVE_COMPRESSED_BYTES = 25 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 1000
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key material", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("OpenAI-style secret key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private Cortex URI", re.compile(r"\bcortex" + r"://[^\s)`]+", re.IGNORECASE)),
    (
        "private Action Production identifier",
        re.compile(r"\b(?:action|fact)-\d{13}-\d{6}-[0-9a-f]{8}-[0-9a-f]{4}\b", re.IGNORECASE),
    ),
    (
        "private/internal endpoint",
        re.compile(r"https?://[^\s)`]*(?:\.internal|\.local)(?=[:/\s)`]|$)", re.IGNORECASE),
    ),
)


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_yaml(text: str, source: str) -> Any:
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        fail(f"invalid YAML in {source}: {exc}")


def validate_schema(instance: Any, schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        path = ".".join(str(part) for part in error.absolute_path) or "<root>"
        fail(f"manifest schema validation failed at {path}: {error.message}")


def extract_frontmatter(text: str) -> str | None:
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index])
    return None


def validate_root_contract(manifest: dict[str, Any]) -> None:
    for relative in REQUIRED_ROOT_FILES:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            fail(f"required regular public repository file is missing: {relative}")

    license_status = manifest["license_status"]
    license_documents = [ROOT / name for name in APPROVED_LICENSE_FILES if (ROOT / name).exists()]

    if license_status == "approved":
        if not license_documents:
            fail("approved license_status requires a repository LICENSE file")
        substantive = False
        for path in license_documents:
            if path.is_symlink() or not path.is_file():
                fail(f"repository license must be a regular file: {path.name}")
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                fail(f"repository license must be UTF-8 text: {path.name}")
            if len(text.strip()) >= 100:
                substantive = True
        if not substantive:
            fail("approved license_status requires substantive repository license terms")

    if license_status == "pending-owner-decision" and not (ROOT / "LICENSE-STATUS.md").is_file():
        fail("pending license_status requires LICENSE-STATUS.md")


def should_ignore(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True
    return any(part in IGNORED_DIR_NAMES for part in relative.parts)


def scan_text(text: str, source: str) -> None:
    for label, pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(text)
        if match:
            fail(f"{label} detected in {source}: {match.group(0)[:80]!r}")


def is_supported_archive_name(name: str) -> bool:
    lower = name.lower()
    return lower.endswith((".zip", ".tar", ".tar.gz", ".tgz"))


def validate_archive_member_name(name: str, archive_source: str) -> PurePosixPath:
    if "\\" in name or re.match(r"^[A-Za-z]:", name):
        fail(f"unsafe archive member path in {archive_source}: {name!r}")
    member_path = PurePosixPath(name)
    if member_path.is_absolute() or ".." in member_path.parts:
        fail(f"unsafe archive member path in {archive_source}: {name!r}")
    if not member_path.name and name not in {"", "."}:
        return member_path
    if member_path.name.lower() in FORBIDDEN_FILENAMES:
        fail(f"forbidden sensitive filename in archive {archive_source}: {name}")
    if is_supported_archive_name(member_path.name):
        fail(f"nested archives are not allowed in public packages: {archive_source}!{name}")
    return member_path


def scan_archive_member(data: bytes, name: str, archive_source: str) -> None:
    member_path = validate_archive_member_name(name, archive_source)
    if member_path.suffix.lower() in BINARY_SUFFIXES:
        return
    if b"\x00" in data[:8192]:
        fail(f"unapproved binary artifact in archive: {archive_source}!{name}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"archive member is not UTF-8 text or an approved binary type: {archive_source}!{name}")
    scan_text(text, f"{archive_source}!{name}")


def scan_zip_archive(data: bytes, archive_source: str) -> None:
    total_uncompressed = 0
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_ENTRIES:
                fail(f"archive contains too many entries: {archive_source}")
            for info in infos:
                validate_archive_member_name(info.filename, archive_source)
                if info.is_dir():
                    continue
                if info.flag_bits & 0x1:
                    fail(f"encrypted archive members are not allowed: {archive_source}!{info.filename}")
                mode = (info.external_attr >> 16) & 0o170000
                if mode == stat.S_IFLNK:
                    fail(f"archive symlinks are not allowed: {archive_source}!{info.filename}")
                total_uncompressed += info.file_size
                if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    fail(f"archive exceeds uncompressed size limit: {archive_source}")
                with archive.open(info) as member:
                    member_data = member.read(info.file_size + 1)
                if len(member_data) != info.file_size:
                    fail(f"archive member size mismatch: {archive_source}!{info.filename}")
                scan_archive_member(member_data, info.filename, archive_source)
    except (zipfile.BadZipFile, RuntimeError) as exc:
        fail(f"invalid ZIP archive {archive_source}: {exc}")


def scan_tar_archive(data: bytes, archive_source: str) -> None:
    total_uncompressed = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            members = archive.getmembers()
            if len(members) > MAX_ARCHIVE_ENTRIES:
                fail(f"archive contains too many entries: {archive_source}")
            for member in members:
                validate_archive_member_name(member.name, archive_source)
                if member.isdir():
                    continue
                if not member.isreg():
                    fail(f"archive links and special files are not allowed: {archive_source}!{member.name}")
                total_uncompressed += member.size
                if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                    fail(f"archive exceeds uncompressed size limit: {archive_source}")
                extracted = archive.extractfile(member)
                if extracted is None:
                    fail(f"unable to read archive member: {archive_source}!{member.name}")
                member_data = extracted.read(member.size + 1)
                if len(member_data) != member.size:
                    fail(f"archive member size mismatch: {archive_source}!{member.name}")
                scan_archive_member(member_data, member.name, archive_source)
    except (tarfile.TarError, EOFError) as exc:
        fail(f"invalid TAR archive {archive_source}: {exc}")


def scan_archive(path: Path, relative: Path) -> None:
    if path.stat().st_size > MAX_ARCHIVE_COMPRESSED_BYTES:
        fail(f"archive exceeds compressed size limit: {relative}")
    data = path.read_bytes()
    lower = path.name.lower()
    if lower.endswith(".zip"):
        scan_zip_archive(data, str(relative))
    elif lower.endswith((".tar", ".tar.gz", ".tgz")):
        scan_tar_archive(data, str(relative))
    else:
        fail(f"unsupported archive format in public tree: {relative}")


def scan_public_tree() -> None:
    """Scan every tracked-style public file, including supported archive contents."""

    for path in sorted(ROOT.rglob("*")):
        if should_ignore(path):
            continue
        if path.is_symlink():
            fail(f"symlinks are not allowed in the public tree: {path.relative_to(ROOT)}")
        if not path.is_file():
            continue

        relative = path.relative_to(ROOT)
        if path.name.lower() in FORBIDDEN_FILENAMES:
            fail(f"forbidden sensitive filename in public tree: {relative}")
        if is_supported_archive_name(path.name):
            scan_archive(path, relative)
            continue
        if path.suffix.lower() == ".gz":
            fail(f"unsupported compressed artifact in public tree: {relative}")
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue

        data = path.read_bytes()
        if b"\x00" in data[:8192]:
            fail(f"unapproved binary artifact in public tree: {relative}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            fail(f"public artifact is not UTF-8 text or an approved binary type: {relative}")
        scan_text(text, str(relative))


def validate_release_evidence(entry: dict[str, Any], repository_license_status: str) -> None:
    skill_id = entry["id"]
    release_state = entry["release_state"]
    artifact_status = entry["artifact_status"]
    license_value = entry["license"].strip()

    if not license_value:
        fail(f"skill license value must not be blank: {skill_id}")

    pre_pr_states = {"not-candidate", "candidate-needs-sanitization", "ready-for-public-pr"}
    merged_states = {"public-merged-verification-pending", "public-released"}

    if release_state in pre_pr_states and "public_pr" in entry:
        fail(f"{release_state} must not claim public_pr for {skill_id}")
    if release_state in {"public-pr-open", *merged_states} and "public_pr" not in entry:
        fail(f"{release_state} requires public_pr for {skill_id}")
    if release_state not in merged_states and "public_merge_commit" in entry:
        fail(f"{release_state} must not claim public_merge_commit for {skill_id}")
    if release_state in merged_states and "public_merge_commit" not in entry:
        fail(f"{release_state} requires public_merge_commit for {skill_id}")

    if artifact_status == "none" and "package_sha256" in entry:
        fail(f"artifact_status none must not include package_sha256: {skill_id}")
    if "package_sha256" in entry and release_state not in merged_states:
        fail(f"package_sha256 must reference merged public content: {skill_id}")

    if release_state in merged_states:
        if repository_license_status != "approved":
            fail(f"{release_state} requires approved repository license: {skill_id}")
        if license_value.lower() in {"pending", "unknown", "unlicensed", "not-applicable"}:
            fail(f"{release_state} requires an approved per-skill license: {skill_id}")

    if release_state == "public-released":
        if not entry.get("verification", "").strip():
            fail(f"public-released skill requires verification evidence: {skill_id}")
        if "residuals" not in entry or not isinstance(entry["residuals"], list):
            fail(f"public-released skill requires explicit residuals array: {skill_id}")
        if artifact_status == "package" and "package_sha256" not in entry:
            fail(f"packaged public-released skill requires package_sha256: {skill_id}")


def validate_skill(entry: dict[str, Any], repository_license_status: str) -> None:
    skill_id = entry["id"]
    expected_path = f"skills/{skill_id}"
    skill_dir = ROOT / entry["path"]
    canonical = entry["canonical"]

    validate_release_evidence(entry, repository_license_status)

    if entry["path"] != expected_path:
        fail(f"manifest path must be {expected_path}")
    if canonical["path"] != expected_path:
        fail(f"canonical path must be {expected_path}")
    if canonical["version"] != entry["version"]:
        fail(f"public projection version differs from canonical version for {skill_id}")

    if entry["release_state"] == "not-candidate" and not skill_dir.exists():
        if entry["artifact_status"] != "none":
            fail(f"not-candidate entry must use artifact_status none: {skill_id}")
        return

    if not skill_dir.is_dir() or skill_dir.is_symlink():
        fail(f"manifest entry missing regular skill directory: {entry['path']}")

    required = [
        skill_dir / "SKILL.md",
        skill_dir / "CHANGELOG.md",
        skill_dir / "README.md",
        skill_dir / "agents" / "openai.yaml",
    ]
    for required_file in required:
        if not required_file.is_file() or required_file.is_symlink():
            fail(f"missing required regular public file: {required_file.relative_to(ROOT)}")

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter_text = extract_frontmatter(skill_text)
    if frontmatter_text is None:
        fail(f"SKILL.md requires opening YAML frontmatter for {skill_id}")
    frontmatter = load_yaml(frontmatter_text, f"skills/{skill_id}/SKILL.md frontmatter")
    if not isinstance(frontmatter, dict):
        fail(f"SKILL.md frontmatter must be a mapping for {skill_id}")

    unexpected = set(frontmatter) - ALLOWED_SKILL_FRONTMATTER
    if unexpected:
        fail(
            f"SKILL.md frontmatter contains non-portable keys for {skill_id}: "
            f"{', '.join(sorted(unexpected))}"
        )
    for key in ("name", "description", "metadata"):
        if key not in frontmatter:
            fail(f"SKILL.md frontmatter requires {key} for {skill_id}")
    if frontmatter["name"] != skill_id:
        fail(f"SKILL.md name must match directory for {skill_id}")
    if not isinstance(frontmatter["description"], str) or not frontmatter["description"].strip():
        fail(f"SKILL.md description must be non-empty for {skill_id}")

    metadata = frontmatter["metadata"]
    if not isinstance(metadata, dict):
        fail(f"SKILL.md metadata must be a mapping for {skill_id}")
    for key in ("version", "canonical_repository", "canonical_path"):
        if key not in metadata:
            fail(f"SKILL.md metadata requires {key} for {skill_id}")

    version = metadata["version"]
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        fail(f"SKILL.md metadata.version is invalid for {skill_id}")
    if entry["version"] != version:
        fail(f"manifest and SKILL.md version differ for {skill_id}")

    if metadata["canonical_repository"] != canonical["repository"]:
        fail(f"SKILL.md canonical_repository differs from manifest for {skill_id}")
    if metadata["canonical_path"] != canonical["path"]:
        fail(f"SKILL.md canonical_path differs from manifest for {skill_id}")

    changelog = (skill_dir / "CHANGELOG.md").read_text(encoding="utf-8")
    heading_pattern = rf"(?m)^##\s+(?:\[{re.escape(version)}\](?:\s|$)|{re.escape(version)}(?:\s|$))"
    if not re.search(heading_pattern, changelog):
        fail(f"CHANGELOG.md must contain version {version} for {skill_id}")

    readme_lines = set((skill_dir / "README.md").read_text(encoding="utf-8").splitlines())
    expected_lineage = (
        f"- Canonical repository: `{canonical['repository']}`",
        f"- Canonical path: `{canonical['path']}`",
        f"- Canonical version: `{canonical['version']}`",
        f"- Canonical source PR: `#{canonical['source_pr']}`",
        f"- Canonical final PR HEAD: `{canonical['final_pr_head']}`",
        f"- Canonical merge commit: `{canonical['merge_commit']}`",
    )
    for expected in expected_lineage:
        if expected not in readme_lines:
            fail(f"README.md is missing exact canonical lineage field {expected!r} for {skill_id}")


def main() -> int:
    if not MANIFEST.is_file():
        fail("skills-manifest.yaml is missing")
    if not SCHEMA.is_file():
        fail("public manifest JSON schema is missing")

    manifest = load_yaml(MANIFEST.read_text(encoding="utf-8"), "skills-manifest.yaml")
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid public manifest JSON schema: {exc}")

    validate_schema(manifest, schema)
    validate_root_contract(manifest)
    scan_public_tree()

    entries = manifest["skills"]
    entries_by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        skill_id = entry["id"]
        if skill_id in entries_by_id:
            fail(f"manifest contains duplicate skill ID: {skill_id}")
        entries_by_id[skill_id] = entry
        validate_skill(entry, manifest["license_status"])

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()) if SKILLS_DIR.exists() else []
    found_ids: set[str] = set()
    for skill_dir in skill_dirs:
        skill_id = skill_dir.name
        if not ID_PATTERN.fullmatch(skill_id):
            fail(f"invalid skill directory name: {skill_id}")
        if skill_id in found_ids:
            fail(f"duplicate skill directory: {skill_id}")
        found_ids.add(skill_id)
        if skill_id not in entries_by_id:
            fail(f"public skill directory is not registered in manifest: {skill_id}")

    required_directory_ids = {
        skill_id
        for skill_id, entry in entries_by_id.items()
        if entry["release_state"] != "not-candidate"
    }
    missing_dirs = sorted(required_directory_ids - found_ids)
    if missing_dirs:
        fail(f"manifest entries missing directories: {', '.join(missing_dirs)}")

    print(f"Public Skill Validation PASS: {len(skill_dirs)} registered skill directorie(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

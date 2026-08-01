#!/usr/bin/env python3
"""Validate downstream public ChatGPT skill projections and release lineage."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
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
    "LICENSE-STATUS.md",
    "skills-manifest.yaml",
    "schemas/public-skills-manifest.schema.json",
    "scripts/validate_public_skills.py",
    "tests/test_validate_public_skills.py",
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
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp3",
    ".mp4",
    ".otf",
    ".pdf",
    ".png",
    ".tar",
    ".ttf",
    ".wav",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}
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


def scan_public_tree() -> None:
    """Scan every tracked-style public file, not only registered skill directories."""

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
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue

        data = path.read_bytes()
        if b"\x00" in data[:8192]:
            fail(f"unapproved binary artifact in public tree: {relative}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            fail(f"public artifact is not UTF-8 text or an approved binary type: {relative}")

        for label, pattern in FORBIDDEN_PATTERNS:
            match = pattern.search(text)
            if match:
                fail(f"{label} detected in {relative}: {match.group(0)[:80]!r}")


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
        if artifact_status == "package" and "package_sha256" not in entry:
            fail(f"packaged public-released skill requires package_sha256: {skill_id}")


def validate_skill(entry: dict[str, Any], repository_license_status: str) -> None:
    skill_id = entry["id"]
    skill_dir = ROOT / entry["path"]

    validate_release_evidence(entry, repository_license_status)

    if entry["path"] != f"skills/{skill_id}":
        fail(f"manifest path must be skills/{skill_id}")

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

    canonical = entry["canonical"]
    if metadata["canonical_repository"] != canonical["repository"]:
        fail(f"SKILL.md canonical_repository differs from manifest for {skill_id}")
    if metadata["canonical_path"] != canonical["path"]:
        fail(f"SKILL.md canonical_path differs from manifest for {skill_id}")
    if canonical["path"] != f"skills/{skill_id}":
        fail(f"canonical path must be skills/{skill_id}")
    if canonical["version"] != version:
        fail(f"public projection version differs from canonical version for {skill_id}")

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

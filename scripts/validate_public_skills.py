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
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml"}
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key material", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("OpenAI-style secret key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private Cortex URI", re.compile(r"\bcortex://[^\s)`]+", re.IGNORECASE)),
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


def scan_public_safety(skill_dir: Path) -> None:
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"public text file is not valid UTF-8: {path.relative_to(ROOT)}")
        for label, pattern in FORBIDDEN_PATTERNS:
            match = pattern.search(text)
            if match:
                fail(
                    f"{label} detected in {path.relative_to(ROOT)}: "
                    f"{match.group(0)[:80]!r}"
                )


def validate_skill(entry: dict[str, Any], repository_license_status: str) -> None:
    skill_id = entry["id"]
    skill_dir = ROOT / entry["path"]
    if entry["path"] != f"skills/{skill_id}":
        fail(f"manifest path must be skills/{skill_id}")
    if not skill_dir.is_dir():
        fail(f"manifest entry missing skill directory: {entry['path']}")

    required = [
        skill_dir / "SKILL.md",
        skill_dir / "CHANGELOG.md",
        skill_dir / "README.md",
        skill_dir / "agents" / "openai.yaml",
    ]
    for required_file in required:
        if not required_file.is_file():
            fail(f"missing required public file: {required_file.relative_to(ROOT)}")

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

    readme = (skill_dir / "README.md").read_text(encoding="utf-8")
    for expected in (
        canonical["repository"],
        canonical["path"],
        canonical["merge_commit"],
    ):
        if expected not in readme:
            fail(f"README.md is missing canonical lineage {expected!r} for {skill_id}")

    release_state = entry["release_state"]
    if release_state in {"public-pr-open", "public-released"} and "public_pr" not in entry:
        fail(f"{release_state} requires public_pr for {skill_id}")
    if release_state == "public-released":
        if repository_license_status != "approved":
            fail(f"public-released skill requires approved repository license: {skill_id}")
        for key in ("public_merge_commit", "package_sha256", "verification"):
            if key not in entry:
                fail(f"public-released skill requires {key}: {skill_id}")

    scan_public_safety(skill_dir)


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

    missing_dirs = sorted(set(entries_by_id) - found_ids)
    if missing_dirs:
        fail(f"manifest entries missing directories: {', '.join(missing_dirs)}")

    print(f"Public Skill Validation PASS: {len(skill_dirs)} registered skill(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

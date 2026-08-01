from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_public_skills.py"
SCHEMA_SOURCE = REPOSITORY_ROOT / "schemas" / "public-skills-manifest.schema.json"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_public_skills", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillValidatorTests(unittest.TestCase):
    validator = load_validator()

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._write_root_contract()
        self._patch_validator_root()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _patch_validator_root(self) -> None:
        self.validator.ROOT = self.root
        self.validator.MANIFEST = self.root / "skills-manifest.yaml"
        self.validator.SCHEMA = self.root / "schemas" / "public-skills-manifest.schema.json"
        self.validator.SKILLS_DIR = self.root / "skills"

    def _write_root_contract(self) -> None:
        for relative in self.validator.REQUIRED_ROOT_FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative == "schemas/public-skills-manifest.schema.json":
                path.write_text(SCHEMA_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                path.write_text(f"test fixture for {relative}\n", encoding="utf-8")

    def _base_manifest(self, *, license_status: str = "pending-owner-decision") -> dict[str, Any]:
        return {
            "schema_version": 1,
            "repository": {
                "name": "dosev-ai/chatgpt-skills",
                "default_branch": "main",
                "contribution_model": "pull-request-only",
                "canonical_repository": "deldos/skills",
                "required_checks": ["Public Skill Validation", "Bot Comment Closure Rate"],
            },
            "naming": {
                "skill_id_pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
                "directory_pattern": "skills/<skill-id>",
            },
            "versioning": {"scheme": "semver"},
            "license_status": license_status,
            "allowed_release_states": [
                "candidate-needs-sanitization",
                "ready-for-public-pr",
                "public-pr-open",
                "public-released",
            ],
            "skills": [],
        }

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        (self.root / "skills-manifest.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )

    def _skill_entry(self, *, release_state: str = "public-pr-open") -> dict[str, Any]:
        entry: dict[str, Any] = {
            "id": "example-skill",
            "path": "skills/example-skill",
            "display_name": "Example Skill",
            "version": "1.2.3",
            "release_state": release_state,
            "description": "Public validation fixture.",
            "canonical": {
                "repository": "deldos/skills",
                "path": "skills/example-skill",
                "version": "1.2.3",
                "source_pr": 42,
                "final_pr_head": "a" * 40,
                "merge_commit": "b" * 40,
            },
            "license": "pending" if release_state != "public-released" else "MIT",
            "public_pr": 7,
        }
        if release_state == "public-released":
            entry.update(
                {
                    "public_merge_commit": "c" * 40,
                    "package_sha256": "d" * 64,
                    "verification": "Clean-room invocation passed.",
                }
            )
        return entry

    def _write_skill(self, entry: dict[str, Any], *, body: str = "Public skill body.\n") -> None:
        skill_dir = self.root / entry["path"]
        (skill_dir / "agents").mkdir(parents=True, exist_ok=True)
        canonical = entry["canonical"]
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: example-skill\n"
            "description: Public validation fixture.\n"
            "metadata:\n"
            f"  version: {entry['version']}\n"
            f"  canonical_repository: {canonical['repository']}\n"
            f"  canonical_path: {canonical['path']}\n"
            "---\n\n"
            f"# Example Skill\n\n{body}",
            encoding="utf-8",
        )
        (skill_dir / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## {entry['version']} - 2026-08-02\n\n- Fixture.\n",
            encoding="utf-8",
        )
        (skill_dir / "README.md").write_text(
            "# Example Skill\n\n"
            f"Canonical repository: {canonical['repository']}\n\n"
            f"Canonical path: {canonical['path']}\n\n"
            f"Canonical version: {canonical['version']}\n\n"
            f"Canonical source PR: PR #{canonical['source_pr']}\n\n"
            f"Final PR HEAD: {canonical['final_pr_head']}\n\n"
            f"Merge commit: {canonical['merge_commit']}\n",
            encoding="utf-8",
        )
        (skill_dir / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: Example Skill\n  short_description: Fixture.\n",
            encoding="utf-8",
        )

    def _run(self) -> tuple[int, str]:
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                result = self.validator.main()
        except SystemExit as exc:
            return int(exc.code), output.getvalue()
        return result, output.getvalue()

    def test_empty_foundation_passes(self) -> None:
        self._write_manifest(self._base_manifest())
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("0 registered skill(s)", output)

    def test_valid_public_pr_open_skill_passes(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 registered skill(s)", output)

    def test_public_released_requires_approved_repository_license(self) -> None:
        manifest = self._base_manifest(license_status="pending-owner-decision")
        entry = self._skill_entry(release_state="public-released")
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires approved repository license", output)

    def test_private_action_identifier_is_rejected(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry, body="Leaked action-1785621210329-210329-c1a4b863-2ad5.\n")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("private Action Production identifier", output)

    def test_missing_readme_lineage_is_rejected(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry)
        readme = self.root / entry["path"] / "README.md"
        readme.write_text("# Missing lineage\n", encoding="utf-8")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("missing canonical lineage", output)

    def test_approved_license_status_requires_license_file(self) -> None:
        manifest = self._base_manifest(license_status="approved")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires a repository LICENSE file", output)


if __name__ == "__main__":
    unittest.main()

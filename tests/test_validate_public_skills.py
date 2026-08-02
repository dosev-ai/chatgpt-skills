from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import tempfile
import unittest
import zipfile
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

    def _approve_repository_license(self) -> None:
        (self.root / "LICENSE").write_text(
            self.validator.EXPECTED_MIT_LICENSE,
            encoding="utf-8",
        )

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
                "not-candidate",
                "candidate-needs-sanitization",
                "ready-for-public-pr",
                "public-pr-open",
                "public-merged-verification-pending",
                "public-released",
            ],
            "skills": [],
        }

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        (self.root / "skills-manifest.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )

    def _skill_entry(
        self,
        *,
        release_state: str = "public-pr-open",
        artifact_status: str = "none",
        include_package_hash: bool = False,
    ) -> dict[str, Any]:
        merged_states = {"public-merged-verification-pending", "public-released"}
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
            "license": "MIT" if release_state in {"public-pr-open", *merged_states} else "pending",
            "artifact_status": artifact_status,
        }
        if release_state in {"public-pr-open", *merged_states}:
            entry["public_pr"] = 7
        if release_state in merged_states:
            entry["public_merge_commit"] = "c" * 40
        if release_state == "public-released":
            entry["verification"] = "PASS: Clean-room invocation completed successfully."
            entry["residuals"] = []
        if include_package_hash:
            entry["package_sha256"] = "d" * 64
        return entry

    def _write_skill(self, entry: dict[str, Any], *, body: str = "Public skill body.\n") -> None:
        skill_dir = self.root / entry["path"]
        (skill_dir / "agents").mkdir(parents=True, exist_ok=True)
        canonical = entry["canonical"]
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: example-skill\n"
            "description: Public validation fixture.\n"
            f"license: {entry['license']}\n"
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
            "## Canonical lineage\n\n"
            f"- Canonical repository: `{canonical['repository']}`\n"
            f"- Canonical path: `{canonical['path']}`\n"
            f"- Canonical version: `{canonical['version']}`\n"
            f"- Canonical source PR: `#{canonical['source_pr']}`\n"
            f"- Canonical final PR HEAD: `{canonical['final_pr_head']}`\n"
            f"- Canonical merge commit: `{canonical['merge_commit']}`\n",
            encoding="utf-8",
        )
        (skill_dir / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: Example Skill\n  short_description: Fixture.\n",
            encoding="utf-8",
        )

    def _write_zip(self, filename: str, members: dict[str, str | bytes]) -> None:
        with zipfile.ZipFile(self.root / filename, "w") as archive:
            for name, content in members.items():
                archive.writestr(name, content)

    def _write_skill_package(self, entry: dict[str, Any]) -> Path:
        skill_dir = self.root / entry["path"]
        package_path = skill_dir / "skill.zip"
        with zipfile.ZipFile(package_path, "w") as archive:
            for path in sorted(skill_dir.rglob("*")):
                if path.is_file() and path != package_path:
                    archive.writestr(path.relative_to(skill_dir).as_posix(), path.read_bytes())
        return package_path

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
        self.assertIn("0 registered skill directorie(s)", output)

    def test_valid_public_pr_open_skill_passes_with_approved_license(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 registered skill directorie(s)", output)

    def test_public_pr_open_requires_approved_repository_license(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires approved repository license", output)

    def test_not_candidate_without_public_directory_passes(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry(release_state="not-candidate")
        entry["license"] = "not-applicable"
        manifest["skills"].append(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("0 registered skill directorie(s)", output)

    def test_not_candidate_rejects_mismatched_canonical_path(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry(release_state="not-candidate")
        entry["license"] = "not-applicable"
        entry["canonical"]["path"] = "skills/different-skill"
        manifest["skills"].append(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("canonical path must be skills/example-skill", output)

    def test_not_candidate_rejects_mismatched_canonical_version(self) -> None:
        manifest = self._base_manifest()
        entry = self._skill_entry(release_state="not-candidate")
        entry["license"] = "not-applicable"
        entry["canonical"]["version"] = "1.2.2"
        manifest["skills"].append(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("differs from canonical version", output)

    def test_public_released_requires_approved_repository_license(self) -> None:
        manifest = self._base_manifest(license_status="pending-owner-decision")
        entry = self._skill_entry(release_state="public-released")
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires approved repository license", output)

    def test_public_released_requires_explicit_residuals(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry(release_state="public-released")
        del entry["residuals"]
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("residuals", output)

    def test_public_released_without_package_passes(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry(release_state="public-released", artifact_status="none")
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 registered skill directorie(s)", output)

    def test_packaged_public_release_requires_hash(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry(release_state="public-released", artifact_status="package")
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires package_sha256", output)

    def test_packaged_public_release_with_hash_passes(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry(
            release_state="public-released",
            artifact_status="package",
        )
        manifest["skills"].append(entry)
        self._write_skill(entry)
        package_path = self._write_skill_package(entry)
        entry["package_sha256"] = hashlib.sha256(package_path.read_bytes()).hexdigest()
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 registered skill directorie(s)", output)

    def test_packaged_public_release_rejects_incomplete_tree(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry(release_state="public-released", artifact_status="package")
        manifest["skills"].append(entry)
        self._write_skill(entry)
        package_path = self.root / entry["path"] / "skill.zip"
        with zipfile.ZipFile(package_path, "w") as archive:
            archive.writestr("SKILL.md", (self.root / entry["path"] / "SKILL.md").read_bytes())
        entry["package_sha256"] = hashlib.sha256(package_path.read_bytes()).hexdigest()
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("package contents differ from public skill tree", output)

    def test_private_action_identifier_in_root_csv_is_rejected(self) -> None:
        manifest = self._base_manifest()
        private_id = "action-" + "1785621210329" + "-210329-" + "c1a4b863" + "-2ad5"
        (self.root / "public-data.csv").write_text(f"value\n{private_id}\n", encoding="utf-8")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("private Action Production identifier", output)

    def test_private_identifier_in_skill_csv_is_rejected(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry)
        private_id = "fact-" + "1785621202220" + "-202220-" + "416a22f6" + "-f06a"
        reference = self.root / entry["path"] / "references" / "private.csv"
        reference.parent.mkdir(parents=True, exist_ok=True)
        reference.write_text(f"id\n{private_id}\n", encoding="utf-8")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("private Action Production identifier", output)

    def test_private_identifier_inside_zip_is_rejected(self) -> None:
        manifest = self._base_manifest()
        private_id = "action-" + "1785621210329" + "-210329-" + "c1a4b863" + "-2ad5"
        self._write_zip("public-package.zip", {"references/data.csv": f"id\n{private_id}\n"})
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("private Action Production identifier", output)
        self.assertIn("public-package.zip!references/data.csv", output)

    def test_secret_inside_valid_png_is_rejected(self) -> None:
        manifest = self._base_manifest()
        token = "ghp_" + "A" * 20
        (self.root / "cover.png").write_bytes(b"\x89PNG\r\n\x1a\n" + token.encode("ascii"))
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("GitHub token", output)

    def test_plain_text_named_png_is_rejected(self) -> None:
        manifest = self._base_manifest()
        (self.root / "cover.png").write_text("not actually a PNG", encoding="utf-8")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("does not match its declared format", output)

    def test_secret_inside_zip_png_is_rejected(self) -> None:
        manifest = self._base_manifest()
        token = "sk-" + "B" * 20
        payload = b"\x89PNG\r\n\x1a\n" + token.encode("ascii")
        self._write_zip("public-package.zip", {"assets/cover.png": payload})
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("OpenAI-style secret key", output)

    def test_archive_path_traversal_is_rejected(self) -> None:
        manifest = self._base_manifest()
        self._write_zip("public-package.zip", {"../outside.txt": "public text"})
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("unsafe archive member path", output)

    def test_unlabeled_readme_lineage_is_rejected(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry()
        manifest["skills"].append(entry)
        self._write_skill(entry)
        canonical = entry["canonical"]
        readme = self.root / entry["path"] / "README.md"
        readme.write_text(
            "# Misleading lineage\n\n"
            f"Historical values: {canonical['repository']} {canonical['path']} "
            f"{canonical['version']} #{canonical['source_pr']} "
            f"{canonical['final_pr_head']} {canonical['merge_commit']}\n",
            encoding="utf-8",
        )
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("missing exact canonical lineage field", output)

    def test_approved_license_status_requires_license_file(self) -> None:
        manifest = self._base_manifest(license_status="approved")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires a repository LICENSE file", output)

    def test_approved_license_status_rejects_empty_license(self) -> None:
        manifest = self._base_manifest(license_status="approved")
        (self.root / "LICENSE").write_text("   \n", encoding="utf-8")
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires substantive repository license terms", output)

    def test_public_released_rejects_blank_skill_license(self) -> None:
        self._approve_repository_license()
        manifest = self._base_manifest(license_status="approved")
        entry = self._skill_entry(release_state="public-released")
        entry["license"] = "   "
        manifest["skills"].append(entry)
        self._write_skill(entry)
        self._write_manifest(manifest)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("must not be blank", output)


if __name__ == "__main__":
    unittest.main()

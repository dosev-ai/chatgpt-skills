from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_public_skills.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "validate_public_skills_release_hardening", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillReleaseHardeningTests(unittest.TestCase):
    validator = load_validator()

    def _capture_failure(self, callback) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                callback()
        return output.getvalue()

    def _patch_root(self, root: Path) -> tuple[Path, Path, Path, Path]:
        previous = (
            self.validator.ROOT,
            self.validator.MANIFEST,
            self.validator.SCHEMA,
            self.validator.SKILLS_DIR,
        )
        self.validator.ROOT = root
        self.validator.MANIFEST = root / "skills-manifest.yaml"
        self.validator.SCHEMA = root / "schemas" / "public-skills-manifest.schema.json"
        self.validator.SKILLS_DIR = root / "skills"
        self.validator._sync_paths()
        return previous

    def _restore_root(self, previous: tuple[Path, Path, Path, Path]) -> None:
        (
            self.validator.ROOT,
            self.validator.MANIFEST,
            self.validator.SCHEMA,
            self.validator.SKILLS_DIR,
        ) = previous
        self.validator._sync_paths()

    def test_public_released_rejects_pending_verification(self) -> None:
        entry = {
            "id": "example-skill",
            "path": "skills/example-skill",
            "release_state": "public-released",
            "artifact_status": "none",
            "license": "MIT",
            "public_pr": 7,
            "public_merge_commit": "c" * 40,
            "verification": "pending",
            "residuals": [],
        }
        output = self._capture_failure(
            lambda: self.validator.validate_release_evidence(entry, "approved", True)
        )
        self.assertIn("structured PASS verification evidence", output)

    def test_public_released_rejects_explicit_failed_verification(self) -> None:
        entry = {
            "id": "example-skill",
            "path": "skills/example-skill",
            "release_state": "public-released",
            "artifact_status": "none",
            "license": "MIT",
            "public_pr": 7,
            "public_merge_commit": "c" * 40,
            "verification": "Clean-room invocation failed.",
            "residuals": [],
        }
        output = self._capture_failure(
            lambda: self.validator.validate_release_evidence(entry, "approved", True)
        )
        self.assertIn("structured PASS verification evidence", output)

    def test_package_hash_must_match_actual_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "skills" / "example-skill" / "skill.zip"
            package.parent.mkdir(parents=True)
            package.write_bytes(b"package-bytes")
            previous = self._patch_root(root)
            try:
                entry = {
                    "id": "example-skill",
                    "path": "skills/example-skill",
                    "package_sha256": "0" * 64,
                }
                output = self._capture_failure(
                    lambda: self.validator.validate_package_evidence(entry)
                )
            finally:
                self._restore_root(previous)
        self.assertIn("package_sha256 does not match", output)

    def test_pending_merged_package_hash_is_verified_when_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "skills" / "example-skill" / "skill.zip"
            package.parent.mkdir(parents=True)
            package.write_bytes(b"pending-package-bytes")
            previous = self._patch_root(root)
            try:
                entry = {
                    "id": "example-skill",
                    "path": "skills/example-skill",
                    "release_state": "public-merged-verification-pending",
                    "artifact_status": "package",
                    "license": "MIT",
                    "public_pr": 7,
                    "public_merge_commit": "c" * 40,
                    "package_sha256": "0" * 64,
                }
                output = self._capture_failure(
                    lambda: self.validator.validate_release_evidence(
                        entry, "approved", True
                    )
                )
            finally:
                self._restore_root(previous)
        self.assertIn("package_sha256 does not match", output)

    def test_wrong_repository_license_text_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative in self.validator.REQUIRED_ROOT_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"fixture for {relative}\n", encoding="utf-8")
            (root / "LICENSE").write_text(
                "Proprietary terms. All rights reserved. " * 5,
                encoding="utf-8",
            )
            previous = self._patch_root(root)
            try:
                output = self._capture_failure(
                    lambda: self.validator.validate_root_contract(
                        {"license_status": "approved"}
                    )
                )
            finally:
                self._restore_root(previous)
        self.assertIn("does not match the governed MIT terms", output)

    def test_skill_frontmatter_license_must_match_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "skills" / "example-skill"
            (skill_dir / "agents").mkdir(parents=True)
            canonical = {
                "repository": "deldos/skills",
                "path": "skills/example-skill",
                "version": "1.2.3",
                "source_pr": 42,
                "final_pr_head": "a" * 40,
                "merge_commit": "b" * 40,
            }
            entry = {
                "id": "example-skill",
                "path": "skills/example-skill",
                "version": "1.2.3",
                "release_state": "public-pr-open",
                "artifact_status": "none",
                "license": "MIT",
                "public_pr": 7,
                "canonical": canonical,
            }
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: example-skill\n"
                "description: Public fixture.\n"
                "license: GPL-3.0\n"
                "metadata:\n"
                "  version: 1.2.3\n"
                "  canonical_repository: deldos/skills\n"
                "  canonical_path: skills/example-skill\n"
                "---\n\n# Example Skill\n",
                encoding="utf-8",
            )
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.2.3 - 2026-08-02\n",
                encoding="utf-8",
            )
            (skill_dir / "README.md").write_text(
                "# Example Skill\n\n"
                "## Canonical lineage\n\n"
                "- Canonical repository: `deldos/skills`\n"
                "- Canonical path: `skills/example-skill`\n"
                "- Canonical version: `1.2.3`\n"
                "- Canonical source PR: `#42`\n"
                f"- Canonical final PR HEAD: `{'a' * 40}`\n"
                f"- Canonical merge commit: `{'b' * 40}`\n",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                "interface:\n  display_name: Example Skill\n  short_description: Fixture.\n",
                encoding="utf-8",
            )
            previous = self._patch_root(root)
            try:
                output = self._capture_failure(
                    lambda: self.validator.validate_skill(entry, "approved")
                )
            finally:
                self._restore_root(previous)
        self.assertIn("SKILL.md license differs from manifest", output)

    def test_utf16_secret_in_public_text_payload_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            token = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            (root / "notes.txt").write_bytes(
                (b"A" * 9000) + b"!!" + token.encode("utf-16-le")
            )
            previous = self._patch_root(root)
            try:
                output = self._capture_failure(self.validator.scan_public_tree)
            finally:
                self._restore_root(previous)
        self.assertIn("GitHub token", output)

    def test_utf16_secret_in_archive_text_member_is_rejected(self) -> None:
        token = "sk" + "-" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        payload = (b"A" * 9000) + b"!!" + token.encode("utf-16-be")
        output = self._capture_failure(
            lambda: self.validator.scan_archive_member(
                payload, "references/notes.txt", "package.zip"
            )
        )
        self.assertIn("OpenAI-style secret key", output)

    def test_private_identifier_in_public_path_is_rejected(self) -> None:
        private_id = (
            "action-" + "1785621210329" + "-210329-" + "c1a4b863" + "-2ad5"
        )
        output = self._capture_failure(
            lambda: self.validator.scan_public_path(Path(private_id) / "file.txt")
        )
        self.assertIn("private Action Production identifier", output)

    def test_private_identifier_in_archive_member_path_is_rejected(self) -> None:
        private_id = (
            "fact-" + "1785621202220" + "-202220-" + "416a22f6" + "-f06a"
        )
        output = self._capture_failure(
            lambda: self.validator.scan_archive_member(
                b"public text", f"{private_id}/file.txt", "package.zip"
            )
        )
        self.assertIn("private Action Production identifier", output)

    def test_private_identifier_in_archive_directory_path_is_rejected(self) -> None:
        private_id = (
            "action-" + "1785621210329" + "-210329-" + "c1a4b863" + "-2ad5"
        )
        output = self._capture_failure(
            lambda: self.validator.validate_archive_member_name(
                f"{private_id}/", "package.zip"
            )
        )
        self.assertIn("private Action Production identifier", output)


if __name__ == "__main__":
    unittest.main()

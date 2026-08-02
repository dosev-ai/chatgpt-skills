from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import ModuleType

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_public_skills.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "validate_public_skills_package_metadata", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillPackageMetadataTests(unittest.TestCase):
    validator = load_validator()

    def _capture_failure(self, callback) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                callback()
        return output.getvalue()

    def _zip_bytes(self, *, location: str, secret: bytes) -> bytes:
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            info = zipfile.ZipInfo("README.md")
            if location == "entry_comment":
                info.comment = secret
            if location == "extra":
                info.extra = b"\x01\x00" + len(secret).to_bytes(2, "little") + secret
            archive.writestr(info, "public content\n")
            if location == "archive_comment":
                archive.comment = secret
        return output.getvalue()

    def test_zip_metadata_is_scanned(self) -> None:
        token = ("gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890").encode("ascii")
        for location in ("archive_comment", "entry_comment", "extra"):
            with self.subTest(location=location):
                payload = self._zip_bytes(location=location, secret=token)
                output = self._capture_failure(
                    lambda: self.validator.scan_zip_archive(payload, "package.zip")
                )
                self.assertIn("GitHub token", output)

    def test_artifact_status_none_rejects_arbitrary_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "skills" / "example-skill"
            skill_dir.mkdir(parents=True)
            with zipfile.ZipFile(skill_dir / "release.zip", "w") as archive:
                archive.writestr("README.md", "public content\n")
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
            try:
                entry = {
                    "id": "example-skill",
                    "path": "skills/example-skill",
                    "release_state": "public-released",
                    "artifact_status": "none",
                    "license": "MIT",
                    "public_pr": 7,
                    "public_merge_commit": "c" * 40,
                    "verification": "PASS: Clean-room invocation completed successfully.",
                    "residuals": [],
                }
                output = self._capture_failure(
                    lambda: self.validator.validate_release_evidence(
                        entry, "approved", True
                    )
                )
            finally:
                (
                    self.validator.ROOT,
                    self.validator.MANIFEST,
                    self.validator.SCHEMA,
                    self.validator.SKILLS_DIR,
                ) = previous
                self.validator._sync_paths()
        self.assertIn("artifact_status none requires no archive artifacts", output)


if __name__ == "__main__":
    unittest.main()

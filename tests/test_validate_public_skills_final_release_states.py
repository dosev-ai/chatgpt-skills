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
        "validate_public_skills_final_release_states", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillFinalReleaseStateTests(unittest.TestCase):
    validator = load_validator()

    def _capture_failure(self, callback) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                callback()
        return output.getvalue()

    def test_negated_passed_verification_is_rejected(self) -> None:
        entry = {
            "id": "example-skill",
            "path": "skills/example-skill",
            "release_state": "public-released",
            "artifact_status": "none",
            "license": "MIT",
            "public_pr": 7,
            "public_merge_commit": "c" * 40,
            "verification": "Clean-room invocation not passed",
            "residuals": [],
        }
        output = self._capture_failure(
            lambda: self.validator.validate_release_evidence(entry, "approved", True)
        )
        self.assertIn("affirmative clean-room verification evidence", output)

    def test_artifact_status_none_rejects_designated_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "skills" / "example-skill" / "skill.zip"
            package.parent.mkdir(parents=True)
            package.write_bytes(b"unexpected-package")
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
                    "verification": "Clean-room invocation passed.",
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
        self.assertIn("artifact_status none requires absence", output)


if __name__ == "__main__":
    unittest.main()

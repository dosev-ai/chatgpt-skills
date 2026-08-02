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
        "validate_public_skills_policy_hardening", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillPolicyHardeningTests(unittest.TestCase):
    validator = load_validator()

    def _capture_failure(self, callback) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                callback()
        return output.getvalue()

    def test_cache_named_directory_content_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache_dir = root / "__pycache__"
            cache_dir.mkdir()
            private_id = (
                "action-" + "1785621210329" + "-210329-" + "c1a4b863" + "-2ad5"
            )
            (cache_dir / "tracked.txt").write_text(private_id, encoding="utf-8")

            original_root = self.validator.ROOT
            try:
                self.validator.ROOT = root
                self.validator._sync_paths()
                output = self._capture_failure(self.validator.scan_public_tree)
            finally:
                self.validator.ROOT = original_root
                self.validator._sync_paths()

            self.assertIn("private Action Production identifier", output)
            self.assertIn("__pycache__/tracked.txt", output)

    def test_public_directory_rejects_non_mit_license(self) -> None:
        entry = {
            "id": "example-skill",
            "release_state": "public-pr-open",
            "artifact_status": "none",
            "license": "GPL-3.0",
            "public_pr": 7,
        }
        output = self._capture_failure(
            lambda: self.validator.validate_release_evidence(entry, "approved", True)
        )
        self.assertIn("requires per-skill license MIT", output)

    def test_public_release_rejects_blank_residual_text(self) -> None:
        entry = {
            "id": "example-skill",
            "release_state": "public-released",
            "artifact_status": "none",
            "license": "MIT",
            "public_pr": 7,
            "public_merge_commit": "c" * 40,
            "verification": "Clean-room invocation passed.",
            "residuals": [" "],
        }
        output = self._capture_failure(
            lambda: self.validator.validate_release_evidence(entry, "approved", True)
        )
        self.assertIn("residuals must contain only nonblank text", output)


if __name__ == "__main__":
    unittest.main()

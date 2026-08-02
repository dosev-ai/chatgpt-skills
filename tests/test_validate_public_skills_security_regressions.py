from __future__ import annotations

import contextlib
import importlib.util
import io
import tarfile
import unittest
from pathlib import Path
from types import ModuleType

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_public_skills.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_public_skills", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillSecurityRegressionTests(unittest.TestCase):
    validator = load_validator()

    def _release_entry(self, release_state: str, license_value: str = "pending") -> dict[str, object]:
        return {
            "id": "example-skill",
            "path": "skills/example-skill",
            "release_state": release_state,
            "artifact_status": "none",
            "license": license_value,
        }

    def _capture_failure(self, callback) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                callback()
        return output.getvalue()

    def _tar_bytes(self, member: tarfile.TarInfo, payload: bytes = b"safe") -> bytes:
        output = io.BytesIO()
        member.size = len(payload)
        with tarfile.open(fileobj=output, mode="w", format=tarfile.PAX_FORMAT) as archive:
            archive.addfile(member, io.BytesIO(payload))
        return output.getvalue()

    def test_candidate_directory_requires_approved_repository_license(self) -> None:
        for state in ("candidate-needs-sanitization", "ready-for-public-pr"):
            with self.subTest(state=state):
                entry = self._release_entry(state, license_value="MIT")
                output = self._capture_failure(
                    lambda: self.validator.validate_release_evidence(
                        entry, "pending-owner-decision", True
                    )
                )
                self.assertIn("requires approved repository license", output)

    def test_candidate_directory_requires_approved_per_skill_license(self) -> None:
        for state in ("candidate-needs-sanitization", "ready-for-public-pr"):
            with self.subTest(state=state):
                entry = self._release_entry(state)
                output = self._capture_failure(
                    lambda: self.validator.validate_release_evidence(entry, "approved", True)
                )
                self.assertIn("requires an approved per-skill license", output)

    def test_directoryless_not_candidate_may_remain_pending(self) -> None:
        entry = self._release_entry("not-candidate")
        self.validator.validate_release_evidence(entry, "pending-owner-decision", False)

    def test_utf16_secret_after_long_binary_prefix_is_rejected(self) -> None:
        secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        payload = (
            b"\x89PNG\r\n\x1a\n"
            + (b"A" * 9000)
            + b"!!"
            + secret.encode("utf-16-le")
        )
        output = self._capture_failure(
            lambda: self.validator.scan_binary(payload, ".png", "late-secret.png")
        )
        self.assertIn("GitHub token", output)

    def test_tar_pax_header_secret_is_rejected(self) -> None:
        secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        member = tarfile.TarInfo("safe.txt")
        member.pax_headers = {"comment": secret}
        archive_bytes = self._tar_bytes(member)
        output = self._capture_failure(
            lambda: self.validator.scan_tar_archive(archive_bytes, "metadata.tar")
        )
        self.assertIn("GitHub token", output)

    def test_tar_ownership_metadata_private_identifier_is_rejected(self) -> None:
        private_id = "action-" + "1234567890123-123456-deadbeef-cafe"
        member = tarfile.TarInfo("safe.txt")
        member.uname = private_id
        archive_bytes = self._tar_bytes(member)
        output = self._capture_failure(
            lambda: self.validator.scan_tar_archive(archive_bytes, "ownership.tar")
        )
        self.assertIn("private Action Production identifier", output)


if __name__ == "__main__":
    unittest.main()
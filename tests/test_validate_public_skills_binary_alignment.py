from __future__ import annotations

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from types import ModuleType

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_public_skills.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_public_skills_alignment", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillBinaryAlignmentTests(unittest.TestCase):
    validator = load_validator()

    def _capture_failure(self, callback) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                callback()
        return output.getvalue()

    def test_utf16le_secret_at_odd_byte_alignment_is_rejected(self) -> None:
        secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        payload = b"\x89PNG\r\n\x1a\n" + b"!" + secret.encode("utf-16-le")
        output = self._capture_failure(
            lambda: self.validator.scan_binary(payload, ".png", "odd-alignment.png")
        )
        self.assertIn("GitHub token", output)

    def test_utf16be_secret_at_odd_byte_alignment_is_rejected(self) -> None:
        secret = "sk" + "-" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        payload = b"%PDF-1.7\n" + b"!" + secret.encode("utf-16-be")
        output = self._capture_failure(
            lambda: self.validator.scan_binary(payload, ".pdf", "odd-alignment.pdf")
        )
        self.assertIn("OpenAI-style secret key", output)


if __name__ == "__main__":
    unittest.main()

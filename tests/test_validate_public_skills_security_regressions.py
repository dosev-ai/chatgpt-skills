from __future__ import annotations

import contextlib
import gzip
import importlib.util
import io
import struct
import tarfile
import unittest
import zlib
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

    def _pax_record(self, key: str, value: str) -> bytes:
        body = f"{key}={value}\n".encode("utf-8")
        length = len(body) + 2
        while True:
            record = f"{length} ".encode("ascii") + body
            if len(record) == length:
                return record
            length = len(record)

    def _duplicate_pax_tar_bytes(self) -> bytes:
        secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        pax_payload = self._pax_record("comment", secret) + self._pax_record(
            "comment", "safe"
        )
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            pax_member = tarfile.TarInfo("././@PaxHeader")
            pax_member.type = tarfile.XHDTYPE
            pax_member.size = len(pax_payload)
            archive.addfile(pax_member, io.BytesIO(pax_payload))
            member = tarfile.TarInfo("safe.txt")
            member.size = 4
            archive.addfile(member, io.BytesIO(b"safe"))
        return output.getvalue()

    def _gzip_with_metadata(self, payload: bytes, flag: int, metadata: bytes) -> bytes:
        compressor = zlib.compressobj(level=9, wbits=-zlib.MAX_WBITS)
        compressed = compressor.compress(payload) + compressor.flush()
        header = b"\x1f\x8b\x08" + bytes([flag]) + (b"\x00" * 4) + b"\x00\xff"
        if flag == 0x04:
            optional = struct.pack("<H", len(metadata)) + metadata
        elif flag in (0x08, 0x10):
            optional = metadata + b"\x00"
        else:
            raise ValueError(f"unsupported test gzip flag: {flag}")
        trailer = struct.pack(
            "<II",
            zlib.crc32(payload) & 0xFFFFFFFF,
            len(payload) & 0xFFFFFFFF,
        )
        return header + optional + compressed + trailer

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

    def test_duplicate_pax_key_secret_is_rejected_before_dictionary_collapse(self) -> None:
        raw_archive = self._duplicate_pax_tar_bytes()
        for archive_bytes, source in (
            (raw_archive, "duplicate-pax.tar"),
            (gzip.compress(raw_archive), "duplicate-pax.tar.gz"),
        ):
            with self.subTest(source=source):
                output = self._capture_failure(
                    lambda data=archive_bytes, name=source: self.validator.scan_tar_archive(
                        data, name
                    )
                )
                self.assertIn("GitHub token", output)

    def test_gzip_wrapper_metadata_secret_is_rejected(self) -> None:
        secret = ("gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890").encode("ascii")
        member = tarfile.TarInfo("safe.txt")
        raw_archive = self._tar_bytes(member)
        for flag, label in (
            (0x04, "extra"),
            (0x08, "filename"),
            (0x10, "comment"),
        ):
            with self.subTest(field=label):
                archive_bytes = self._gzip_with_metadata(raw_archive, flag, secret)
                output = self._capture_failure(
                    lambda data=archive_bytes, name=label: self.validator.scan_tar_archive(
                        data, f"gzip-{name}.tar.gz"
                    )
                )
                self.assertIn("GitHub token", output)


if __name__ == "__main__":
    unittest.main()
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

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_pr_open_packages.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_pr_open_packages", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PR-open package validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrOpenPackageParityTests(unittest.TestCase):
    validator = load_validator()

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.skill_dir = self.root / "skills" / "example-skill"
        self.skill_dir.mkdir(parents=True)
        (self.skill_dir / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: test\n---\n", encoding="utf-8"
        )
        (self.skill_dir / "README.md").write_text("public source\n", encoding="utf-8")
        self.entry = {
            "id": "example-skill",
            "path": "skills/example-skill",
            "version": "1.2.3",
            "release_state": "public-pr-open",
            "artifact_status": "package",
        }
        (self.root / "skills-manifest.yaml").write_text(
            yaml.safe_dump({"skills": [self.entry]}, sort_keys=False), encoding="utf-8"
        )
        self.previous = (self.validator.ROOT, self.validator.MANIFEST)
        self.validator.ROOT = self.root
        self.validator.MANIFEST = self.root / "skills-manifest.yaml"

    def tearDown(self) -> None:
        self.validator.ROOT, self.validator.MANIFEST = self.previous
        self.temp_dir.cleanup()

    def run_validator(self) -> tuple[int, str]:
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                result = self.validator.main()
        except SystemExit as exc:
            return int(exc.code), output.getvalue()
        return result, output.getvalue()

    def write_zip(self, files: dict[str, str], *, top_level: str | None = "example-skill") -> Path:
        package = self.skill_dir / "skill.zip"
        with zipfile.ZipFile(package, "w") as archive:
            for name, text in files.items():
                path = f"{top_level}/{name}" if top_level else name
                archive.writestr(path, text)
        return package

    def write_evidence(
        self,
        package: Path,
        *,
        checksum: str | None = None,
        size: int | None = None,
        inventory: list[str] | None = None,
    ) -> None:
        evidence_dir = self.root / "release-evidence"
        evidence_dir.mkdir()
        base = evidence_dir / "example-skill-v1.2.3-package"
        actual_checksum = hashlib.sha256(package.read_bytes()).hexdigest()
        (Path(f"{base}.sha256")).write_text(
            f"{checksum or actual_checksum}  skills/example-skill/skill.zip\n",
            encoding="utf-8",
        )
        (Path(f"{base}.size")).write_text(
            f"{size if size is not None else package.stat().st_size}\n",
            encoding="utf-8",
        )
        (Path(f"{base}.inventory")).write_text(
            "\n".join(inventory or ["README.md", "SKILL.md"]) + "\n",
            encoding="utf-8",
        )

    def matching_files(self) -> dict[str, str]:
        return {
            "README.md": "public source\n",
            "SKILL.md": "---\nname: example-skill\ndescription: test\n---\n",
        }

    def test_matching_standard_package_without_manifest_hash_passes(self) -> None:
        package = self.write_zip(self.matching_files())
        self.write_evidence(package)
        code, output = self.run_validator()
        self.assertEqual(code, 0)
        self.assertIn("PASS: 1 package(s)", output)

    def test_flat_package_fails(self) -> None:
        package = self.write_zip(self.matching_files(), top_level=None)
        self.write_evidence(package)
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("must use one top-level directory", output)

    def test_wrong_top_level_directory_fails(self) -> None:
        package = self.write_zip(self.matching_files(), top_level="wrong-name")
        self.write_evidence(package)
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("must use one top-level directory", output)

    def test_missing_package_fails(self) -> None:
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("requires regular artifact", output)

    def test_stale_incomplete_package_fails(self) -> None:
        package = self.write_zip({"SKILL.md": "stale\n"})
        self.write_evidence(package, inventory=["SKILL.md"])
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("contents differ from public skill tree", output)

    def test_stale_external_checksum_fails(self) -> None:
        package = self.write_zip(self.matching_files())
        self.write_evidence(package, checksum="0" * 64)
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("checksum differs from release evidence", output)

    def test_stale_external_size_fails(self) -> None:
        package = self.write_zip(self.matching_files())
        self.write_evidence(package, size=1)
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("size differs from release evidence", output)

    def test_stale_external_inventory_fails(self) -> None:
        package = self.write_zip(self.matching_files())
        self.write_evidence(package, inventory=["SKILL.md"])
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("inventory differs from public skill tree", output)


if __name__ == "__main__":
    unittest.main()

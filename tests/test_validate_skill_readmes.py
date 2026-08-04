from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_skill_readmes.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_skill_readmes", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load skill README validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillReadmeValidatorTests(unittest.TestCase):
    validator = load_validator()

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.validator.ROOT = self.root
        self.validator.SKILLS_DIR = self.root / "skills"
        self.validator.MANIFEST = self.root / "skills-manifest.yaml"
        self._write_manifest([])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _entry(
        self,
        *,
        release_state: str = "public-pr-open",
        artifact_status: str = "none",
    ) -> dict[str, object]:
        entry: dict[str, object] = {
            "id": "example-skill",
            "release_state": release_state,
            "artifact_status": artifact_status,
        }
        if release_state in {
            "public-pr-open",
            "public-merged-verification-pending",
            "public-released",
        }:
            entry["public_pr"] = 7
        if release_state == "public-released":
            entry["verification"] = "Clean-room invocation passed."
            entry["residuals"] = []
        return entry

    def _write_manifest(self, entries: list[dict[str, object]]) -> None:
        (self.root / "skills-manifest.yaml").write_text(
            yaml.safe_dump({"skills": entries}, sort_keys=False),
            encoding="utf-8",
        )

    def _release_lines(self, entry: dict[str, object]) -> str:
        verification = entry.get("verification", "pending")
        if not isinstance(verification, str):
            verification = str(verification)
        residuals = entry.get("residuals")
        if residuals is None:
            residual_text = "pending"
        elif isinstance(residuals, list) and not residuals:
            residual_text = "none"
        elif isinstance(residuals, list):
            residual_text = "; ".join(str(value) for value in residuals)
        else:
            residual_text = str(residuals)

        if entry["artifact_status"] == "package":
            return "\n".join(self.validator.PACKAGE_RELEASE_LINES) + "\n"

        public_pr = f"#{entry['public_pr']}" if "public_pr" in entry else "not yet opened"
        return (
            f"- Public release state: `{entry['release_state']}`\n"
            f"- Public pull request: `{public_pr}`\n"
            f"- Artifact status: `{entry['artifact_status']}`\n"
            f"- Clean-room verification: `{verification}`\n"
            f"- Known residuals: `{residual_text}`\n"
        )

    def _valid_readme(self, entry: dict[str, object]) -> str:
        sections = []
        for heading in self.validator.REQUIRED_HEADINGS:
            body = f"Specific content for {heading[3:].lower()}."
            if heading == "## Release status":
                body = self._release_lines(entry).rstrip()
            sections.append(f"{heading}\n\n{body}\n")
        return "# Example Skill\n\n" + "\n".join(sections)

    def _write_readme(self, content: str) -> Path:
        skill_dir = self.validator.SKILLS_DIR / "example-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "README.md").write_text(content, encoding="utf-8")
        return skill_dir

    def _run(self) -> tuple[int, str]:
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                result = self.validator.main()
        except SystemExit as exc:
            return int(exc.code), output.getvalue()
        return result, output.getvalue()

    def test_empty_foundation_passes(self) -> None:
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("0 skill README(s)", output)

    def test_complete_skill_readme_passes(self) -> None:
        entry = self._entry()
        self._write_manifest([entry])
        self._write_readme(self._valid_readme(entry))
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 skill README(s)", output)

    def test_package_readme_uses_stable_external_release_ledger(self) -> None:
        entry = self._entry(artifact_status="package")
        self._write_manifest([entry])
        self._write_readme(self._valid_readme(entry))
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 skill README(s)", output)

    def test_package_readme_remains_valid_after_manifest_state_changes(self) -> None:
        initial = self._entry(
            release_state="public-pr-open",
            artifact_status="package",
        )
        self._write_readme(self._valid_readme(initial))
        released = self._entry(
            release_state="public-released",
            artifact_status="package",
        )
        self._write_manifest([released])
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 skill README(s)", output)

    def test_package_readme_rejects_embedded_dynamic_release_state(self) -> None:
        entry = self._entry(artifact_status="package")
        self._write_manifest([entry])
        content = self._valid_readme(entry).replace(
            "- Public release state: `See skills-manifest.yaml`",
            "- Public release state: `public-pr-open`",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("release status differs from manifest", output)

    def test_missing_required_section_is_rejected(self) -> None:
        entry = self._entry()
        self._write_manifest([entry])
        content = self._valid_readme(entry).replace(
            "## Benefits\n\nSpecific content for benefits.\n",
            "",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires exactly one '## Benefits' section", output)

    def test_empty_required_section_is_rejected(self) -> None:
        entry = self._entry()
        self._write_manifest([entry])
        content = self._valid_readme(entry).replace(
            "## Limitations\n\nSpecific content for limitations.\n",
            "## Limitations\n\n",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("must not be empty", output)

    def test_out_of_order_sections_are_rejected(self) -> None:
        entry = self._entry()
        self._write_manifest([entry])
        content = self._valid_readme(entry)
        benefits = "## Benefits\n\nSpecific content for benefits.\n"
        why = "## Why it exists\n\nSpecific content for why it exists.\n"
        content = content.replace(why + "\n" + benefits, benefits + "\n" + why)
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("required sections are out of order", output)

    def test_stale_release_state_is_rejected(self) -> None:
        entry = self._entry(release_state="public-pr-open")
        self._write_manifest([entry])
        content = self._valid_readme(entry).replace(
            "- Public release state: `public-pr-open`",
            "- Public release state: `public-released`",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("release status differs from manifest", output)

    def test_released_evidence_fields_are_bound(self) -> None:
        entry = self._entry(release_state="public-released")
        self._write_manifest([entry])
        content = self._valid_readme(entry).replace(
            "- Clean-room verification: `Clean-room invocation passed.`",
            "- Clean-room verification: `pending`",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("release status differs from manifest", output)

    def test_duplicate_release_field_outside_section_is_rejected(self) -> None:
        entry = self._entry()
        self._write_manifest([entry])
        content = self._valid_readme(entry).replace(
            "Specific content for benefits.",
            "Specific content for benefits.\n\n- Public release state: `public-pr-open`",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires exactly one '- Public release state:' field", output)

    def test_release_field_only_outside_section_is_rejected(self) -> None:
        entry = self._entry()
        self._write_manifest([entry])
        expected = "- Artifact status: `none`"
        content = self._valid_readme(entry).replace(expected + "\n", "")
        content = content.replace(
            "Specific content for benefits.",
            f"Specific content for benefits.\n\n{expected}",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("must appear inside the Release status section", output)

    def test_non_string_verification_fails_cleanly(self) -> None:
        entry = self._entry(release_state="public-released")
        entry["verification"] = None
        self._write_manifest([entry])
        self._write_readme(self._valid_readme(entry))
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("manifest verification must be text", output)

    def test_non_list_residuals_fail_cleanly(self) -> None:
        entry = self._entry(release_state="public-released")
        entry["residuals"] = "none"
        self._write_manifest([entry])
        self._write_readme(self._valid_readme(entry))
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("manifest residuals must be a list", output)

    def test_non_string_residual_item_fails_cleanly(self) -> None:
        entry = self._entry(release_state="public-released")
        entry["residuals"] = [7]
        self._write_manifest([entry])
        self._write_readme(self._valid_readme(entry))
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("manifest residuals must contain only text", output)

    def test_duplicate_manifest_skill_ids_are_rejected(self) -> None:
        entry = self._entry()
        self._write_manifest([entry, dict(entry)])
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("duplicate skill ID: example-skill", output)

    def test_symlinked_skill_directory_is_rejected(self) -> None:
        target = self.root / "outside-skill"
        target.mkdir()
        self.validator.SKILLS_DIR.mkdir(parents=True)
        (self.validator.SKILLS_DIR / "example-skill").symlink_to(
            target, target_is_directory=True
        )
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("public skill directory must not be a symlink", output)


if __name__ == "__main__":
    unittest.main()

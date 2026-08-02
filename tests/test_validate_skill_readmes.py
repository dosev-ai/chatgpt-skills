from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

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

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _valid_readme(self) -> str:
        sections = []
        for heading in self.validator.REQUIRED_HEADINGS:
            sections.append(f"{heading}\n\nSpecific content for {heading[3:].lower()}.\n")
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
        self._write_readme(self._valid_readme())
        code, output = self._run()
        self.assertEqual(code, 0)
        self.assertIn("1 skill README(s)", output)

    def test_missing_required_section_is_rejected(self) -> None:
        content = self._valid_readme().replace(
            "## Benefits\n\nSpecific content for benefits.\n",
            "",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("requires exactly one '## Benefits' section", output)

    def test_empty_required_section_is_rejected(self) -> None:
        content = self._valid_readme().replace(
            "## Limitations\n\nSpecific content for limitations.\n",
            "## Limitations\n\n",
        )
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("must not be empty", output)

    def test_out_of_order_sections_are_rejected(self) -> None:
        content = self._valid_readme()
        benefits = "## Benefits\n\nSpecific content for benefits.\n"
        why = "## Why it exists\n\nSpecific content for why it exists.\n"
        content = content.replace(why + "\n" + benefits, benefits + "\n" + why)
        self._write_readme(content)
        code, output = self._run()
        self.assertEqual(code, 1)
        self.assertIn("required sections are out of order", output)


if __name__ == "__main__":
    unittest.main()

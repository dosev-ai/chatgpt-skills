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
    spec = importlib.util.spec_from_file_location("validate_public_skills_lineage", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load public skill validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicSkillCanonicalLineageTests(unittest.TestCase):
    validator = load_validator()
    canonical = {
        "repository": "deldos/skills",
        "path": "skills/example-skill",
        "version": "1.2.3",
        "source_pr": 42,
        "final_pr_head": "a" * 40,
        "merge_commit": "b" * 40,
    }

    def _valid_lines(self) -> list[str]:
        return [
            "# Example Skill",
            "",
            "## What it does",
            "",
            "Example.",
            "",
            "## Canonical lineage",
            "",
            "- Canonical repository: `deldos/skills`",
            "- Canonical path: `skills/example-skill`",
            "- Canonical version: `1.2.3`",
            "- Canonical source PR: `#42`",
            f"- Canonical final PR HEAD: `{'a' * 40}`",
            f"- Canonical merge commit: `{'b' * 40}`",
            "",
            "## Release status",
            "",
            "Pending.",
        ]

    def _capture_failure(self, lines: list[str]) -> str:
        output = io.StringIO()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(output):
                self.validator.validate_canonical_lineage(
                    lines, self.canonical, "example-skill"
                )
        return output.getvalue()

    def test_exact_unique_fields_inside_section_pass(self) -> None:
        self.validator.validate_canonical_lineage(
            self._valid_lines(), self.canonical, "example-skill"
        )

    def test_stale_section_with_matching_copy_elsewhere_is_rejected(self) -> None:
        lines = self._valid_lines()
        index = lines.index("- Canonical version: `1.2.3`")
        lines[index] = "- Canonical version: `1.2.2`"
        lines.insert(4, "- Canonical version: `1.2.3`")
        output = self._capture_failure(lines)
        self.assertIn("requires exactly one '- Canonical version:' field", output)

    def test_field_only_outside_lineage_section_is_rejected(self) -> None:
        lines = self._valid_lines()
        expected = "- Canonical source PR: `#42`"
        lines.remove(expected)
        lines.insert(4, expected)
        output = self._capture_failure(lines)
        self.assertIn("must appear inside the Canonical lineage section", output)


if __name__ == "__main__":
    unittest.main()

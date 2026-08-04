# Governed PRD Creation v1.1.1 package evidence

- Public skill source: `skills/governed-prd-creation/`
- Installable artifact: `skills/governed-prd-creation/skill.zip`
- Package SHA-256: `9642eced97299740157fea73c1d4fd329d2e9378323669acf0c580604ede7503`
- Package size: `14,326 bytes`
- Package files: `13`
- Layout: single-skill archive rooted at `SKILL.md`
- Source parity: `PRE-MERGE PASS` — every packaged path and byte matches the exact PR-head public skill tree, excluding the package itself.
- Skill validation: `PRE-MERGE PASS` — the extracted archive passed the `skill-creator` validator.
- PR-open package gate: `PASS` — the mandatory Public Skill Validation workflow requires the package to exist and match the public source tree even before a manifest checksum is published.
- Canonical source: `deldos/skills` PR #33, merge `f218d5ffaddcab12a736420166f3348b31183dac`.
- Prior source-only public skill merge: `ee6c7a853b18e8f3928f1c5a299a0d9750fcfb2c`.
- Package publication PR: `#4`.
- Post-merge verification: `pending`.

Before the package-containing merge is verified, installers should compare `skill.zip` with `release-evidence/governed-prd-creation-v1.1.1-package.sha256`. After merged-tree verification, the same checksum and package-containing merge commit will be promoted into `skills-manifest.yaml` by an evidence-only pull request.

Mutable release state, merge lineage, checksum promotion, and final verification remain outside the ZIP, preventing a self-referential package hash.

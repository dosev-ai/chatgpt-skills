# Governed PRD Creation v1.1.1 package evidence

- Public skill source: `skills/governed-prd-creation/`
- Installable artifact: `skills/governed-prd-creation/skill.zip`
- Package SHA-256: `7360064f2ebe4fc0bd18b0eeb33251114170dce32a0238578da1e388ea4c98a7`
- Package size: `14,436 bytes`
- Package files: `13`
- Layout: single-skill archive rooted at `SKILL.md`
- Source parity: `PASS` — every packaged path and byte matches the public skill tree, excluding the package itself.
- Skill validation: `PASS` — the extracted archive passed the `skill-creator` validator.
- Canonical source: `deldos/skills` PR #33, merge `f218d5ffaddcab12a736420166f3348b31183dac`.
- Public skill merge: `ee6c7a853b18e8f3928f1c5a299a0d9750fcfb2c`.

The package checksum is recorded outside the skill directory to avoid a self-referential package-content dependency. The skill README points to the authoritative `package_sha256` field in `skills-manifest.yaml` rather than embedding the checksum inside the ZIP.

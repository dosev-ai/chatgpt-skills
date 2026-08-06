# Governed PRD Creation v1.1.1 package evidence

- Public skill source: `skills/governed-prd-creation/`
- Installable artifact: `skills/governed-prd-creation/skill.zip`
- Package SHA-256: `a8cad6237999b2c8174a93cd36f92f093b48767cb4735c7a9e5916cddb510f07`
- Package size: `14,898 bytes`
- Package files: `13`
- Layout: standard `skill-creator` single-skill archive with one top-level `governed-prd-creation/` directory and one `governed-prd-creation/SKILL.md` entrypoint.
- Source parity: `PRE-MERGE PASS` — after removing the required top-level directory prefix, every packaged path and byte matches the exact public skill tree, excluding the package itself.
- Skill validation: `PRE-MERGE PASS` — the source directory and cleanly extracted archive passed the `skill-creator` validator.
- Package gate: `PASS` — the validator now requires the standard top-level skill directory and rejects flat-rooted or incorrectly named archives.
- Regression tests: `9/9 PASS`, including flat-package, wrong-top-level-directory, and missing-`SKILL.md`-entrypoint failures.
- Canonical source: `deldos/skills` PR #33, merge `f218d5ffaddcab12a736420166f3348b31183dac`.
- Faulty package publication: public PR #4, merge `811f13fa0fa3dce9123612376678d30b7f20ac5b`; the flat-rooted archive and its prior checksum evidence are superseded by this repair.
- ChatGPT upload/replacement validation: `pending user runtime confirmation`.
- Post-merge verification: `pending`.

Installers should use the package checksum recorded in `release-evidence/governed-prd-creation-v1.1.1-package.sha256`. The skill remains verification-pending until the repaired package is merged and a ChatGPT upload or replacement succeeds.

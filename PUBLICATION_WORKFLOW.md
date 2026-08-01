# Public Skill Publishing Workflow

## 1. Candidate intake

Record the skill ID, canonical path and version, canonical visibility, reviewed source commit, target audience, public value, proposed release order, and known private dependencies.

## 2. Public-safety design

Define:

- a connector-independent standalone path;
- optional connected behavior where useful;
- removed private assumptions and identifiers;
- public examples and expected outputs;
- secret, personal-data, confidentiality, license, and attribution checks.

## 3. Canonical preparation

When the canonical source is not already public-ready:

1. create an isolated branch in `deldos/skills`;
2. update the complete skill, references, agent metadata, changelog, semantic version, and manifest;
3. run structural validation and focused tests;
4. open a canonical pull request;
5. disposition automated findings and resolve review threads;
6. require accepted exact-final-HEAD review for public/private-boundary changes;
7. merge only when repository gates and owner authorization pass.

## 4. Public projection

Build the public projection from the reviewed canonical merge commit, never from a pre-review folder or package.

Create a separate branch and pull request in this repository. Include:

- the complete public skill directory;
- public README and usage example;
- canonical source lineage;
- license and attribution information;
- validation and clean-room test plan.

## 5. Public review

Verify:

- no secrets, personal data, private endpoints, internal IDs, or confidential content;
- no mandatory private connector or internal-skill dependency;
- version and canonical source lineage are accurate;
- instructions and examples work for a fresh user;
- package structure and documentation validate;
- all findings are dispositioned and exact-final-HEAD requirements pass.

## 6. Release and verification

After merge:

- verify the public tree and source lineage;
- create a package or release artifact when required;
- record its SHA-256;
- run a clean-room installation or invocation;
- record the public PR, final HEAD, merge commit, verification result, residuals, and final state.

## 7. Repair loop

Record a public defect against the canonical skill, repair it through the canonical review cycle, then repeat public projection. Do not let the public repository become an independent source of truth.

## Starter-pack sequence

1. `governed-prd-creation`
2. `session-handoff-compact`
3. `governed-excel-creation`

Each release blocks the next until its canonical and public evidence gates are complete.

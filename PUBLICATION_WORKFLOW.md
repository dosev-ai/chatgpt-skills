# Public Skill Publishing Workflow

## Operating model: two editions, one source of truth

Each promoted skill has two controlled editions:

- **Private/full edition** — the complete skill in the private canonical repository, including private integrations and operating context where applicable.
- **Public/sanitized edition** — the portable edition published here with connector-independent instructions, neutral examples, explicit limitations and public-safe lineage.

The public edition is a reviewed projection, not an independent fork. Public preparation must not remove or downgrade private-only capability. Only the sanitized edition may appear in this repository.

## 1. Candidate intake

Record the skill ID, canonical path and version, canonical visibility, reviewed source commit, target audience, public value, proposed release order, known private dependencies and intended artifact status.

Use `not-candidate` when a reviewed candidate is explicitly excluded from promotion. Use `candidate-needs-sanitization` when public-safety work remains.

## 2. Public-safety design

Define:

- a connector-independent standalone path;
- optional connected behavior where useful;
- private capabilities that must remain available only in the full edition;
- removed private assumptions and identifiers;
- public examples and expected outputs;
- complete-tree secret, personal-data, confidentiality, license and attribution checks;
- whether a package or release artifact will be distributed;
- the clean-room verification criteria.

The public design must preserve useful behavior without exposing private operating details. Sanitization is not permission to weaken the private canonical skill.

## 3. Canonical preparation

When the canonical source is not already public-ready:

1. create an isolated branch in the private canonical repository;
2. update the complete skill, references, agent metadata, changelog, semantic version and manifest;
3. add a portable operating path while preserving the private/full operating path;
4. run structural validation, focused tests and a private-edition non-regression review;
5. open a canonical pull request;
6. disposition automated findings and resolve review threads;
7. require accepted exact-final-HEAD review for public/private-boundary changes;
8. merge only when repository gates and owner authorization pass.

## 4. Public projection

Build the public projection from the reviewed canonical merge commit, never from a pre-review folder, pull-request branch or old package.

Create a separate branch and pull request in this repository. Include:

- the complete public skill directory;
- a dedicated human-facing `README.md`;
- `SKILL.md`, `CHANGELOG.md`, `agents/openai.yaml` and all required public references;
- structured canonical source lineage;
- approved license and attribution information;
- artifact status: `none` or `package`;
- validation, pre-merge invocation and post-merge clean-room test plans.

Move the candidate to `ready-for-public-pr`, then `public-pr-open` when the pull request exists.

## 5. Per-skill README contract

Every public skill must contain `skills/<skill-id>/README.md`. It must help a person decide whether and how to use the skill without reading the full operating contract first.

Required sections:

1. `## What it does`
2. `## Why it exists`
3. `## Benefits`
4. `## When to use it`
5. `## How it works`
6. `## Limitations`
7. `## Canonical lineage`
8. `## Release status`

The README must be specific to the skill. Generic boilerplate, empty sections or benefit claims unsupported by the skill contract are not acceptable.

Use [SKILL_README_TEMPLATE.md](SKILL_README_TEMPLATE.md). The canonical-lineage section must contain the exact labeled values required by the repository validator.

## 6. Public pre-merge review

Verify before merge:

- the complete public tree contains no secrets, personal data, private endpoints, internal IDs or confidential content;
- no mandatory private connector or internal-skill dependency remains;
- the private/full edition remains preserved in the canonical source;
- version and structured canonical source lineage are accurate;
- the dedicated README clearly explains purpose, rationale, benefits, usage and limitations;
- instructions and examples work from the proposed public tree;
- package structure and documentation validate;
- repository and per-skill licensing are approved;
- all findings are dispositioned and all review threads are resolved;
- the trusted base-branch gate confirms automated review of the exact final PR HEAD;
- any required pre-merge invocation or package test passes.

The public merge commit and clean-room verification against merged content do not exist yet and are not pre-merge requirements.

## 7. Merge and verification-pending state

After the public pull request merges:

1. record the public merge commit;
2. move the skill to `public-merged-verification-pending`;
3. verify the merged public tree and canonical lineage;
4. when artifact status is `package`, rebuild the package from the public merge commit and record its SHA-256;
5. when artifact status is `none`, record that no package was distributed;
6. run a clean-room installation or invocation against the merged public content;
7. confirm the README matches the delivered behavior;
8. record the verification result, residuals and evidence references.

## 8. Public release

Move the skill to `public-released` only when:

- the public merge commit is recorded;
- clean-room installation or invocation passes;
- artifact status and hash evidence are complete;
- the dedicated skill README is complete and accurate;
- final residuals and limitations are recorded;
- repository and per-skill licensing remain valid.

## 9. Repair loop

Public users report defects through the public issue tracker. Maintainers classify the report as canonical, public-transformation or both.

When the defect applies to the skill itself, repair it through the private canonical review cycle before repeating public projection. Only transformation-specific documentation or packaging defects may be repaired directly here, with the boundary documented. Do not let the public repository become an independent source of truth.

## Starter-pack sequence

1. `governed-prd-creation`
2. `session-handoff-compact`
3. `governed-excel-creation`

Each release blocks the next until its canonical merge, public merge and post-merge verification gates are complete.

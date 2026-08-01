# Public Skill Publishing Workflow

## 1. Candidate intake

Record the skill ID, canonical path and version, canonical visibility, reviewed source commit, target audience, public value, proposed release order, and known private dependencies.

Use `not-candidate` when a reviewed candidate is explicitly excluded from promotion. Use `candidate-needs-sanitization` when public-safety work remains.

## 2. Public-safety design

Define:

- a connector-independent standalone path;
- optional connected behavior where useful;
- removed private assumptions and identifiers;
- public examples and expected outputs;
- complete-tree secret, personal-data, confidentiality, license, and attribution checks;
- whether a package or release artifact will be distributed.

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
- structured canonical source lineage;
- approved license and attribution information;
- artifact status: `none` or `package`;
- validation, pre-merge invocation, and post-merge clean-room test plans.

Move the candidate to `ready-for-public-pr`, then `public-pr-open` when the pull request exists.

## 5. Public pre-merge review

Verify before merge:

- the complete public tree contains no secrets, personal data, private endpoints, internal IDs, or confidential content;
- no mandatory private connector or internal-skill dependency remains;
- version and structured canonical source lineage are accurate;
- instructions and examples work from the proposed public tree;
- package structure and documentation validate;
- repository and per-skill licensing are approved;
- all findings are dispositioned and all review threads are resolved;
- the trusted base-branch gate confirms automated review of the exact final PR HEAD;
- any required pre-merge invocation or package test passes.

The public merge commit and clean-room verification against merged content do not exist yet and are not pre-merge requirements.

## 6. Merge and verification-pending state

After the public pull request merges:

1. record the public merge commit;
2. move the skill to `public-merged-verification-pending`;
3. verify the merged public tree and canonical lineage;
4. when artifact status is `package`, rebuild the package from the public merge commit and record its SHA-256;
5. when artifact status is `none`, record that no package was distributed;
6. run a clean-room installation or invocation against the merged public content;
7. record the verification result, residuals, and evidence references.

## 7. Public release

Move the skill to `public-released` only when:

- the public merge commit is recorded;
- clean-room installation or invocation passes;
- artifact status and hash evidence are complete;
- final residuals and limitations are recorded;
- repository and per-skill licensing remain valid.

## 8. Repair loop

Public users report defects through the public issue tracker. Maintainers classify the report and, when the defect applies to the canonical skill, repair it through the private canonical review cycle before repeating public projection. Do not let the public repository become an independent source of truth.

## Starter-pack sequence

1. `governed-prd-creation`
2. `session-handoff-compact`
3. `governed-excel-creation`

Each release blocks the next until its canonical, public merge, and post-merge verification gates are complete.

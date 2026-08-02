# Governed ChatGPT Skills

A deliberately small collection of reusable ChatGPT skills published through a governed, evidence-backed release process.

## What this repository contains

This repository contains only **public-safe skill editions**. It does not contain the owner's full private skill implementations, private connectors, internal operating references, confidential examples, or private project identifiers.

The private canonical repository remains the source of truth. This repository is a downstream publishing surface for reviewed, sanitized editions that can be understood and used outside the private operating environment.

## Two editions, one source of truth

| Edition | Purpose | Typical content | Visibility |
| --- | --- | --- | --- |
| Private/full edition | Operate inside the owner's governed environment | Private integrations, specialist routing, internal references, connected governance and full operational context | Private |
| Public/sanitized edition | Provide a portable and understandable public skill | Connector-independent workflow, neutral examples, public documentation, limitations and source lineage | Public |

The public edition is not an independent fork. Material skill changes are made and reviewed in the private canonical source first, then projected into this repository from a specific reviewed merge commit.

## How public publishing works

1. **Select a candidate.** Confirm that the skill has public value and can be safely separated from private operating context.
2. **Prepare the canonical skill.** Add or repair the portable operating mode, public-safe examples, metadata, version and changelog in the private canonical repository.
3. **Review and merge the canonical change.** Run validation, resolve review findings and require automated review of the exact final pull-request HEAD.
4. **Create the public projection.** Build the sanitized public edition from the reviewed canonical merge commit, never from an unmerged branch or an old package.
5. **Review the public pull request.** Validate structure, documentation, lineage, licensing, public safety and the exact final public HEAD.
6. **Verify after merge.** Test the merged public content in a clean environment before classifying the skill as publicly released.

See [PUBLICATION_WORKFLOW.md](PUBLICATION_WORKFLOW.md) for the complete workflow and [GOVERNANCE.md](GOVERNANCE.md) for authority and repair rules.

## Governed Work Starter Pack

The initial release sequence is:

| Order | Skill | Purpose | Current public state |
| --- | --- | --- | --- |
| 1 | `governed-prd-creation` | Define measurable product intent before architecture or implementation planning | Canonical preparation and public documentation in progress |
| 2 | `session-handoff-compact` | Preserve verified context when work moves to a new conversation or operator | Blocked by Release 1 |
| 3 | `governed-excel-creation` | Create and repair controlled business workbooks with validation and lineage | Blocked by Release 2 |

No skill is considered released merely because a branch, ZIP archive, pull request or merge commit exists.

## Dedicated README for every skill

Every public skill must include its own `skills/<skill-id>/README.md`. The README is for people evaluating or adopting the skill; `SKILL.md` remains the machine-readable operating contract.

Each skill README must explain:

- **What it does** — the outcome and scope.
- **Why it exists** — the problem it addresses.
- **Benefits** — the practical value for users and teams.
- **When to use it** — suitable use cases and trigger conditions.
- **How it works** — a concise workflow and expected outputs.
- **Limitations** — boundaries, dependencies and claims it does not make.
- **Canonical lineage** — exact source repository, path, version, pull request, final HEAD and merge commit.
- **Release status** — public state, verification evidence and known residuals.

Use [SKILL_README_TEMPLATE.md](SKILL_README_TEMPLATE.md) when preparing a public skill.

## Repository structure

```text
skills/<skill-id>/
├── README.md           # Human-facing purpose, benefits, usage and lineage
├── SKILL.md            # ChatGPT skill instructions and metadata
├── CHANGELOG.md        # Version history
├── agents/openai.yaml  # ChatGPT interface metadata
└── references/         # Public-safe supporting material
```

## Use, attribution, and risk

Public repository content is available under the standard [MIT License](LICENSE).

You may use, copy, modify, merge, publish, distribute, sublicense, or sell the public skill editions. Copies or substantial portions must retain the copyright and MIT license notice.

- **Copyright:** `Copyright (c) 2026 Delyan Dosev`
- **Preferred origin reference:** `Delyan Dosev — dosev-ai/chatgpt-skills`
- **Risk:** the content is provided as-is without warranty; users are responsible for evaluating and applying it in their own environment.

See [LICENSE-STATUS.md](LICENSE-STATUS.md) for the licensing and contribution policy.

## Public reports and contributions

Use the public issue form for defects, documentation gaps, installation problems, public-safety concerns or feature requests. Include only public-safe evidence.

Public reports are classified as canonical defects, public-transformation defects or both. Canonical defects are repaired in the private source first and then re-promoted so this repository does not become a second source of truth.

The initial contribution model is maintainer-controlled. Public-safe issue reports are welcome, but unsolicited third-party-authored skill content and substantive patches are not accepted until a separate inbound contribution policy is approved. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting anything.

## Release status

The repository foundation and first public skill are under governed review. No starter-pack skill is currently classified as `public-released`.

The MIT licensing decision is approved and implemented on the foundation branch. It removes the prior license-decision blocker but does not bypass canonical merge, public review, exact-head validation, or clean-room release gates.

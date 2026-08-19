# Skill UAT and Dry Runs

## Representative stories

### DR-01 — Driver-based budget

Create monthly budget, actual, variance, and forecast sheets with assumptions, formulas, dashboard, chart, controlled inputs, and complete metadata.

### DR-02 — Supplier-spend analysis

Create raw transactions, supplier/category mapping, calculations, ranked outputs, charts, and lineage metadata.

### DR-03 — Operational project tracker

Create controlled status and priority inputs, dates, progress, risks, KPI summary, conditional formatting, chart, and metadata.

### DR-04 — Undocumented workbook onboarding

Preserve an existing workbook while adding draft metadata that distinguishes observed structure from unknown business meaning.

### DR-05 — Metadata-first continuation

Start in a new session, read `_MCP_META` first, extend the workbook safely, and update requirements, fields, rules, relationships, validations, and change history.

## Authoring-control negative paths

Test these after material lifecycle changes:

- multiple plausible workbook targets -> block;
- source fingerprint changed after plan -> stale-plan rejection;
- approval bound to a different plan hash -> reject with no mutation;
- missing target range or table -> block;
- partial operation failure -> rollback or leave source unchanged;
- undeclared workbook delta -> fail validation;
- `safe_to_open=true` but usability defects remain -> `ready_for_review=false`;
- rollback locator missing for material rework -> fail distribution readiness.

## Reformatting negative paths

- missing style reference;
- inheritance cycle;
- equal-priority conflicting region definitions;
- target sheet or object missing;
- format-only operation changes a formula or value;
- unlisted region changes unexpectedly.

## Required evidence per run

- source and output workbook artifacts;
- plan and snapshot identifiers where applicable;
- metadata-validator result;
- key-range and formula inspection;
- formula-error scan;
- expected-versus-observed delta;
- rendered output and metadata preview;
- PASS, CONDITIONAL_PASS, or FAIL verdict;
- repair or learning record.

## Current baseline

The initial five representative stories passed on 2026-07-18. The undocumented DR-04 baseline correctly failed before onboarding and passed after metadata was added. Re-run the applicable stories after changes to metadata schemas, planning/approval logic, reformatting resolution, preservation rules, or validation gates.


### DR-06 — README and maintenance projection

Create or onboard a standard business workbook with `README` as the first visible sheet. Verify purpose, ownership, version, refresh guidance, validation status, and navigation are linked or generated from `_MCP_META`. Add `MAINTENANCE` and `tbl_meta_maintenance` only when procedures exceed the compact README pattern. Test broken hyperlinks, stale projected values, missing validation references, and accidental disclosure of sensitive local paths.


### DR-07 — Repeatable connected-source workflow workbook

Create a workflow-enabled workbook from at least one real connected source. Include `README`, `WORKFLOW`, business output sheets, `EVIDENCE`, `RUN_HISTORY`, `CHANGE_LOG`, and `_MCP_META`. Validate the workflow metadata bundle, source authority roles, required versus optional source behavior, step checklist, run history, and separation between a workflow run and a workbook design change. Execute one complete run, record an optional-source skip or warning where applicable, render-review the workbook, and leave independent distribution acceptance pending unless separately performed.

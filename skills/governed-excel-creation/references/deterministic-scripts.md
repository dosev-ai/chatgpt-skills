# Deterministic Script Automation

## Contents

- Purpose
- Script map
- Recommended sequence
- Plan request minimum
- Gate interpretation
- Output discipline

## Purpose

Use these scripts when code execution is available to replace repeated manual inspection, plan hashing, target checks, delta comparison, and readiness-envelope assembly. Keep workbook design, formula choice, visual review, and business acceptance with ChatGPT or the responsible reviewer.

All bundled scripts use the Python standard library. Workbook scripts inspect OOXML directly; connector adapters normalize JSON previously retrieved by connector tools. They do not call networks, authenticate to connectors, or edit the workbook. The only files they create are JSON packets, manifests, context, plans, and evidence reports.

## Script map

| Script | Use |
|---|---|
| `workbook_context.py` | Extract stable workbook fingerprint, sheet/table inventory, formula counts, defined names, drawings, and metadata presence. |
| `validate_meta_contract.py` | Validate required and optional `_MCP_META` Excel Tables, formatting metadata relationships, maintenance procedures, and workflow-definition/run relationships. |
| `build_change_plan.py` | Convert a JSON request into a versioned target-locked change plan with a plan ID and content hash. |
| `build_workflow_run.py` | Validate a compact workflow definition and emit a planned run envelope with definition hash, input fingerprint, run ID, and step checklist. |
| `validate_source_packet.py` | Validate a source packet or merged source manifest and verify its fingerprint. |
| `merge_source_packets.py` | Merge validated connector packets into `source-manifest-v1` without collapsing authority roles. |
| `verify_change_plan.py` | Reject modified plans, stale workbook targets, or approval hashes that do not match the current plan. |
| `compare_workbooks.py` | Compare pre-change and post-change OOXML packages and detect changed sheets outside the declared plan. |
| `run_governed_checks.py` | Compose metadata, target, delta, cached-error, visual-review, acceptance, and rollback evidence into one result envelope. |

`_ooxml.py` is a shared implementation module. Do not call it directly.

## Recommended sequence

### New substantive workbook

1. Build the workbook with native spreadsheet tooling.
2. Run metadata validation.
3. Run workbook context extraction.
4. Render and review the workbook.
5. Run the combined checks with explicit visual and acceptance flags only after those reviews occurred.

```bash
python scripts/validate_meta_contract.py output.xlsx --output meta-validation.json
python scripts/workbook_context.py output.xlsx --output workbook-context.json
python scripts/run_governed_checks.py output.xlsx \
  --visual-review-pass \
  --acceptance-pass \
  --output governed-result.json
```

### Existing-workbook modification

1. Extract the source context.
2. Define a JSON plan request.
3. Generate the target-locked plan.
4. Present the preview and obtain approval when required.
5. Verify the unchanged source immediately before mutation.
6. Modify the workbook through native tooling.
7. Compare before and after.
8. Run combined validation.

```bash
python scripts/workbook_context.py source.xlsx --output source-context.json
python scripts/build_change_plan.py source.xlsx plan-request.json --output plan.json
python scripts/verify_change_plan.py source.xlsx plan.json \
  --approved-plan-hash <approved-hash>
python scripts/compare_workbooks.py source.xlsx output.xlsx \
  --plan plan.json \
  --allow-meta-update \
  --output delta.json
python scripts/run_governed_checks.py output.xlsx \
  --before source.xlsx \
  --plan plan.json \
  --approved-plan-hash <approved-hash> \
  --visual-review-pass \
  --acceptance-pass \
  --output governed-result.json
```

## Plan request minimum

Provide:

- `intent`
- `risk_tier`
- a non-empty `operations` array
- unique `operation_id` values
- an operation name and target object for every operation

Recommended optional fields:

- `requirements`
- `preservation_rules`
- `validation_checks`
- `approval_required`
- `rollback_required`

Targets should identify sheets explicitly where possible:

```json
{
  "operation_id": "OP-01",
  "operation": "apply_region_style",
  "target": {
    "sheet": "Summary",
    "address": "A1:H2"
  },
  "preserve": ["values", "formulas"]
}
```

## Gate interpretation

- A changed source fingerprint invalidates the plan.
- An approval-required plan must receive the exact current `plan_hash` as its approval binding.
- A modified plan fails its own hash check.
- A changed sheet outside the plan is undeclared drift.
- `_MCP_META` may change as evidence and design declarations are synchronized.
- Cached OOXML error cells are reported but are not blocking by default because they may be stale or intentional. Use `--block-cached-errors` only when the workbook contract requires it.
- `--visual-review-pass` must represent a real render review; never use it automatically.
- `--acceptance-pass` must represent actual user, reviewer, or defined acceptance evidence.
- These scripts never prove native Excel recalculation. Use a verified native Excel session or another explicitly validated recalculation engine when recalculation is required.

## Output discipline

Store generated plan and evidence JSON beside the delivered workbook or in the run evidence directory. Record plan ID, plan hash, source fingerprint, output fingerprint, snapshot or rollback locator, validation result, and reviewer state in `tbl_meta_changes` and `tbl_meta_validations` when applicable.

### Workbook-local workflow — portable core

1. Define the workflow and steps in a compact JSON definition.
2. Generate a planned run envelope from the workbook-local definition and non-secret inputs. Do not require connector retrieval or a source manifest.
3. Build or refresh the workbook through native spreadsheet tooling.
4. Validate `_MCP_META`, workflow relationships, workbook structure, and declared deltas.
5. Render-review the workbook and record workflow/run evidence from workbook, input, and output fingerprints.

```bash
python scripts/build_workflow_run.py workflow-definition.json \
  --inputs workflow-inputs.json \
  --output planned-run.json
python scripts/validate_meta_contract.py output.xlsx \
  --output meta-validation.json
```

In workbook-local mode, omit `--source-manifest`. The planned run binds its definition and input fingerprints without inventing connector source IDs or source packets. Completion state still must come from actual execution evidence; the script does not edit workbooks or assert that steps completed.

### Connected-source workflow — optional extension

1. Define the workflow and steps in a compact JSON definition.
2. Generate a planned run envelope before connector execution.
3. Retrieve required connected sources, normalize them, and build a source manifest.
4. Rebuild the planned run with the actual source manifest when the run must bind to that retrieved source snapshot.
5. Build or refresh the workbook through native spreadsheet tooling.
6. Validate `_MCP_META`, workflow relationships, workbook structure, and visual output.

```bash
python scripts/build_workflow_run.py workflow-definition.json \
  --inputs workflow-inputs.json \
  --source-manifest source-manifest.json \
  --output planned-run.json
python scripts/validate_meta_contract.py output.xlsx \
  --output meta-validation.json
```

When a source manifest is supplied, the planned run binds its input fingerprint and `source_snapshot` to the manifest fingerprint and records source IDs plus authority summary. The planned-run script does not call connectors, edit workbooks, or assert that steps completed. Completion state must come from actual execution evidence.

## Generic connected-source normalization — optional extension

Retrieve data with an authorized connector first, then normalize only the workflow-relevant non-secret fields into `source-packet-v1` using a connector-specific adapter supplied outside this portable package. Validate and merge the resulting packets with the bundled generic helpers before workbook mapping. Skip this section entirely for workbook-local workflows.

```bash
python scripts/validate_source_packet.py source-a.json
python scripts/validate_source_packet.py source-b.json
python scripts/merge_source_packets.py source-a.json source-b.json --output source-manifest.json
```

Use [connector-source-contract.md](connector-source-contract.md) for the shared schema and [connector-extension-guide.md](connector-extension-guide.md) when defining a connector-specific adapter. The public skill does not bundle credentials, private endpoints, or system-specific connector normalizers.

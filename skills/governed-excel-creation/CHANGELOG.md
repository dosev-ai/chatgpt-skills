# Changelog

## 1.1.1 - 2026-08-19

- Reject workflow run-step evidence that crosses `Workflow_ID` boundaries.
- Keep populated metadata rows in validation even when the identifier field is blank so malformed rows fail closed instead of being silently skipped.
- Clarify the workbook-format boundary: bundled deterministic helpers operate on OOXML workbooks such as `.xlsx` and `.xlsm`.
- Require feature-preserving controlled conversion for legacy binary `.xls` inputs: `.xlsx` only for established macro-free conversion; macro-bearing or potentially macro-bearing inputs require a macro-enabled OOXML target such as `.xlsm`, with fail-closed handling when preservation cannot be verified.
- Preserve this legacy-conversion safety boundary in the downstream public projection contract.

## 1.1.0 - 2026-08-19

- Added a connector-independent portable core for normal workbook delivery.
- Added workbook-local repeatable workflows that do not require an external orchestration or source system.
- Added a human-facing README and a normalized `_MCP_META` workbook contract.
- Added deterministic workbook inspection, planning, delta, validation, and generic source-packet helpers.
- Clarified that environment-dependent native recalculation and connected-source capabilities are optional and must not be claimed without evidence.

## 1.0.0 - 2026-07-21

- Established the governed workbook lifecycle for creation, repair, reformatting, documentation, validation, render review, rollback, and continuation.
- Added metadata, workflow, formatting, planning, source-packet, and readiness evidence contracts.
- Added deterministic helpers for workbook context, target-locked plans, metadata validation, workbook comparison, workflow-run envelopes, and governed checks.

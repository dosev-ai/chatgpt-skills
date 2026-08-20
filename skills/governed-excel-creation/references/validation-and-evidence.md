# Validation, Delta, Readiness, and Evidence

## Validation sequence

1. Reopen or reparse the saved workbook.
2. Inspect key input, calculation, output, changed, adjacent, and metadata ranges.
3. Scan for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, and `#N/A`.
4. Validate formulas, names, tables, filters, charts, validations, conditional rules, protection, and metadata references.
5. Compare expected versus observed change.
6. Confirm undeclared content remained unchanged for existing-workbook edits.
7. Render README, every materially affected output sheet, optional MAINTENANCE, and `_MCP_META` after structural changes.
8. Run the deterministic metadata validator when available.
9. Repair failures and rerun only affected checks plus regression checks.
10. Export one final workbook.

## Expected-versus-observed delta

Record:

- expected objects and properties changed;
- actual objects and properties changed;
- unexpected additions, removals, or mutations;
- preserved object hashes or focused comparisons where available;
- idempotency result when reapplication should be a no-op;
- rollback test or locator status.

Unexpected delta is blocking until explained and explicitly accepted.


## Documentation consistency

For standard and governed workbooks, verify:

- README is the first visible sheet unless a preserved workbook convention justifies another placement;
- README purpose, owner, version, update date, refresh guidance, limitations, and validation status agree with `_MCP_META`;
- internal navigation links resolve;
- optional MAINTENANCE procedures agree with `tbl_meta_maintenance` and reference valid validation IDs;
- documentation sheets contain no secrets, credentials, or sensitive local paths;
- documentation is readable in render and print review.

Treat documentation inconsistency as a review-readiness failure. Treat a misleading operational instruction that could corrupt data or distribution as a technical blocker.

## Readiness states

Return distinct booleans or clear states:

- `safe_to_open`: package and workbook structure are technically intact;
- `metadata_consistent`: metadata matches workbook objects and logic;
- `ready_for_review`: presentation and business usability checks pass;
- `ready_to_distribute`: acceptance, evidence, and output checks pass;
- `rollback_available`: a usable pre-change snapshot or source copy exists.

Do not collapse these into one generic success result.

## Evidence package

Capture:

- output path and workbook fingerprint;
- source fingerprint and snapshot or rollback locator;
- plan ID and plan hash for material changes;
- sheet, table, name, and chart inventory;
- inspected formulas and ranges;
- formula-error scan;
- metadata-validator JSON result;
- expected-versus-observed delta;
- render review result;
- recalculation engine used or explicit statement that cached values were not refreshed;
- unresolved limitations.

## Verdict

- `PASS`: all applicable gates and readiness requirements pass.
- `CONDITIONAL_PASS`: usable result with a documented non-blocking limitation.
- `FAIL`: formula, structural, preservation, metadata, delta, rollback, or visual defect remains.

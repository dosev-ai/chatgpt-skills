# Metadata-Driven Reformatting Execution

## Resolution sequence

1. Read core metadata and formatting tables before business sheets.
2. Validate exact sheet names, unique IDs, controlled vocabularies, style references, rule references, and target objects.
3. Reject missing references and inheritance cycles.
4. Resolve style inheritance from parent to child.
5. Convert table and named-range targets to concrete workbook objects; never guess missing objects.
6. Sort active regions by `Priority`, then `Format_ID`.
7. Apply base styles before explicit overlays.
8. Honor `Preserve_Unspecified=Yes` by mutating only declared properties.
9. Apply layout after static cell formatting.
10. Apply conditional formatting last.
11. Update change and validation metadata.
12. Inspect changed and adjacent regions, compare with baseline, and render affected outputs.

## Preservation and conflict rules

- Metadata controls only active declared regions; preserve all unlisted regions.
- Higher-priority regions may override lower-priority regions.
- Equal-priority overlapping regions with conflicting values are a validation failure.
- A format-only operation must not replace formulas, values, comments, hyperlinks, names, or validations.
- Do not infer semantic roles from color when metadata exists.
- For undocumented workbooks, mark proposed roles as `Unknown` or `Inferred` until confirmed.
- Treat tables, merged cells, hidden support sheets, named ranges, conditional rules, and print areas as high-risk objects.

## Execution grouping

Use the fewest safe operations:

- same font/fill style on non-contiguous ranges -> multi-range style application;
- same address and full format across sheets -> sheet-list formatting;
- governed reference format -> format-only copy;
- new values plus one consistent format -> write-plus-format;
- different complete formats by region -> one native in-memory mutation session and one save;
- compatible width and height changes -> grouped layout operations.

When an external native-Excel automation layer is used, snapshot first and sequence only supported bounded calls. Do not claim cross-call atomicity.

## Preview example

```text
Will change:
- Summary!A1:H2 -> title style
- Summary!A5:H5 -> section-header style
- Inputs!B4:B18 -> input style and number format
- Summary columns A:H -> declared widths

Will preserve:
- all values and formulas
- table identities and ranges
- named ranges and chart source data
- hidden-sheet state
```

## Completion evidence

Capture:

- style, property, region, and layout counts;
- resolved plan and grouped operations;
- pre-change baseline or snapshot;
- formula and value preservation result;
- expected-versus-observed delta;
- render evidence for affected sheets;
- updated validation and change rows.

# Formatting Metadata Tables

## Activation rule

Use the formatting extension only for repeatable metadata-driven reformatting. If any core formatting table exists, require all three:

- `tbl_meta_styles`;
- `tbl_meta_style_properties`;
- `tbl_meta_format_regions`.

`tbl_meta_layout` is optional.

## `tbl_meta_styles`

| Column | Meaning |
|---|---|
| Style_ID | Stable identifier such as `STY-001` |
| Style_Name | Human-readable name |
| Semantic_Role | title, header, input, formula, output, total, warning, note, or another controlled role |
| Description | Intended visual meaning |
| Inherits_From | Parent Style_ID or blank |
| Active | Yes/No |

## `tbl_meta_style_properties`

Store one property per row.

| Column | Meaning |
|---|---|
| Style_Property_ID | Stable identifier |
| Style_ID | Referenced style |
| Property | Controlled property name |
| Value | Property value |
| Value_Type | Text, Number, Boolean, or FormatCode |
| Apply_Mode | set, preserve_if_blank, or clear |

Controlled properties:

- font: `font_name`, `font_size`, `bold`, `italic`, `underline`, `font_color`;
- fill: `fill_color`;
- number: `number_format`;
- alignment: `horizontal`, `vertical`, `wrap_text`, `shrink_to_fit`, `text_rotation`, `indent`;
- border: `border_style`, `border_color`;
- table: `table_style`.

## `tbl_meta_format_regions`

Use one row per target. Reuse a Style_ID across several rows instead of storing a list of ranges in one cell.

| Column | Meaning |
|---|---|
| Format_ID | Stable identifier |
| Sheet_Name | Exact worksheet name |
| Target_Type | range, table, named_range, row, or column |
| Target_Ref | Exact A1 reference or object name |
| Style_ID | Referenced semantic style |
| Conditional_Rule_ID | Optional Rule_ID from `tbl_meta_rules` |
| Priority | Integer overlay order; lower applies first |
| Preserve_Unspecified | Yes/No; normally Yes |
| Active | Yes/No |
| Notes | Bounded implementation note |

## `tbl_meta_layout`

| Column | Meaning |
|---|---|
| Layout_ID | Stable identifier |
| Sheet_Name | Exact worksheet name |
| Layout_Type | column_width, row_height, autofit_columns, freeze_panes, gridlines, zoom, or print_area |
| Target_Ref | Target column, row, cell, or range |
| Value | Declared value |
| Priority | Integer application order |
| Active | Yes/No |
| Notes | Bounded implementation note |

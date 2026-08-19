# Connector Extension Guide

## Purpose

Add future connectors without expanding `SKILL.md` into a monolith or inventing a new source contract for every system.

## Required extension pattern

For each connector:

1. Define its authority domain and default authority role.
2. Document the connector retrieval sequence in one direct reference file.
3. Define the minimum exported JSON shape.
4. Add a deterministic `normalize_<connector>.py` adapter.
5. Emit `source-packet-v1` from [connector-source-contract.md](connector-source-contract.md).
6. Redact credentials and unnecessary sensitive fields.
7. Add positive and negative fixtures outside the packaged skill or as small synthetic examples.
8. Test packet validation, fingerprint stability, empty-result behavior, malformed input, and authority boundaries.
9. Link the connector reference directly from `SKILL.md` only when the connector becomes supported.
10. Keep connector calls in the tool layer and artifact mutation in the specialist skill.

## Normalizer responsibilities

A connector adapter should:

- unwrap the connector's response envelope;
- select only workflow-relevant fields;
- normalize identifiers, timestamps, and record arrays;
- declare authority explicitly;
- retain source references and retrieval operations;
- record row counts, warnings, and redactions;
- produce a deterministic content fingerprint;
- fail closed on missing required identity or invalid governed state.

It should not:

- call the connector or use network libraries;
- store credentials;
- mutate the source system;
- create or edit Excel files;
- decide business acceptance;
- upgrade source authority based on content quality or confidence scores.

## Suggested connector references

Future candidates may include:

- ERP or finance systems for posted transactions;
- procurement and spend platforms for supplier/category records;
- Gmail or Outlook for selected message metadata and attachments;
- Google Drive, Notion, or SharePoint for controlled source documents;
- GitHub for repository, issue, pull-request, and release evidence;
- Power BI or analytical systems for governed dataset exports.

Each connector keeps its own retrieval and field-mapping reference while sharing the packet, manifest, validation, and evidence contracts.

## Promotion criterion

Promote a connector adapter from experimental to supported only after:

- at least one real workflow run;
- positive and negative fixture tests;
- authority and sensitivity review;
- stable source identifiers and retrieval filters;
- documented degraded or unavailable behavior;
- workbook reconciliation evidence.

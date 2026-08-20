# Connector Source Packet Contract

## Purpose

Use a common, portable JSON contract between connector retrieval and workbook generation. Connector tools retrieve data; deterministic adapter scripts normalize those responses; workbook planning and workflow execution consume the normalized packet or merged manifest.

The skill scripts do not authenticate, call network services, or retain credentials.

## Boundary

```text
Connector tool call
  -> exported JSON response
  -> connector-specific normalizer
  -> source-packet-v1
  -> optional source-manifest-v1
  -> workflow input mapping
  -> workbook generation or refresh
```

This is an ingestion and provenance boundary, not a second connector runtime.

## `source-packet-v1`

Required fields:

| Field | Meaning |
|---|---|
| `packet_version` | Exact value `source-packet-v1`. |
| `source_id` | Stable unique identifier for the source binding. |
| `connector` | Connector or source family. |
| `authority_role` | `Authoritative`, `Contextual`, `Derived`, `Manual`, or `Unknown`. |
| `authority_domain` | Plain-language boundary of what the source may govern. |
| `retrieved_at` | Retrieval timestamp. |
| `scope` | Project, query, tag, date, or other source filters. |
| `records` | Typed arrays such as projects, facts, actions, dependencies, or documents. |
| `provenance` | Operations, counts, source references, warnings, and redaction evidence. |
| `content_fingerprint` | SHA-256 over the packet content excluding the fingerprint field. |

Recommended record families:

- `projects`
- `facts`
- `actions`
- `dependencies`
- `documents`

A future connector may add another record family, but every record family must be an array and must remain connector-neutral enough for declared workflow transforms.

## `source-manifest-v1`

A manifest merges two or more validated packets and contains:

- `manifest_version`
- `created_at`
- `sources`
- `authority_summary`
- `manifest_fingerprint`

Reject duplicate `source_id` values. Preserve each packet's authority role; merging must never collapse or upgrade authority.

## Authority rules

- A governed operational system may be `Authoritative` only for the domain it explicitly owns.
- A document or knowledge source is normally `Contextual` unless its authority is independently established.
- Contextual content may enrich labels, explanations, or narratives but must not override authoritative records.
- Inferred or transformed values must be labeled `Derived` and retain source references.
- Use `Unknown` when authority is unverified.

## Security and privacy

- Do not store access tokens, API keys, passwords, cookies, authorization headers, or private keys.
- Normalizers redact values under secret-like keys and record redacted paths in provenance.
- Include only fields required for the workflow.
- Default document-source packets to snippets and document references. Include full document content only when explicitly required and permitted.
- Do not bundle production payload fixtures inside the skill package.

## Fingerprints and freshness

Use packet and manifest fingerprints to bind workflow inputs to a specific retrieved source snapshot. A refreshed connector result creates a new fingerprint and may invalidate an approved workbook plan.

The fingerprint proves packet content identity. It does not prove that the connector response was complete, current, or authoritative outside the declared domain. Record retrieval filters, row counts, warnings, and timestamps separately.

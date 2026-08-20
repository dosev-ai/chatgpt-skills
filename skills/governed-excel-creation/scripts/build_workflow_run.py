#!/usr/bin/env python3
"""Build a deterministic planned workflow-run envelope from JSON inputs.

The script does not call connectors or edit workbooks. It validates a compact
workflow definition, hashes the definition and non-secret inputs, and emits a
planned run with one NOT_STARTED step record per declared step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _source_packets import redact_secrets, validate_manifest


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_definition(definition: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    workflow_id = str(definition.get("workflow_id", "")).strip()
    workflow_version = str(definition.get("workflow_version", "")).strip()
    steps = definition.get("steps")
    if not workflow_id:
        errors.append("workflow_id is required")
    if not workflow_version:
        errors.append("workflow_version is required")
    if not isinstance(steps, list) or not steps:
        errors.append("steps must be a non-empty array")
        return errors

    seen_ids: set[str] = set()
    seen_sequences: set[int] = set()
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"steps[{index}] must be an object")
            continue
        step_id = str(step.get("step_id", "")).strip()
        if not step_id:
            errors.append(f"steps[{index}].step_id is required")
        elif step_id in seen_ids:
            errors.append(f"duplicate step_id {step_id!r}")
        else:
            seen_ids.add(step_id)
        sequence = step.get("sequence")
        if not isinstance(sequence, int) or sequence <= 0:
            errors.append(f"steps[{index}].sequence must be a positive integer")
        elif sequence in seen_sequences:
            errors.append(f"duplicate step sequence {sequence}")
        else:
            seen_sequences.add(sequence)
    return errors


def declared_sensitive_input_keys(definition: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    declarations = definition.get("inputs", [])
    if not isinstance(declarations, list):
        return keys
    for declaration in declarations:
        if not isinstance(declaration, dict):
            continue
        sensitive = declaration.get("sensitive", declaration.get("Sensitive", False))
        is_sensitive = sensitive is True or (
            isinstance(sensitive, str) and sensitive.strip().lower() in {"yes", "true", "1"}
        )
        if not is_sensitive:
            continue
        for field in ("input_name", "name", "input_id", "Input_Name", "Input_ID"):
            value = declaration.get(field)
            if isinstance(value, str) and value.strip():
                keys.add(value.strip())
    return keys


def redact_explicit_input_keys(value: Any, sensitive_keys: set[str], path: str = "$.inputs") -> tuple[Any, list[str]]:
    redactions: list[str] = []

    def visit(item: Any, item_path: str) -> Any:
        if isinstance(item, dict):
            result: dict[str, Any] = {}
            for key, child in item.items():
                key_text = str(key)
                child_path = f"{item_path}.{key_text}"
                if key_text in sensitive_keys:
                    result[key_text] = "<redacted>"
                    redactions.append(child_path)
                else:
                    result[key_text] = visit(child, child_path)
            return result
        if isinstance(item, list):
            return [visit(child, f"{item_path}[{index}]") for index, child in enumerate(item)]
        return item

    return visit(value, path), redactions


def normalized_non_secret_inputs(
    inputs: dict[str, Any],
    sensitive_keys: set[str],
) -> tuple[dict[str, Any], list[str]]:
    auto_redacted, auto_paths = redact_secrets(inputs, "$.inputs")
    explicit_redacted, explicit_paths = redact_explicit_input_keys(auto_redacted, sensitive_keys)
    return explicit_redacted, sorted(set(auto_paths + explicit_paths))


def build_run(
    definition: dict[str, Any],
    inputs: dict[str, Any],
    started_at: str,
    executed_by: str,
    source_manifest: dict[str, Any] | None = None,
    sensitive_input_keys: set[str] | None = None,
) -> dict[str, Any]:
    definition_hash = digest(definition)
    manifest_fingerprint = source_manifest.get("manifest_fingerprint", "") if source_manifest else ""
    sanitized_inputs, input_redactions = normalized_non_secret_inputs(inputs, sensitive_input_keys or set())
    input_fingerprint = (
        digest({"inputs": sanitized_inputs, "source_manifest_fingerprint": manifest_fingerprint})
        if source_manifest else digest(sanitized_inputs)
    )
    run_seed = {
        "workflow_id": definition["workflow_id"],
        "workflow_version": definition["workflow_version"],
        "definition_hash": definition_hash,
        "input_fingerprint": input_fingerprint,
        "started_at": started_at,
    }
    run_id = f"run-{digest(run_seed)[:20]}"
    steps = sorted(definition["steps"], key=lambda item: item["sequence"])
    return {
        "run_id": run_id,
        "workflow_id": definition["workflow_id"],
        "workflow_version": definition["workflow_version"],
        "status": "PLANNED",
        "started_at": started_at,
        "completed_at": "",
        "executed_by": executed_by,
        "definition_hash": definition_hash,
        "input_fingerprint": input_fingerprint,
        "input_redaction_count": len(input_redactions),
        "source_snapshot": manifest_fingerprint,
        "source_manifest_version": source_manifest.get("manifest_version", "") if source_manifest else "",
        "source_ids": [item.get("source_id") for item in source_manifest.get("sources", [])] if source_manifest else [],
        "authority_summary": source_manifest.get("authority_summary", {}) if source_manifest else {},
        "output_fingerprint": "",
        "validation_status": "NOT_RUN",
        "evidence_ref": "",
        "steps": [
            {
                "run_step_id": f"{run_id}-{step['step_id']}",
                "step_id": step["step_id"],
                "sequence": step["sequence"],
                "required": bool(step.get("required", True)),
                "checkpoint_type": step.get("checkpoint_type", "None"),
                "checked": False,
                "status": "NOT_STARTED",
                "started_at": "",
                "completed_at": "",
                "result_summary": "",
                "evidence_ref": "",
                "error_or_warning": "",
            }
            for step in steps
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("definition", type=Path)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument(
        "--sensitive-input-key",
        action="append",
        default=[],
        help="Input key whose value must be redacted before fingerprinting; repeat as needed",
    )
    parser.add_argument("--source-manifest", type=Path, help="Validated source-manifest-v1 from connector packet adapters")
    parser.add_argument("--started-at", help="ISO timestamp; defaults to current UTC time")
    parser.add_argument("--executed-by", default="ChatGPT")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        definition = load_json(args.definition)
        inputs = load_json(args.inputs) if args.inputs else {}
        source_manifest = load_json(args.source_manifest) if args.source_manifest else None
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2
    if not isinstance(definition, dict) or not isinstance(inputs, dict):
        print(json.dumps({"status": "ERROR", "error": "definition and inputs must be JSON objects"}, indent=2))
        return 2
    if source_manifest is not None and not isinstance(source_manifest, dict):
        print(json.dumps({"status": "ERROR", "error": "source manifest must be a JSON object"}, indent=2))
        return 2

    errors = validate_definition(definition)
    if source_manifest is not None:
        errors.extend(f"source manifest: {error}" for error in validate_manifest(source_manifest))
    if errors:
        payload = {"status": "FAIL", "errors": errors}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1

    started_at = args.started_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    sensitive_keys = declared_sensitive_input_keys(definition)
    sensitive_keys.update(key.strip() for key in args.sensitive_input_key if key.strip())
    run = build_run(
        definition, inputs, started_at, args.executed_by, source_manifest, sensitive_keys
    )
    payload = {"status": "PASS", "run": run}
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

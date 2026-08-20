#!/usr/bin/env python3
"""Validate a source-packet-v1 or source-manifest-v1 JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _source_packets import MANIFEST_VERSION, PACKET_VERSION, validate_manifest, validate_packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        value = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2

    if isinstance(value, dict) and value.get("packet_version") == PACKET_VERSION:
        kind = "packet"
        errors = validate_packet(value)
    elif isinstance(value, dict) and value.get("manifest_version") == MANIFEST_VERSION:
        kind = "manifest"
        errors = validate_manifest(value)
    else:
        kind = "unknown"
        errors = [f"expected {PACKET_VERSION!r} or {MANIFEST_VERSION!r}"]
    result = {"status": "PASS" if not errors else "FAIL", "kind": kind, "errors": errors}
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

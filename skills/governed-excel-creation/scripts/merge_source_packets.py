#!/usr/bin/env python3
"""Merge validated connector source packets into source-manifest-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _source_packets import finalize_manifest, validate_packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packets", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    sources = []
    errors: list[str] = []
    seen: set[str] = set()
    for path in args.packets:
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        packet_errors = validate_packet(packet)
        errors.extend(f"{path}: {error}" for error in packet_errors)
        source_id = packet.get("source_id") if isinstance(packet, dict) else None
        if isinstance(source_id, str):
            if source_id in seen:
                errors.append(f"duplicate source_id {source_id!r}")
            seen.add(source_id)
        sources.append(packet)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    manifest = finalize_manifest(sources)
    text = json.dumps({"status": "PASS", "manifest": manifest}, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

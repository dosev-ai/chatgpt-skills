#!/usr/bin/env python3
"""Extract a deterministic governed context summary from an XLSX workbook."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET

from _ooxml import workbook_context


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    if not args.workbook.is_file():
        print(json.dumps({"status": "ERROR", "error": "Workbook not found"}, indent=2))
        return 2

    try:
        context = workbook_context(args.workbook)
    except (zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as exc:
        payload = {"status": "ERROR", "workbook": str(args.workbook), "error": str(exc)}
        code = 2
    else:
        payload = {"status": "PASS", **context}
        code = 0

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

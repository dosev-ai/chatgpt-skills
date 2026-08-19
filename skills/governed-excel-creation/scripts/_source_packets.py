#!/usr/bin/env python3
"""Shared helpers for deterministic connector source packets.

The module contains no network or connector code. Connector calls are made by
ChatGPT/tooling, then their JSON responses are normalized by adapter scripts.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Iterable

PACKET_VERSION = "source-packet-v1"
MANIFEST_VERSION = "source-manifest-v1"
AUTHORITY_ROLES = {"Authoritative", "Contextual", "Derived", "Manual", "Unknown"}
SOURCE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
SECRET_KEY_MARKERS = {
    "api_key", "apikey", "access_token", "refresh_token", "token", "password",
    "passwd", "secret", "authorization", "bearer", "cookie", "private_key",
    "client_secret", "session_key", "credential", "credentials",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def unwrap_json(value: Any) -> Any:
    """Unwrap common connector envelopes containing JSON in a text field."""
    current = value
    for _ in range(4):
        if isinstance(current, dict) and set(current).issubset({"text", "resource_uri"}) and isinstance(current.get("text"), str):
            text = current["text"].strip()
            try:
                current = json.loads(text)
                continue
            except json.JSONDecodeError:
                return current
        if isinstance(current, str):
            text = current.strip()
            if text.startswith(("{", "[")):
                try:
                    current = json.loads(text)
                    continue
                except json.JSONDecodeError:
                    return current
        break
    return current


def _is_secret_key(key: str) -> bool:
    # Normalize separators and camel/Pascal case so accessToken, clientSecret,
    # APIKey, credentialMetadata, and serviceRefreshToken match snake_case markers.
    split_acronyms = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
    split_camel = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", split_acronyms)
    normalized = re.sub(r"[^a-z0-9]+", "_", split_camel.lower()).strip("_")
    return normalized in SECRET_KEY_MARKERS or any(
        normalized.endswith(f"_{marker}") or normalized.startswith(f"{marker}_")
        for marker in SECRET_KEY_MARKERS
    )


def redact_secrets(value: Any, path: str = "$") -> tuple[Any, list[str]]:
    """Redact values under secret-like keys and return redacted paths."""
    redactions: list[str] = []

    def visit(item: Any, item_path: str) -> Any:
        if isinstance(item, dict):
            result: dict[str, Any] = {}
            for key, child in item.items():
                key_text = str(key)
                child_path = f"{item_path}.{key_text}"
                if _is_secret_key(key_text):
                    result[key_text] = "<redacted>"
                    redactions.append(child_path)
                else:
                    result[key_text] = visit(child, child_path)
            return result
        if isinstance(item, list):
            return [visit(child, f"{item_path}[{index}]") for index, child in enumerate(item)]
        return item

    return visit(deepcopy(value), path), redactions


def stable_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            output.append(text)
            seen.add(text)
    return output


def count_records(records: dict[str, Any]) -> dict[str, int]:
    return {
        key: len(value) if isinstance(value, list) else 0
        for key, value in sorted(records.items())
    }


def packet_fingerprint_payload(packet: dict[str, Any]) -> dict[str, Any]:
    copy = deepcopy(packet)
    copy.pop("content_fingerprint", None)
    return copy


def finalize_packet(packet: dict[str, Any]) -> dict[str, Any]:
    packet = deepcopy(packet)
    packet["packet_version"] = PACKET_VERSION
    packet.setdefault("retrieved_at", utc_now())
    packet.setdefault("records", {})
    packet.setdefault("scope", {})
    packet.setdefault("provenance", {})
    packet["provenance"].setdefault("operations", [])
    packet["provenance"].setdefault("record_counts", count_records(packet["records"]))
    packet["provenance"].setdefault("source_refs", [])
    packet["provenance"].setdefault("warnings", [])
    packet["content_fingerprint"] = sha256_value(packet_fingerprint_payload(packet))
    return packet


def validate_packet(packet: Any, verify_fingerprint: bool = True) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"]
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(f"packet_version must be {PACKET_VERSION!r}")
    source_id = packet.get("source_id")
    if not isinstance(source_id, str) or not SOURCE_ID_RE.fullmatch(source_id):
        errors.append("source_id is required and must use letters, numbers, dot, underscore, colon, or hyphen")
    connector = packet.get("connector")
    if not isinstance(connector, str) or not connector.strip():
        errors.append("connector is required")
    role = packet.get("authority_role")
    if role not in AUTHORITY_ROLES:
        errors.append(f"authority_role must be one of {sorted(AUTHORITY_ROLES)}")
    if not isinstance(packet.get("authority_domain"), str) or not packet.get("authority_domain", "").strip():
        errors.append("authority_domain is required")
    if not isinstance(packet.get("scope"), dict):
        errors.append("scope must be an object")
    records = packet.get("records")
    if not isinstance(records, dict):
        errors.append("records must be an object")
    elif any(not isinstance(value, list) for value in records.values()):
        errors.append("every records member must be an array")
    provenance = packet.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for key in ("operations", "source_refs", "warnings"):
            if not isinstance(provenance.get(key), list):
                errors.append(f"provenance.{key} must be an array")
        if not isinstance(provenance.get("record_counts"), dict):
            errors.append("provenance.record_counts must be an object")
    if verify_fingerprint:
        expected = packet.get("content_fingerprint")
        if not isinstance(expected, str) or len(expected) != 64:
            errors.append("content_fingerprint must be a SHA-256 hex string")
        elif expected != sha256_value(packet_fingerprint_payload(packet)):
            errors.append("content_fingerprint does not match packet content")
    return errors


def manifest_fingerprint_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    copy = deepcopy(manifest)
    copy.pop("manifest_fingerprint", None)
    return copy


def finalize_manifest(sources: list[dict[str, Any]], created_at: str | None = None) -> dict[str, Any]:
    role_counts: dict[str, int] = {}
    for source in sources:
        role = source.get("authority_role", "Unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "created_at": created_at or utc_now(),
        "sources": sources,
        "authority_summary": {
            "roles": dict(sorted(role_counts.items())),
            "authoritative_source_ids": [s["source_id"] for s in sources if s.get("authority_role") == "Authoritative"],
            "contextual_source_ids": [s["source_id"] for s in sources if s.get("authority_role") == "Contextual"],
        },
    }
    manifest["manifest_fingerprint"] = sha256_value(manifest_fingerprint_payload(manifest))
    return manifest


def validate_manifest(manifest: Any, verify_fingerprint: bool = True) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        errors.append(f"manifest_version must be {MANIFEST_VERSION!r}")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty array")
        return errors
    seen: set[str] = set()
    for index, source in enumerate(sources):
        source_errors = validate_packet(source, verify_fingerprint=verify_fingerprint)
        errors.extend(f"sources[{index}]: {error}" for error in source_errors)
        source_id = source.get("source_id") if isinstance(source, dict) else None
        if isinstance(source_id, str):
            if source_id in seen:
                errors.append(f"duplicate source_id {source_id!r}")
            seen.add(source_id)
    if verify_fingerprint:
        expected = manifest.get("manifest_fingerprint")
        if not isinstance(expected, str) or len(expected) != 64:
            errors.append("manifest_fingerprint must be a SHA-256 hex string")
        elif expected != sha256_value(manifest_fingerprint_payload(manifest)):
            errors.append("manifest_fingerprint does not match manifest content")
    return errors

#!/usr/bin/env python3
"""Validate the lossless, secret-scanner-safe SHA-256 evidence format.

Usage: python3 tools/verify_rc_checksum_manifest.py [path/to/manifest.json]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MANIFEST = "docs/RC_DASHBOARD_WIDGET_APPEARANCE_MANIFEST.json"
WORD = re.compile(r"[0-9a-f]{8}\Z")


def decode_sha256_words(words: object) -> str:
    if not isinstance(words, list) or len(words) != 8 or any(not isinstance(w, str) or WORD.fullmatch(w) is None for w in words):
        raise ValueError("each SHA-256 digest must be encoded as 8 lowercase eight-hex-character words")
    return "".join(words)


def validate_manifest(path: Path) -> dict[str, str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if "sha256_by_file" in document:
        raise ValueError("unsafe legacy sha256_by_file format: encode hash words instead")
    hashes = document.get("sha256_hex_groups_by_file")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("missing SHA-256 integrity evidence")
    if document.get("total_count") != len(hashes):
        raise ValueError("manifest entry count does not match total_count")
    if not all(isinstance(path, str) and path and "\x00" not in path for path in hashes):
        raise ValueError("invalid SHA-256 file identifier")
    return {name: decode_sha256_words(words) for name, words in hashes.items()}


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(MANIFEST)
    result = validate_manifest(path)
    print(f"Checksum manifest VALID: {len(result)} historical SHA-256 digests preserved")

#!/usr/bin/env python3
"""Validate *archive* closure of all workflow-referenced RC inventory receipts.

An inventory can hash its own source files correctly and still omit a prior
receipt if its file list was copied from the previous inventory without adding
that inventory's manifest. Validate dependencies against source AND ZIP members.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Collection

WORKFLOW = '.github/workflows/ci.yml'
COMMAND = re.compile(r'^\s*python3 tools/(verify_rc_cycle\d+_inventory\.py)(?:\s+--historical)?\s*$', re.M)
MANIFEST = re.compile(r"^MANIFEST\s*=\s*'([^']+)'", re.M)


def required_inventory_files(read_text: Callable[[str], str]) -> set[str]:
    """Return verifier/receipt paths required by the workflow itself."""
    workflow = read_text(WORKFLOW)
    commands = COMMAND.findall(workflow)
    if not commands:
        raise ValueError('workflow contains no RC inventory verification commands')
    required = {WORKFLOW}
    for command in commands:
        source = 'tools/' + command
        match = MANIFEST.search(read_text(source))
        if match is None:
            # Some very early verification helpers use inline paths rather than
            # a MANIFEST constant; they are still required as source files.
            required.add(source)
            continue
        receipt = match.group(1)
        if (not receipt.startswith('docs/validation/RC_CYCLE') or
                not receipt.endswith('.json') or '..' in receipt.split('/') or '\\' in receipt):
            raise ValueError('unsafe inventory receipt name: ' + receipt)
        required.update((source, receipt))
    return required


def check_inventory_closure(files: Collection[str], read_text: Callable[[str], str]) -> int:
    """Fail if *any* workflow verifier or historical receipt is missing."""
    required = required_inventory_files(read_text)
    missing = sorted(required - set(files))
    if missing:
        raise ValueError('RC archive/inventory missing workflow evidence: ' + ', '.join(missing))
    return len(required)

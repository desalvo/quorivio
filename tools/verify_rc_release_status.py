#!/usr/bin/env python3
"""Check active release headers against the current CI inventory before expensive jobs.

Historical sections following the first divider remain unchanged. This script
must also be executed against the freshly extracted final release ZIP.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# The same release guard is imported as tools.verify_rc_release_status by
# `python -m unittest`, but executed as tools/verify_rc_release_status.py by
# the release preflight. Make sibling imports deterministic in both cases.
_TOOLS = str(Path(__file__).resolve().parent)
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
from verify_rc_current_inventory import current_verifier_module
from rc_gate_audit import audit

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'DEVELOPMENT_STATUS.md',
    'DEVELOPMENT_STATUS.it.md',
    'COMPLETION_HANDOFF.md',
    'COMPLETION_HANDOFF.it.md',
)
FLAGS = ('rc_strict=false', 'publish_image=false', 'publish_latest=false')


def verify_headers(root: Path = ROOT, cycle: int | None = None) -> int:
    if cycle is None:
        name = current_verifier_module().__name__
        match = re.fullmatch(r'verify_rc_cycle([0-9]+)_inventory', name)
        if match is None:
            raise ValueError('unrecognized current inventory: ' + name)
        cycle = int(match.group(1))
    expected = f'RC{cycle}'
    score = audit()['score']
    # Percentage is derived from the gate ledger, not an unverified status note.
    score_en = f'{score:.2f}%'
    score_it = score_en.replace('.', ',')
    for file in FILES:
        path = root / 'docs' / file
        text = path.read_text(encoding='utf8')
        current = text.split('\n---\n', 1)[0]
        heading = current.splitlines()[0]
        # The first heading, not an old archived note or footer, must identify
        # the active release; do not accept 'RC100' as a substring of 'RC1000'.
        if re.search(rf'(?<![A-Za-z0-9]){re.escape(expected)}(?![0-9])', heading) is None:
            raise ValueError(f'{file}: active heading {heading!r} does not identify {expected}')
        if not all(flag in current for flag in FLAGS):
            raise ValueError(f'{file}: missing one or more explicit release flags')
        score_label = score_it if file.endswith('.it.md') else score_en
        if re.search(rf'(?<![0-9]){re.escape(score_label)}(?![0-9])', current) is None:
            raise ValueError(f'{file}: missing ledger-derived localized completion score {score_label}')
    return len(FILES)


if __name__ == '__main__':
    count = verify_headers()
    print(f'PASS active release metadata: {count} files match the current inventory')

#!/usr/bin/env python3
"""Check active release headers against the current CI inventory before expensive jobs.

Historical sections following the first divider remain unchanged. This script
must also be executed against the freshly extracted final release ZIP.
"""
from __future__ import annotations

import re
from pathlib import Path
from verify_rc_current_inventory import current_verifier_module

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
    return len(FILES)


if __name__ == '__main__':
    count = verify_headers()
    print(f'PASS active release metadata: {count} files match the current inventory')

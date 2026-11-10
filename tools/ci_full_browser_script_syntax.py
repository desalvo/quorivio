#!/usr/bin/env python3
"""Fail early if an opt-in full-CI Chromium script is syntactically invalid.

A normal PR intentionally skips full browser acceptance. Validate its *entire*
script list before npm to prevent a full campaign from being blocked by broken
legacy source that the standard job never imports.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/'.github/workflows/ci.yml'
START='      - name: Chromium editor UI acceptance (opt-in)'
END='      - name: Upload Chromium failure diagnostics'

def browser_scripts() -> list[Path]:
    text=WORKFLOW.read_text(encoding='utf8')
    if text.count(START)!=1 or text.count(END)!=1:
        raise ValueError('Full browser stage missing or ambiguous')
    block=text.split(START,1)[1].split(END,1)[0]
    paths=sorted(set(re.findall(r'\bpython3\s+(tools/[A-Za-z0-9_./-]+\.py)\b',block)))
    if len(paths)<40:
        raise ValueError(f'Full browser script inventory unexpectedly short: {len(paths)}')
    files=[ROOT/path for path in paths]
    if any(not path.is_file() for path in files):
        raise ValueError('Missing full-browser source: '+', '.join(str(p) for p in files if not p.is_file()))
    return files

def main() -> None:
    failures=[]
    for path in browser_scripts():
        try:
            compile(path.read_bytes(),str(path),'exec')
        except SyntaxError as error:
            failures.append(f'{path.relative_to(ROOT)}:{error.lineno}: {error.msg}')
    if failures:
        raise SystemExit('Invalid full browser script syntax:\n'+'\n'.join(failures))
    print(f'PASS syntax for {len(browser_scripts())} full-browser Python scripts')

if __name__=='__main__':
    main()

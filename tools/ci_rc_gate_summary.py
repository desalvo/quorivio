#!/usr/bin/env python3
"""Publish an evidence-based, non-sensitive RC progress report to GitHub Step Summary.

The report is diagnostic; green CI does not magically accept RC gates.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path


def render(report: dict) -> str:
    score=report['score']
    if not isinstance(score,(int,float)) or isinstance(score,bool) or not 0 <= score <= 100:
        raise ValueError('invalid RC score')
    pending=report['unaccepted_gates']
    if not isinstance(pending,list):
        raise ValueError('invalid pending RC gates')
    rows=['## Quorivio Release Candidate readiness','',
          f'**Gate-weighted progress: {score:.2f}%** — '
          f'**{report["accepted_gates"]}/{report["gate_count"]} gates accepted**','',
          '**RC READY**' if report['release_candidate_ready'] else '**NOT RC READY**',
          '', '> A passing quality gate is not an independent user, device, legal or operational acceptance.', '',
          '| Gate | Status | Remaining verification |', '|---|---|---|']
    for entry in pending:
        fields=[str(entry.get(k,'')) for k in ('id','status','remaining')]
        clean=[f.replace('|','\\|').replace('\r',' ').replace('\n',' ')[:500] for f in fields]
        rows.append('| '+' | '.join(clean)+' |')
    if not pending:rows.append('| All gates | accepted | Independent evidence required in matrix |')
    if report['missing_required_files']:
        rows+=['','**Missing required files:** '+', '.join(str(x) for x in report['missing_required_files'])]
    return '\n'.join(rows)+'\n'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('report',type=Path)
    parser.add_argument('--output',type=Path,default=None)
    args=parser.parse_args()
    result=render(json.loads(args.report.read_text(encoding='utf-8')))
    output=args.output or (Path(os.environ['GITHUB_STEP_SUMMARY']) if os.environ.get('GITHUB_STEP_SUMMARY') else None)
    if not output:
        print(result);return
    with output.open('a',encoding='utf-8') as handle:handle.write(result)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Offline, operator-approved removal of an orphaned conversion reservation.

Never run while conversion workers may still be active on the shared volume.
"""
import argparse
import json
import os
import pathlib
import re
import sys

JOB_ID = re.compile(r'^[0-9a-f]{32}$')


def inspect_and_recover(root: pathlib.Path, job: str, *, confirm: bool = False) -> dict:
    if not JOB_ID.fullmatch(job):
        raise ValueError('invalid job ID')
    root = root.resolve(strict=True)
    work = root / job
    if work.is_symlink() or not work.is_dir():
        raise ValueError('missing or unsafe job workspace')
    lock = work / '.conversion-lock'
    if lock.is_symlink() or not lock.is_dir():
        raise ValueError('missing or unsafe conversion lock')
    if list(lock.iterdir()):
        raise ValueError('nonempty lock: manual inspection required')
    if (work / 'pages').exists() or (work / 'pages').is_symlink():
        raise ValueError('job output exists: manual review required before recovery')
    sources = [p for p in (work / 'source.pdf', work / 'source.pptx') if p.is_file() and not p.is_symlink()]
    if len(sources) != 1:
        raise ValueError('expected exactly one valid source')
    result = {'job': job, 'source': sources[0].name, 'lock': str(lock), 'recovered': False}
    if confirm:
        # The operator must stop all workers sharing this directory first.
        # A pre-existing empty lock can then be removed, never automatically.
        lock.rmdir()
        result['recovered'] = True
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', help='32-character hexadecimal job ID')
    parser.add_argument('--root', default=os.environ.get('QUORIVIO_CONVERSION_DIR', '/conversions'))
    parser.add_argument('--recover', action='store_true', help='remove lock only after all workers are stopped')
    parser.add_argument('--workers-stopped', action='store_true', help='operator confirms all shared-volume workers are stopped')
    args = parser.parse_args(argv)
    if args.recover and not args.workers_stopped:
        parser.error('--recover requires --workers-stopped')
    try:
        print(json.dumps(inspect_and_recover(pathlib.Path(args.root), args.job, confirm=args.recover), sort_keys=True))
    except (ValueError, OSError) as exc:
        print(f'recovery refused: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

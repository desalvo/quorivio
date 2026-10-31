"""Stable source-inventory API used by CI regression tests across RC cycles.

Resolve the latest *nonhistorical* inventory command from the checked-in CI
workflow instead of requiring edits to dozens of historic test files at
release time. The workflow reference guard performs independent safety checks.
"""
from __future__ import annotations

import importlib

from ci_inventory_reference_guard import COMMAND, ROOT, WORKFLOW, verify_references


def current_verifier_module():
    # Fail closed if the workflow references a dropped or damaged manifest.
    verify_references(enforce_git=False)
    commands = COMMAND.findall((ROOT / WORKFLOW).read_text(encoding='utf-8'))
    nonhistorical = [name for name, historical in commands if not historical]
    if not nonhistorical:
        raise ValueError('no current inventory verification command')
    return importlib.import_module(nonhistorical[-1][:-3])


def load_inventory(*args, **kwargs):
    return current_verifier_module().load_inventory(*args, **kwargs)


def verify_source(*args, **kwargs):
    return current_verifier_module().verify_source(*args, **kwargs)

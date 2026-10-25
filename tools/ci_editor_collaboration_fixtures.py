"""Pure, isolated fixtures for real-PostgreSQL editor concurrency acceptance.

A remote collaborator must patch the *latest persisted design*, not recreate the
original fixture: recreating it silently edits coordinates and invalidates the
"independent fields merge" scenario.
"""
from copy import deepcopy


def label_only_remote_patch(activity: dict, widget_id: str, label: str) -> dict:
    """Build a CAS payload that changes exactly one widget label.

    Preserve every other field, widget, geometry and result design from the
    current server snapshot. Never mutate the caller's activity dictionary.
    """
    revision = activity.get('design_revision')
    if type(revision) is not int or revision < 1:
        raise ValueError('invalid fixture design revision')
    if not isinstance(label, str) or not label:
        raise ValueError('invalid fixture label')
    design = deepcopy(activity['page_design'])
    widgets = design.get('widgets')
    if not isinstance(widgets, list):
        raise ValueError('invalid fixture widgets')
    matches = [widget for widget in widgets if isinstance(widget, dict) and widget.get('id') == widget_id]
    if len(matches) != 1:
        raise ValueError('fixture widget id must identify exactly one widget')
    matches[0]['label'] = label
    return {
        'page_design': design,
        'result_design': deepcopy(activity['result_design']),
        'expected_design_revision': revision,
    }

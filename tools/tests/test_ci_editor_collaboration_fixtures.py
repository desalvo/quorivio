from pathlib import Path
"""Behavioral regression for the real PostgreSQL browser's remote-writer fixture."""
import copy
import unittest

from ci_editor_collaboration_fixtures import label_only_remote_patch


def saved_activity():
    return {
        'design_revision': 3,
        'page_design': {
            'backgroundColor': '#FFFFFF',
            'widgets': [
                {'id': 'pg-first', 'kind': 'text', 'label': 'Original', 'position': {'x': 11, 'y': 10, 'width': 20, 'height': 20}},
                {'id': 'pg-second', 'kind': 'text', 'label': 'Second', 'position': {'x': 41, 'y': 35, 'width': 15, 'height': 15}},
                {'id': 'pg-third', 'kind': 'text', 'label': 'Third', 'position': {'x': 75, 'y': 70, 'width': 15, 'height': 10}},
            ],
        },
        'result_design': {'header': 'Keep this result heading', 'other': {'color': '#123456'}},
    }


class CollaboratorFixtureTests(unittest.TestCase):
    def test_remote_label_only_preserves_all_widget_coordinates(self):
        activity = saved_activity()
        patch = label_only_remote_patch(activity, 'pg-first', 'Remote collaborator')
        self.assertEqual([w['position']['x'] for w in patch['page_design']['widgets']], [11, 41, 75])
        self.assertEqual(patch['page_design']['widgets'][0]['label'], 'Remote collaborator')

    def test_remote_label_only_changes_exactly_one_leaf(self):
        activity = saved_activity()
        patch = label_only_remote_patch(activity, 'pg-first', 'Remote collaborator')
        expected = copy.deepcopy(activity['page_design'])
        expected['widgets'][0]['label'] = 'Remote collaborator'
        self.assertEqual(patch['page_design'], expected)

    def test_fixture_uses_current_server_revision(self):
        activity = saved_activity()
        activity['design_revision'] = 9
        self.assertEqual(label_only_remote_patch(activity, 'pg-first', 'Remote')['expected_design_revision'], 9)

    def test_result_design_is_preserved_and_deep_copied(self):
        activity = saved_activity()
        patch = label_only_remote_patch(activity, 'pg-first', 'Remote')
        self.assertEqual(patch['result_design'], activity['result_design'])
        patch['result_design']['other']['color'] = '#000000'
        self.assertEqual(activity['result_design']['other']['color'], '#123456')

    def test_does_not_mutate_original_activity(self):
        activity = saved_activity()
        original = copy.deepcopy(activity)
        patch = label_only_remote_patch(activity, 'pg-first', 'Remote')
        patch['page_design']['widgets'][1]['position']['x'] = 0
        self.assertEqual(activity, original)

    def test_can_change_other_widget_without_touching_first(self):
        activity = saved_activity()
        patch = label_only_remote_patch(activity, 'pg-second', 'New second label')
        self.assertEqual(patch['page_design']['widgets'][0], activity['page_design']['widgets'][0])
        self.assertEqual(patch['page_design']['widgets'][1]['label'], 'New second label')

    def test_unknown_widget_is_rejected(self):
        with self.assertRaises(ValueError):
            label_only_remote_patch(saved_activity(), 'not-present', 'Remote')

    def test_duplicate_widget_identity_is_rejected(self):
        activity = saved_activity()
        activity['page_design']['widgets'][1]['id'] = 'pg-first'
        with self.assertRaises(ValueError):
            label_only_remote_patch(activity, 'pg-first', 'Remote')

    def test_bad_revision_is_rejected(self):
        for revision in (None, 0, -1, '3', True):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                activity = saved_activity()
                activity['design_revision'] = revision
                label_only_remote_patch(activity, 'pg-first', 'Remote')

    def test_empty_label_is_rejected(self):
        with self.assertRaises(ValueError):
            label_only_remote_patch(saved_activity(), 'pg-first', '')

    def test_real_browser_uses_server_snapshot_not_original_draft(self):
        self.assertIn('remote_page=next(x for x in remote_before', (Path(__file__).resolve().parents[2]/'tools/ci_browser_editor_postgres.py').read_text())
        self.assertIn('label_only_remote_patch(remote_page', (Path(__file__).resolve().parents[2]/'tools/ci_browser_editor_postgres.py').read_text())


if __name__ == '__main__':
    unittest.main()

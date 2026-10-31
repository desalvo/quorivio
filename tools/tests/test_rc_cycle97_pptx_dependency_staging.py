"""RC97 regression: native PPTX tests may not execute before python-pptx installation."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[2] / '.github/workflows/ci.yml'
NATIVE = (
    'tools.tests.test_rc74_footer_corner.FooterCornerRC74.test_powerpoint_number_at_exact_slide_right_and_bottom_without_text_insets',
    'tools.tests.test_rc91_scheme_stage.GlobalMasterRegressions.test_native_pptx_inherits_scheme_with_absolute_number_and_local_title_override',
)


class PptxDependencyStaging(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text(encoding='utf-8')
        self.install = self.workflow.index('- name: Install Python conversion and load-test dependencies')
        self.preflight = self.workflow[:self.install]
        self.after_install = self.workflow[self.install:]

    def test_no_native_pptx_test_in_early_dependency_free_gate(self):
        for test in NATIVE:
            with self.subTest(test=test):
                self.assertNotIn(test, self.preflight)
        self.assertNotIn('python3 -m unittest tools.tests.test_rc74_footer_corner -q', self.preflight)
        self.assertNotIn('python3 -m unittest tools.tests.test_rc91_scheme_stage -q', self.preflight)

    def test_pptx_dependency_is_checked_before_explicit_native_tests(self):
        self.assertIn("'python-pptx>=1.0,<2'", self.after_install)
        requirement = self.after_install.index("python3 -c 'import pptx, aiohttp'")
        for test in NATIVE:
            with self.subTest(test=test):
                self.assertIn(test, self.after_install)
                self.assertLess(requirement, self.after_install.index(test))
        self.assertLess(self.after_install.index(NATIVE[-1]),
                        self.after_install.index('python3 -m unittest discover -s tools/tests -v'))

    def test_pure_stage_and_scheme_contracts_still_run_early(self):
        for name in (
            'test_default_footer_occupies_bottom_strip_and_stays_dynamic',
            'test_browser_layout_anchors_number_to_absolute_bottom_right_not_center',
            'test_footer_number_is_pinned_to_canvas_in_all_four_surfaces',
            'test_editor_works_with_selection_and_persistent_schema',
            'test_pptx_uses_widget_style_override_and_canvas_relative_page_number',
        ):
            self.assertIn(name, self.preflight)


if __name__ == '__main__':
    unittest.main()

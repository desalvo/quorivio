"""RC283: browser evidence must open the real editor rehearsal control."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
CAPTURE=ROOT/'tools/ci_manual_real_screenshots.py'
UI=ROOT/'apps/web/src/main.tsx'


def assert_real_rehearsal_contract(capture: str, ui: str):
    selector='button.editor-preview-open.preview-presenter[aria-haspopup="dialog"]'
    assert selector in capture, 'Capture must select the real editor presenter toolbar button'
    assert re.search(r'button=editor\.locator\(PRESENTER_REHEARSAL_OPENER\)',capture), 'Capture must resolve exact UI button'
    assert 'await expect(button).to_be_enabled(timeout=12000)' in capture
    assert 'await button.click(timeout=12000)' in capture
    assert "editor.get_by_role('dialog',name='Anteprima interattiva della sessione')" in capture
    assert 'await expect(dialog).to_be_visible(timeout=12000)' in capture
    assert "get_by_role('button',name=re.compile('Anteprima'" not in capture
    assert "className={'editor-preview-open preview-'+m}" in ui, 'Presenter button must use the real preview CSS class'
    assert 'aria-haspopup="dialog"' in ui, 'Rehearsal button must explicitly open a dialog'
    assert "setRehearsalMode(m);setRehearsalOpen(true)" in ui, 'The toolbar must open the real rehearsal'
    assert 'canvas-widget-submit-preview' in ui, 'The disabled in-canvas submit preview remains, not the click target'


class RC283ManualCaptureSelector(unittest.TestCase):
    def test_real_capture_targets_enabled_editor_rehearsal(self):
        assert_real_rehearsal_contract(CAPTURE.read_text(),UI.read_text())

    def test_broad_selector_or_disabled_click_is_rejected(self):
        original=CAPTURE.read_text()
        ui=UI.read_text()
        replacements=(
            ('button.editor-preview-open.preview-presenter[aria-haspopup="dialog"]', 'button.canvas-widget-submit-preview'),
            ('await expect(button).to_be_enabled(timeout=12000)', 'await expect(button).to_be_visible(timeout=12000)'),
            ('await button.click(timeout=12000)', 'await button.click(force=True)'),
            ("editor.get_by_role('dialog',name='Anteprima interattiva della sessione')", "editor.get_by_role('button',name='Anteprima').first"),
        )
        for old,new in replacements:
            self.assertIn(old, original)
            with self.subTest(replaced=old),self.assertRaises(AssertionError):
                assert_real_rehearsal_contract(original.replace(old,new),ui)

    def test_editor_wiring_mutations_are_rejected(self):
        capture=CAPTURE.read_text()
        ui=UI.read_text()
        for old,new in (('editor-preview-open preview-', 'disabled-editor-preview-open preview-'),('aria-haspopup="dialog"', 'aria-haspopup="false"'),('setRehearsalMode(m);setRehearsalOpen(true)', 'setRehearsalMode(m)')):
            self.assertIn(old,ui)
            with self.subTest(replaced=old),self.assertRaises(AssertionError):
                assert_real_rehearsal_contract(capture,ui.replace(old,new))

    def test_real_inspector_capture_uses_correct_accessible_region(self):
        capture=CAPTURE.read_text()
        ui=UI.read_text()
        self.assertIn("get_by_role('button',name='Mostra proprietà complete del widget')",capture)
        self.assertIn("get_by_role('region',name='Proprietà widget selezionato')",capture)
        self.assertIn('ariaLabel="Proprietà widget selezionato"',ui)
        self.assertIn("inspector.get_by_role('button',name='Chiudi proprietà widget').click()",capture)
        self.assertIn('await expect(inspector).to_have_count(0,timeout=12000)',capture)

if __name__=='__main__': unittest.main()

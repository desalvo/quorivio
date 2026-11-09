"""RC290: exercise resize BEFORE asserting tab-size persistence in the real CI browser.

A content-sized Format widget panel is allowed to change height before the
presenter manually resizes it; the release requirement applies to a resized
window. This guards the exact false failure in GitHub Actions #42670034364.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CAPTURE=ROOT/'tools/ci_manual_real_screenshots.py'
UI=ROOT/'apps/web/src/main.tsx'
CSS=ROOT/'apps/web/src/style.css'


def assert_resized_tab_capture(source:str):
    start=source.index("contents=floating.get_by_role('tab',name='Contenuti')")
    end=source.index("await floating.get_by_role('button',name='Chiudi Formato widget')",start)
    body=source[start:end]
    stages=(
        'original=await floating.bounding_box()',
        "get_by_role('button',name='Ridimensiona Formattazione rapida widget selezionato (trascina o usa le frecce)')",
        'await expect(resize_handle).to_be_visible(timeout=12000)',
        'await resize_handle.focus()',
        "await resize_handle.press('Shift+ArrowRight')",
        "await resize_handle.press('Shift+ArrowDown')",
        'resized=await floating.bounding_box()',
        "resized['width']-original['width'] < 24",
        "resized['height']-original['height'] < 24",
        "await shot('editor-widget-format-resized',editor)",
        'await contents.click()',
        'after=await floating.bounding_box()',
        "abs(resized['width']-after['width']) > 2 or",
        "abs(resized['height']-after['height']) > 2):",
        "await shot('editor-widget-format-tabs',editor)",
    )
    last=-1
    for stage in stages:
        at=body.find(stage,last+1)
        if at < 0:
            raise AssertionError(f'Missing/out-of-order real format-resize check: {stage}')
        last=at
    if "round(before['width'])" in body:
        raise AssertionError('Old auto-size comparison without resize must not return')


class RC290RealFormatResizing(unittest.TestCase):
    def test_browser_capture_resizes_then_switches_tabs(self):
        assert_resized_tab_capture(CAPTURE.read_text())

    def test_regressions_in_handle_press_or_order_are_rejected(self):
        body=CAPTURE.read_text()
        for old,new in (
            ("await resize_handle.press('Shift+ArrowRight')", "await resize_handle.press('ArrowLeft')"),
            ("await resize_handle.press('Shift+ArrowDown')", "await resize_handle.press('ArrowUp')"),
            ('await expect(resize_handle).to_be_visible(timeout=12000)', 'await expect(resize_handle).to_be_hidden(timeout=12000)'),
            ("resized['height']-original['height'] < 24", "resized['height']-original['height'] < -999"),
            ("abs(resized['height']-after['height']) > 2):", "abs(resized['height']-after['height']) > 200"),
        ):
            self.assertIn(old,body)
            with self.subTest(old=old),self.assertRaises(AssertionError):
                assert_resized_tab_capture(body.replace(old,new))

    def test_tab_switch_cannot_precede_resize(self):
        body=CAPTURE.read_text()
        old="                    await contents.click()\n                    after=await floating.bounding_box()"
        self.assertIn(old,body)
        # Swapping the first visual capture and tab click moves the tab switch
        # before evidence of resizing, which the strict stage order rejects.
        moved=body.replace(
            "                    await shot('editor-widget-format-resized',editor)\n                    await contents.click()",
            "                    await contents.click()\n                    await shot('editor-widget-format-resized',editor)",1)
        with self.assertRaises(AssertionError):
            assert_resized_tab_capture(moved)

    def test_real_component_keeps_explicit_css_size_and_accessible_handle(self):
        main=UI.read_text()
        css=CSS.read_text()
        for fragment in (
            "resizeWithKeyboard=(e:React.KeyboardEvent<HTMLButtonElement>)",
            "setSize(boundFloatingSize(base.width+",
            "'--editor-floating-height':size.height+'px'",
            "className=\"editor-floating-resize-handle\"",
        ):
            self.assertIn(fragment,main)
        self.assertIn('height:var(--editor-floating-height,auto)!important;',css)
        self.assertIn('flex:1 1 0%!important;min-height:0!important;max-height:none!important;',css)

if __name__=='__main__': unittest.main()

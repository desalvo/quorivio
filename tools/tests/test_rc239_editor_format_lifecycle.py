"""RC239: real Chromium focus regression follows the RC223 explicit format dialog.

The old RC193 browser test opened the inspector and then looked for the
formatter combobox, which can only exist inside the separately opened
"Formato widget" palette. Keep the real Chromium/PostgreSQL test mandatory.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BROWSER = (ROOT / "tools/ci_rc193_editor_focus_chromium.py").read_text(encoding="utf-8")
UI = (ROOT / "apps/web/src/main.tsx").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

CLOSE = "await page.get_by_role('button',name='Chiudi proprietà widget').click()"
CONTEXT = "await widget.click(button='right',position={'x':14,'y':14})"
MENU = "context_menu=page.get_by_role('group',name='Azioni widget question',exact=True)"
OPEN = "await context_menu.get_by_role('button',name='Formato widget',exact=True).click()"
PANEL = "format_panel=page.get_by_role('toolbar',name='Formattazione rapida widget selezionato')"
VISIBLE = "await expect(format_panel).to_be_visible()"
SCOPE = "await format_panel.get_by_role('combobox',name='Ambito della formattazione').select_option('widget')"
SIZE = "size=format_panel.get_by_role('spinbutton',name='Dimensione del testo selezionato')"
INCREMENT = "await format_panel.get_by_role('button',name='Aumenta dimensione carattere di 1').click()"
FONT = "font=format_panel.get_by_role('combobox',name='Font del testo')"


def verify_browser(source: str = BROWSER) -> None:
    steps = [
        "await expect(option1).to_have_value('Testo iniziale scrivo tutta la frase')",
        "assert await option1.evaluate('e=>document.activeElement===e')",
        CLOSE, CONTEXT, MENU, OPEN, PANEL, VISIBLE, SCOPE,
        SIZE, INCREMENT, FONT,
        "await font.select_option('Georgia')",
        "assert 'Georgia' in family",
        "await font.select_option('Arial')",
        "assert 'Arial' in family",
    ]
    # The same secondary-click intentionally occurs earlier when opening the
    # inspector. Match this post-inspector sequence without rejecting it.
    positions = []
    for step in steps:
        if step != CONTEXT and source.count(step) != 1:
            raise AssertionError('missing or duplicated RC239 focus/format step: ' + step)
        positions.append(source.find(step))
    # All steps must be found *after* the preceding step.  This catches a
    # context click that happened only at the beginning of the test.
    previous = -1
    for step in steps:
        found = source.find(step, previous + 1)
        if found < 0:
            raise AssertionError('RC239 inspector/context formatter sequence is out of order')
        previous = found
    if "page.get_by_role('combobox',name='Ambito della formattazione')" in source:
        raise AssertionError('unscoped formatter combobox can hide an unopened dialog')
    if "page.get_by_role('combobox',name='Font del testo')" in source:
        raise AssertionError('font changes must be scoped to the visible format window')
    if "page.get_by_role('spinbutton',name='Dimensione del testo selezionato')" in source:
        raise AssertionError('font size must be scoped to the visible format window')


class RC239EditorFocusFormatLifecycle(unittest.TestCase):
    def test_browser_reaches_actual_format_window_after_inspector(self):
        verify_browser()

    def test_format_window_exists_only_by_explicit_context_action(self):
        self.assertIn('aria-label="Formato widget" onClick={()=>{setActive(w.id);', UI)
        self.assertIn("setFormatTab('text');setRibbonDismissed(false);setContextWidget(null)", UI)
        self.assertIn('role="toolbar" ariaLabel="Formattazione rapida widget selezionato"', UI)
        self.assertIn('aria-label="Ambito della formattazione"', UI)
        self.assertIn('const toggleSelection=(id:string,extend=false)=>{setRibbonDismissed(true);', UI)

    def test_negative_missing_explicit_action_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'missing or duplicated'):
            verify_browser(BROWSER.replace(OPEN, "await context_menu.get_by_role('button',name='Proprietà widget').click()"))

    def test_negative_inspector_not_closed_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'missing or duplicated'):
            verify_browser(BROWSER.replace(CLOSE, ''))

    def test_negative_wrong_action_order_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'out of order'):
            verify_browser(BROWSER.replace(CLOSE + '\n   ' + CONTEXT, CONTEXT + '\n   ' + CLOSE))

    def test_negative_unscoped_formatter_selector_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'missing or duplicated'):
            verify_browser(BROWSER.replace(SCOPE, SCOPE.replace('format_panel.', 'page.')))

    def test_negative_stale_font_controls_rejected(self):
        for step in (SIZE, INCREMENT, FONT):
            with self.subTest(step=step), self.assertRaisesRegex(AssertionError, 'missing or duplicated'):
                verify_browser(BROWSER.replace(step, step.replace('format_panel.', 'page.')))

    def test_early_ci_and_live_browser_gate_both_required(self):
        preflight = 'python3 -m unittest tools.tests.test_rc239_editor_format_lifecycle -q'
        self.assertIn(preflight, WORKFLOW)
        self.assertIn('python3 tools/ci_rc193_editor_focus_chromium.py', WORKFLOW)
        self.assertLess(WORKFLOW.index(preflight), WORKFLOW.index('Install reproducibly'))
        self.assertLess(WORKFLOW.index(preflight), WORKFLOW.index('python3 tools/ci_rc193_editor_focus_chromium.py'))


if __name__ == '__main__':
    unittest.main()

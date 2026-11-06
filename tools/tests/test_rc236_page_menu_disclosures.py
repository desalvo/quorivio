"""RC236: maintain real thumbnail-menu disclosure semantics in Chromium CI.

The application uses native <details> groups; hidden commands cannot be
selected by role before the corresponding summary is expanded. The previous
browser contract was an obsolete flat-menu assertion. Both authenticated
browser campaigns must follow the native click path, without force clicks.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / 'apps/web/src/main.tsx'
BROWSER = ROOT / 'tools/ci_browser_editor.py'
POSTGRES = ROOT / 'tools/ci_browser_editor_postgres.py'
WORKFLOW = ROOT / '.github/workflows/ci.yml'


def verify_disclosure_contract(ui: str, browser: str, postgres: str) -> None:
    for text in ('<details className="page-editor-thumb-submenu">',
                 '<summary>Crea e importa pagine</summary>',
                 '<summary>Esporta e dati</summary>',
                 'Nuova pagina prima', 'Nuova pagina dopo',
                 'Importa layout JSON', 'Esporta layout JSON'):
        if text not in ui:
            raise AssertionError('Product thumbnail disclosure or command missing: ' + text)

    start = browser.find("   thumb=page.get_by_role('button',name='Menu pagina 1:")
    end = browser.find("   # Keyboard and grouped arrangement", start)
    if start < 0 or end < start:
        raise AssertionError('Missing browser thumbnail interaction block')
    primary = browser[start:end]
    checks = (
        ('open create group', "await create_section.locator('summary').click()"),
        ('confirm create open', "await expect(create_section).to_have_attribute('open','')"),
        ('create-before visible', "actions.get_by_role('button',name=label)"),
        ('check JSON import', "create_section.get_by_text('Importa layout JSON')"),
        ('open export group', "await export_section.locator('summary').click()"),
        ('confirm export open', "await expect(export_section).to_have_attribute('open','')"),
        ('export button accessible', "actions.get_by_role('button',name='Esporta layout JSON')"),
    )
    for label, snippet in checks:
        if snippet not in primary:
            raise AssertionError('Main Chromium menu missing ' + label)
    if not (primary.index("await create_section.locator('summary').click()") <
            primary.index("for label in ('Nuova pagina prima','Nuova pagina dopo')")):
        raise AssertionError('Main Chromium checks create controls before expanding disclosure')
    if not (primary.index("await export_section.locator('summary').click()") <
            primary.index("actions.get_by_role('button',name='Esporta layout JSON')")):
        raise AssertionError('Main Chromium checks export control before expanding disclosure')

    for label, source in (('mocked editor reload', browser), ('PostgreSQL editor', postgres)):
        start = source.find("   # RC236: downloads are under") if label == 'mocked editor reload' else source.find("   # RC236: exercise the same native disclosure")
        if start < 0:
            raise AssertionError(label + ': no RC236 export path')
        end = source.find("    await export_actions.get_by_role('button',name='Esporta layout JSON').click()", start)
        if end < start:
            raise AssertionError(label + ': export not scoped to expanded action group')
        fragment = source[start:end]
        for snippet in ("await export_details.locator('summary').click()",
                        "await expect(export_details).to_have_attribute('open','')",
                        'async with page.expect_download()'):
            if snippet not in fragment:
                raise AssertionError(label + ': ' + snippet + ' missing before download')
        if not fragment.index("await export_details.locator('summary').click()") < fragment.index('async with page.expect_download()'):
            raise AssertionError(label + ': export disclosure was not opened before download')


class RC236PageMenuDisclosures(unittest.TestCase):
    def test_compiled_browser_menu_contract(self):
        verify_disclosure_contract(UI.read_text(), BROWSER.read_text(), POSTGRES.read_text())

    def test_mutations_fail_closed(self):
        ui, browser, postgres = UI.read_text(), BROWSER.read_text(), POSTGRES.read_text()
        for snippet in ("await create_section.locator('summary').click()",
                        "await export_section.locator('summary').click()",
                        "await expect(export_section).to_have_attribute('open','')",
                        "await export_details.locator('summary').click()"):
            with self.subTest(snippet=snippet), self.assertRaises(AssertionError):
                if snippet in browser:
                    verify_disclosure_contract(ui, browser.replace(snippet, '# removed', 1), postgres)
                else:
                    verify_disclosure_contract(ui, browser, postgres.replace(snippet, '# removed', 1))
        with self.assertRaises(AssertionError):
            verify_disclosure_contract(ui.replace('<summary>Esporta e dati</summary>', '<summary>Altro</summary>'), browser, postgres)

    def test_mandatory_chromium_and_postgres_checks_retained(self):
        workflow = WORKFLOW.read_text()
        for command in ('python3 tools/ci_browser_editor.py',
                        'python3 tools/ci_browser_editor_postgres.py',
                        'python3 tools/ci_rc224_thumbnail_menu_chromium.py',
                        'python3 -m unittest tools.tests.test_rc236_page_menu_disclosures -q'):
            with self.subTest(command=command):
                self.assertIn(command, workflow)


if __name__ == '__main__':
    unittest.main()

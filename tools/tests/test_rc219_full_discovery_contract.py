"""RC219: fail-closed contracts for both unittest import modes and relocated UI.

GitHub RC218 (42194028262) reached the 2,115-case tools/tests discovery
and found two relative import errors and four obsolete source-literal assertions.
This test deliberately guards the intended *current* behavior, not the old
literal spellings, and runs before installing npm dependencies.
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / 'tools/tests'
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN = (ROOT / 'apps/api/src/domain.ts').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
MODULES = (
    'test_editor_contextual_layout_v2',
    'test_editor_thumbnail_keyboard_rc',
    'test_page_editor_unsaved_guard',
    'test_rc142_editor_clipboard_mobile_footer',
    'test_rc_cycle198_answer_decorations',
)


def require_navigation_guard(code: str) -> None:
    required = (
        'if(designActivity&&designActivity!==a.id&&!skipNavigationConfirm&&!confirmPageNavigation())return',
        'setSelectedPageIds([a.id]);beginPageDesign(a)',
        "if(confirmPageNavigation())setDesignActivity('')",
    )
    if any(item not in code for item in required):
        raise AssertionError('page navigation must preserve the unsaved-draft fence')
    if 'setSelectedPageIds([a.id]);beginPageDesign(a,true)' in code:
        raise AssertionError('thumbnail click must not bypass the unsaved-draft fence')


def require_page_number_format(code: str) -> None:
    required = (
        'value="page-number">Numero pagina',
        "effectiveScope==='page-number'",
        "fontFamily:'footerNumberFontFamily',fontSize:'footerNumberFontSize',color:'footerNumberColor'",
        'aria-label="Font del testo"',
        'aria-label="Colore del testo"',
        'ariaLabel="Padding destro numero pagina"',
        'ariaLabel="Padding inferiore numero pagina"',
    )
    if any(item not in code for item in required):
        raise AssertionError('shared formatting ribbon must preserve editable footer-number fields')


def require_answer_decorations(code: str, schema: str) -> None:
    if "'answerUnderline','answerStrikethrough','submitBold'" not in schema or \
       "].every(k=>v[k]===undefined||typeof v[k]==='boolean')" not in schema:
        raise AssertionError('API must still type-check independent answer decoration booleans')
    required = (
        'value="answers">Risposte',
        "underline:'answerUnderline',strikethrough:'answerStrikethrough'",
        'aria-label="Sottolineato" aria-pressed={selectedFlag(\'underline\')}',
        'aria-label="Barrato" aria-pressed={selectedFlag(\'strikethrough\')}',
        "onClick={()=>setStyle({underline:!selectedFlag('underline')})}",
        "onClick={()=>setStyle({strikethrough:!selectedFlag('strikethrough')})}",
    )
    if any(item not in code for item in required):
        raise AssertionError('independent answer underline/strike controls disconnected')


class RC219FullDiscoveryContract(unittest.TestCase):
    def test_both_unittest_import_namespaces(self):
        # unittest discover -s tools/tests imports as bare test_*.  A dotted
        # invocation imports the identical source as tools.tests.test_*.
        sys.path.insert(0, str(TESTS))
        try:
            for name in MODULES:
                bare = importlib.import_module(name)
                dotted = importlib.import_module('tools.tests.' + name)
                self.assertIsNot(bare, dotted)
                self.assertGreater(unittest.defaultTestLoader.loadTestsFromModule(bare).countTestCases(), 0)
                self.assertGreater(unittest.defaultTestLoader.loadTestsFromModule(dotted).countTestCases(), 0)
        finally:
            sys.path.remove(str(TESTS))

    def test_thumbnail_helpers_are_absolute_and_share_selection_contract(self):
        from tools.tests.test_rc214_thumbnail_selection_ci import verify_thumbnail_click
        verify_thumbnail_click(UI)
        for name in MODULES[:2]:
            source = (TESTS / (name + '.py')).read_text(encoding='utf8')
            self.assertIn('from tools.tests.test_rc214_thumbnail_selection_ci import verify_thumbnail_click', source)
            self.assertNotIn('from .test_rc214_thumbnail_selection_ci', source)

    def test_unsaved_change_contract_and_mutation(self):
        require_navigation_guard(UI)
        with self.assertRaisesRegex(AssertionError, 'unsaved-draft'):
            require_navigation_guard(UI.replace('!skipNavigationConfirm&&!confirmPageNavigation()', '!skipNavigationConfirm', 1))
        with self.assertRaisesRegex(AssertionError, 'unsaved-draft'):
            require_navigation_guard(UI.replace('setSelectedPageIds([a.id]);beginPageDesign(a)', 'setSelectedPageIds([a.id]);beginPageDesign(a,true)', 1))

    def test_footer_format_contract_and_mutation(self):
        require_page_number_format(UI)
        with self.assertRaisesRegex(AssertionError, 'footer-number'):
            require_page_number_format(UI.replace("fontFamily:'footerNumberFontFamily'", "fontFamily:'fontFamily'", 1))

    def test_answer_decorations_and_mutations(self):
        require_answer_decorations(UI, DOMAIN)
        with self.assertRaises(AssertionError):
            require_answer_decorations(UI, DOMAIN.replace("'answerUnderline','answerStrikethrough','submitBold'", "'answerUnderline','submitBold'", 1))
        with self.assertRaises(AssertionError):
            require_answer_decorations(UI.replace('aria-label="Barrato"', 'aria-label="B-R"', 1), DOMAIN)

    def test_pre_npm_ci_covers_exact_global_discovery_modes(self):
        self.assertIn('RC219 Python discovery import and historical UI contracts before npm', WORKFLOW)
        self.assertIn('tools.tests.test_rc219_full_discovery_contract', WORKFLOW)
        self.assertIn('unittest discover -s tools/tests -p "$case" -q', WORKFLOW)
        for name in MODULES:
            self.assertIn(name + '.py', WORKFLOW)


if __name__ == '__main__':
    unittest.main()

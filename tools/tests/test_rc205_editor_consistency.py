"""RC205 fail-fast source contracts for editor/master parity and imported pages.

These are dependency-free preflight guards. CI still must run the actual
React/Chromium/PostgreSQL and native converter suites before RC acceptance.
"""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WEB = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
API = (ROOT / 'apps/api/src/server.ts').read_text(encoding='utf8')
DOMAIN = (ROOT / 'apps/api/src/domain.ts').read_text(encoding='utf8')
RICH = (ROOT / 'apps/web/src/widget-text-marks.ts').read_text(encoding='utf8')
PPTX = (ROOT / 'tools/pptx_portable.py').read_text(encoding='utf8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


def guard_editor_consistency(web: str, css: str, api: str, domain: str, pptx: str) -> None:
    """The earliest CI step must reject silent regressions before npm install."""
    necessary_web = (
        'WidgetContentFit editor textStyle={widgetTypographyStyle(',
        'sourceActivities={snap.activities}',
        'peerWidgets={w.kind===\'results-button\'&&w.targetActivityId',
        'sampleStatisticRows(linkedStatisticSource(widget,peerWidgets)!,42)',
        "formatScope,setFormatScope]=useState<'widget'|'label'|'description'|'answers'|'submit'|'page-number'>",
        '<option value="submit">Pulsante di invio</option>',
        '<option value="page-number">Numero pagina</option>',
        "fontFamily:'submitFontFamily'",
        "fontFamily:'footerNumberFontFamily'",
        "'single','multiple'].includes(w.answerMode||'text')",
        "questionModeOptions(selectedQuestion.options||[],e.target.value)",
        'Selezionare solo le risposte vere',
        'Selezionare solo una risposta',
        'pageExportError&&<p className="page-editor-export-error" role="alert">',
        'if(designActivity&&!confirmPageNavigation())return;',
        'beginPageDesign(imported,true)',
        'conversion_worker_not_configured',
    )
    for pattern in necessary_web:
        if pattern not in web:
            raise AssertionError('RC205 editor regression: '+pattern)
    for forbidden in ('aria-label="Font delle risposte"', 'aria-label="Font numero pagina"',
                      'aria-label="Dimensione tasto invio"'):
        if forbidden in web:
            raise AssertionError('Duplicate font control returned: '+forbidden)
    for fragment in ('height:auto!important;min-height:0!important;width:min(860px',
                     'palette-ribbon-groups', 'overflow-wrap:anywhere!important',
                     '.widget-truth-hint'):
        if fragment not in css:
            raise AssertionError('Missing editor layout safeguard: '+fragment)
    for fragment in ('submitFontFamily', 'submitColor', 'footerNumberFontFamily',
                     'footerNumberFontSize', 'answerFontFamily'):
        if fragment not in domain:
            raise AssertionError('Missing persisted typography field: '+fragment)
    for fragment in ("backgroundAssetId:assetId", "importedImageFit",
                     "suppressMaster:suppressMaster==='1'", 'widgets:[]',
                     'presentation_slide_assets(activity_id,asset_id)'):
        if fragment not in api:
            raise AssertionError('Imported page not visible in the editor: '+fragment)
    if "if asset_id == slide_asset_id and widget.get('kind') == 'image':" not in pptx:
        raise AssertionError('Imported image would be duplicated in PPTX')


class RC205EditorConsistency(unittest.TestCase):
    def test_shared_editor_master_font_controls_and_import(self):
        guard_editor_consistency(WEB, CSS, API, DOMAIN, PPTX)
        self.assertIn('widgets={schemaWidgets}', WEB)
        self.assertIn('applyAllWidgetTypeface', RICH)
        self.assertIn('answerFontFamily:change.fontFamily', RICH)

    def test_guard_rejects_unwrapped_answers(self):
        with self.assertRaisesRegex(AssertionError, 'layout'):
            guard_editor_consistency(WEB, CSS.replace('height:auto!important;min-height:0!important;width:min(860px', 'height:100vh!important;min-height:100vh!important;width:min(860px', 1), API, DOMAIN, PPTX)

    def test_guard_rejects_old_raster_only_import(self):
        with self.assertRaisesRegex(AssertionError, 'Imported page'):
            guard_editor_consistency(WEB, CSS, API.replace("backgroundAssetId:assetId", "media:[{kind:'image'}]", 1), DOMAIN, PPTX)

    def test_guard_rejects_duplicate_font_picker(self):
        with self.assertRaisesRegex(AssertionError, 'Duplicate'):
            guard_editor_consistency(WEB+' aria-label="Font delle risposte"', CSS, API, DOMAIN, PPTX)

    def test_ci_runs_contract_before_dependencies(self):
        self.assertIn('tools.tests.test_rc205_editor_consistency', CI)
        self.assertLess(CI.index('tools.tests.test_rc205_editor_consistency'), CI.index('Install reproducibly'))
        self.assertIn('tools.tests.test_rc205_native_slide_roundtrip', CI)

if __name__ == '__main__':
    unittest.main()

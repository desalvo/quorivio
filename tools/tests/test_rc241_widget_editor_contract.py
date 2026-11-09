"""RC241 pre-npm contracts for editor results, mobile previews and number entry.

Deliberately fail closed if a new UI accidentally removes independent result
styles, editable numeric inputs, editor toolbar actions or shared stage geometry.
"""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
RESULT=(ROOT/'apps/web/src/result-format-controls.tsx').read_text(encoding='utf8')
NUMBER=(ROOT/'apps/web/src/editable-number-field.tsx').read_text(encoding='utf8')
PHONE=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

# The linked result row supports the RC241 direct style and the composed
# style object introduced by RC270 to apply pie-slice palette colors.
# Match the same JSX element so another call cannot mask a lost row style.
_ROW_STYLE = re.compile(
 r"""style\s*=\s*\{\s*(?:\{\s*\.\.\.\s*)?resultTextCss\s*\(\s*widget\.resultTextStyles\s*,\s*resultElementKey\s*\(\s*['"]row['"]\s*,"""
)

def _has_per_row_style(ui: str) -> bool:
 start = ui.find('<span className="linked-result-pair"')
 if start < 0:
  return False
 end = ui.find('><span className="linked-result-label"',start)
 if end < 0:
  return False
 fragment = ui[start:end]
 return 'data-result-custom=' in fragment and _ROW_STYLE.search(fragment) is not None

def verify_contract(ui=UI, css=CSS, result=RESULT, number=NUMBER, phone=PHONE):
 checks={
  'per-row-result-style': _has_per_row_style(ui),
  'last-word-font': '.linked-result-pair>.linked-result-final' in css and 'font-size:inherit!important' in css,
  'independent-result-controls': 'onCommit={n=>update(item.key,{fontSize:n})}' in result and "resultElementKey('row',questionId,o.id)" in result,
  'editable-draft': 'onBlur={e=>{focused.current=false;commit(e.currentTarget.value)}}' in number and 'setDraft(next);' in number,
  'explicit-number-arrows': "onClick={()=>stepBy(1)}" in number and "onClick={()=>stepBy(-1)}" in number,
  'numeric-widget-sizes': '<EditableNumberField ariaLabel="Dimensione emoji reazioni"' in ui and '<EditableNumberField ariaLabel="Dimensione pulsanti gradimento"' in ui,
  'mobile-height-reduction': '(options.length?150:190)+optionSpace' in phone,
  'matching-mobile-geometry': 'padding:10px!important' in css and 'data-canvas-device="phone"' in css,
  'unified-preview-stage': 'function DesktopRehearsalStage(' in ui and '<DesktopRehearsalStage immersive={fullScreen}>{renderSlide(\'presenter\')}</DesktopRehearsalStage>' in ui,
  'toolbar-clipboard': "issueEditorClipboard('cut')" in ui and "issueEditorClipboard('copy')" in ui and "issueEditorClipboard('paste')" in ui,
  'toolbar-history': 'onClick={undoPageWidgets}' in ui and 'onClick={redoPageWidgets}' in ui,
  'toolbar-info': 'aria-label="Informazioni editor"' in ui,
 }
 failed=[k for k,value in checks.items() if not value]
 if failed:raise AssertionError('RC241 UI contract missing: '+', '.join(failed))
 return len(checks)

class RC241EditorAndNumberPreflight(unittest.TestCase):
 def test_full_product_contract(self):self.assertEqual(verify_contract(),12)
 def test_negative_remove_per_row_style(self):
  # Removal of independent per-answer text styling remains a hard failure.
  altered=UI.replace("...resultTextCss(widget.resultTextStyles,resultElementKey('row',", "...removedRowStyle(widget.resultTextStyles,resultElementKey('row',")
  self.assertNotEqual(altered,UI)
  with self.assertRaisesRegex(AssertionError,'per-row-result-style'):
   verify_contract(ui=altered)
 def test_legacy_direct_row_style_is_accepted(self):
  # Original JSX style={resultTextCss(...)} is still supported.
  composed="style={{...resultTextCss(widget.resultTextStyles,resultElementKey('row',widget.targetQuestionId||'',r.id)),"
  self.assertIn(composed,UI)
  legacy=UI.replace(composed,"style={resultTextCss(widget.resultTextStyles,resultElementKey('row',widget.targetQuestionId||'',r.id))} data-style-extension={{",1)
  self.assertTrue(_has_per_row_style(legacy))
 def test_negative_remove_number_commit(self):
  with self.assertRaisesRegex(AssertionError,'editable-draft'):
   verify_contract(number=NUMBER.replace('commit(e.currentTarget.value)','setDraft(\'\')'))
 def test_negative_remove_independent_option_size(self):
  with self.assertRaisesRegex(AssertionError,'independent-result-controls'):
   verify_contract(result=RESULT.replace('onCommit={n=>update(item.key,{fontSize:n})}',''))
 def test_negative_remove_presenter_stage(self):
  with self.assertRaisesRegex(AssertionError,'unified-preview-stage'):
   verify_contract(ui=UI.replace('function DesktopRehearsalStage(','function LegacyRehearsalStage('))
 def test_negative_remove_cut_toolbar(self):
  with self.assertRaisesRegex(AssertionError,'toolbar-clipboard'):
   verify_contract(ui=UI.replace("issueEditorClipboard('cut')",'void 0'))
 def test_early_ci_gate_before_npm_and_active_inventory(self):
  self.assertIn('tools.tests.test_rc241_widget_editor_contract',CI)
  self.assertIn('apps/web/test/rc241-editable-widget-numbers.test.ts',CI)
  self.assertLess(CI.index('tools.tests.test_rc241_widget_editor_contract'),CI.index('run: npm run build'))
  self.assertIn('python3 tools/verify_rc_cycle241_inventory.py',CI)

if __name__=='__main__':unittest.main()

"""RC247 pre-npm CI contract: browser zoom, widget scope, result text and converter tags."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]

class RC247(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ui=(ROOT/'apps/web/src/main.tsx').read_text()
  cls.zoom=(ROOT/'apps/web/src/global-page-zoom.ts').read_text()
  cls.css=(ROOT/'apps/web/src/style.css').read_text()
  cls.results=(ROOT/'apps/web/src/result-text-style.ts').read_text()
  cls.workflow=(ROOT/'.github/workflows/converter-image.yml').read_text()
  cls.upgrade=(ROOT/'tools/k8s_converter_upgrade.py').read_text()
 def test_selection_cannot_override_explicit_widget_scope(self):
  self.assertIn("const effectiveScope=formatScope==='widget'?'widget':selectedRange",self.ui)
  self.assertIn('applyAllWidgetTypeface(w,changes as InlineStyle)',self.ui)
 def test_results_in_proportional_canvas_units(self):
  self.assertIn('(x.fontSize/12.8).toFixed(5)}cqw',self.results)
  self.assertNotIn('`${x.fontSize}px`',self.results)
 def test_browser_like_zoom_and_full_viewport(self):
  self.assertIn('GLOBAL_ZOOM_BASE=0.8',self.zoom)
  self.assertIn('GLOBAL_ZOOM_CSS_VARIABLE',self.ui)
  self.assertIn('calc(100vw / var(--quorivio-ui-scale))',self.css)
  self.assertIn('calc(100dvh / var(--quorivio-ui-scale))',self.css)
 def test_default_arial_preserves_explicit_custom(self):
  self.assertIn('.widget-rich-inline>span',self.css)
  self.assertNotIn('font-family:Arial!important',self.css)
 def test_converter_main_latest_git_tag_and_manual_consent(self):
  self.assertIn('image_tag=latest',self.workflow)
  self.assertIn('refs/tags/',self.workflow)
  self.assertIn('inputs.confirm_publish == true',self.workflow)
  self.assertNotIn('publish_tag:',self.workflow)
  self.assertIn('desalvo/quorivio-converter:$image_tag',self.workflow)
  self.assertNotIn("image.endswith(':latest')",self.upgrade)
 def test_full_ci_remains_strict(self):
  ci=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('RC247 compact full-viewport typography and converter regression',ci)
  self.assertIn('python3 tools/ci_rc247_zoom_editor_chromium.py',ci)

if __name__=='__main__':unittest.main()

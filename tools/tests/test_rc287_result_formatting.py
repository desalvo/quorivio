"""RC287 results UI and editorial release contracts (before npm)."""
from pathlib import Path
from tools.manual_release_metadata import CYCLE
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()

class RC287ResultFormatting(unittest.TestCase):
 def test_gradients_use_two_safe_persisted_colors(self):
  self.assertIn('barGradientStartColor?:string;barGradientEndColor?:string',DOMAIN)
  self.assertIn("['barGradientStartColor','barGradientEndColor']",DOMAIN)
  self.assertIn("/^#[0-9a-fA-F]{6}$/",DOMAIN)
  self.assertIn('aria-label="Colore iniziale gradiente barre"',MAIN)
  self.assertIn('aria-label="Colore finale gradiente barre"',MAIN)
  self.assertIn('resultBarGradient(widget.barGradientStartColor',MAIN)
 def test_r_stays_available_without_authoring_footer_overlap(self):
  self.assertIn('setTruthVisible(v=>!v)',MAIN)
  self.assertNotIn('className="canvas-results-truth-toggle"',MAIN)
 def test_resized_bounds_are_not_capped_at_390_pixels(self):
  self.assertIn("'--editor-floating-height':size.height+'px'",MAIN)
  self.assertIn('max-height:calc(100dvh - 16px)!important;',CSS)
  self.assertIn('flex:1 1 0%!important;min-height:0!important;max-height:none!important;',CSS)
 def test_colour_outlines_preserve_layout(self):
  self.assertIn('border-width:3px!important;border-style:solid!important',CSS)
  self.assertIn('min-height:max-content!important;height:auto!important',CSS)
  self.assertIn('.linked-source-answers{gap:clamp(7px',CSS)
 def test_navigation_preserves_real_icons(self):
  self.assertIn('className="panel dashboard-nav"',MAIN)
  self.assertIn('aria-current={dashboardPage===key?',MAIN)
  self.assertIn('background:linear-gradient(100deg,#0c816f,#0c705f)',CSS)
 def test_six_manuals_current_and_without_raw_commit_ids(self):
  for role in ('admin','presenter','user'):
   for lang in ('it','en'):
    text=(ROOT/f'docs/manuals-src/{role}-guide.{lang}.md').read_text()
    self.assertIn(f'RC{CYCLE}',text)
    self.assertIn('<!-- REAL_SCREENSHOT_GALLERY -->',text)
    self.assertNotRegex(text,r'\b[0-9a-f]{40}\b')
    self.assertIn('Appendice' if lang=='it' else 'Appendix',text)
 def test_six_published_pdfs_are_current_and_illustrated(self):
  import fitz
  for role in ('admin','presenter','user'):
   for lang in ('it','en'):
    pdf=ROOT/f'docs/manuals/{role}-guide.{lang}.pdf'
    web=ROOT/f'apps/web/public/docs/manuals/{role}-guide.{lang}.pdf'
    self.assertEqual(pdf.read_bytes(),web.read_bytes())
    with fitz.open(pdf) as doc:
     body='\n'.join(page.get_text() for page in doc)
     self.assertIn(f'RC{CYCLE}',body)
     self.assertNotRegex(body,r'\b(?:commit|Commit)\s+[0-9a-f]{8,40}\b')
     self.assertGreaterEqual(sum(len(page.get_image_info()) for page in doc),10)
     self.assertIn(('colori' if lang=='it' else 'colours') if role=='user' else ('gradiente' if lang=='it' else 'gradient'),body.lower())

if __name__=='__main__':unittest.main()

"""RC226 mobile presenter/editor contract, with browser test as separate gate."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
UI=(R/'apps/web/src/main.tsx').read_text()
CSS=(R/'apps/web/src/style.css').read_text()

class ResponsiveStudio(unittest.TestCase):
 def test_participant_defaults_to_mobile_without_forcing_manual_switch(self):
  self.assertIn('defaultParticipantPhoneMode(window.innerWidth,window.matchMedia',UI)
  self.assertIn('setParticipantPhoneMode(false)',UI)
  self.assertIn('setParticipantPhoneMode(true)',UI)
 def test_toolbar_has_caption_and_tooltip(self):
  for value in ['function SchemaRibbonButton(', 'className="slide-scheme-ribbon-icon"','className="slide-scheme-ribbon-caption"','title={hint}', 'schemaAlignIcons[mode]']:
   self.assertIn(value,UI)
 def test_schema_widgets_use_same_icon_component(self):
  self.assertIn('<EditorWidgetIcon kind={kind}/>',UI)
  self.assertIn('data-widget-kind={kind} data-graphic-palette={kind}',UI)
  self.assertIn('data-widget-kind={kind} disabled={schemaSaving',UI)
 def test_responsive_rules_only_in_small_viewports(self):
  section=CSS.split('/* RC226 — Mobile presenter/admin workspace.',1)[1]
  self.assertIn('@media(max-width:760px)',section)
  for name in ['.dashboard>.workspace', '.slide-scheme-ribbon', '.slide-scheme-inspector', 'body .editor-ux-v2 .page-editor-sidebar', 'body .editor-ux-v2 .editor-stage', '.rehearsal-shell', '.presenter-stage-tools']:
   self.assertIn(name,section)
 def test_safe_mobile_controls_not_desktop_canvas_resize(self):
  self.assertIn('body .editor-ux-v2 .page-editor-thumbnails{display:flex!important;flex-direction:row!important',CSS)
  self.assertIn('grid-template-columns:minmax(0,1fr)!important;',CSS.split('/* RC226 — Mobile presenter/admin workspace.',1)[1])
  self.assertNotIn('grid-template-columns:minmax(0,1fr)!important;',CSS.split('/* RC226 — Mobile presenter/admin workspace.',1)[0][-50:])

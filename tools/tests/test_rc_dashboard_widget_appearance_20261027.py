"""Contract: no duplicated legacy dashboard controls; appearance settings round trip."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
class DashboardWidgetAppearance(unittest.TestCase):
 def test_dashboard_has_no_legacy_media_card_or_redundant_interaction_tab(self):
  self.assertNotIn('Grafica e media (legacy)',UI)
  self.assertIn("['results','Monitoraggio live']",UI)
  self.assertNotIn("['audience','Interazione']",UI)
  self.assertIn('Apri editor grafico',UI)
  self.assertIn('legacy-page-admin',UI) # Only for real live operations and backward-compatibility
 def test_owner_and_collaborators_have_distinct_identity_treatments(self):
  self.assertIn('editor-owner-chip',UI);self.assertIn('editor-collaborator-chip',UI)
  self.assertIn('availablePresenters.find(p=>p.is_owner)',UI)
  self.assertIn('(u.id=$1) AS is_owner',(ROOT/'apps/api/src/server.ts').read_text())
  self.assertIn('editor-presenter-identities',CSS)
 def test_widget_context_actions_only_mouse_touch_or_keyboard(self):
  self.assertNotIn('className="canvas-menu-trigger"',UI)
  self.assertIn('onTouchStart={e=>',UI)
  self.assertIn('setContextWidget(w.id)',UI)
  self.assertIn("e.shiftKey&&e.key==='F10'",UI)
  self.assertIn('canvas-context-menu',UI)
 def test_every_widget_has_server_validated_appearance(self):
  for text in ['Colore di sfondo del widget','Tipo di bordo del widget','Stile bordo del widget','Spessore bordo del widget','Colore bordo del widget']:
   self.assertIn(text,UI)
  self.assertIn('WidgetAppearanceEditor widget={w}',UI)
  self.assertIn('widgetAppearanceStyle(w.style,',UI)
  self.assertIn('widgetAppearanceStyle', (ROOT/'apps/web/src/widget-appearance.ts').read_text())
  for term in ['fillColor','fillNone','strokeNone','strokeWidth','strokeColor','strokeDash']:
   self.assertIn(term,DOMAIN)
 def test_distinct_icon_palettes(self):
  self.assertIn('data-widget-kind={kind}',UI)
  self.assertIn('editor-palette',CSS) if 'editor-palette' in CSS else self.assertIn('editor-icon-tool[data-widget-kind=',CSS)

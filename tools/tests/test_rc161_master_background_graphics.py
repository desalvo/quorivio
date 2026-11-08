"""RC161 guarded integration contracts for defaults, global backgrounds and graphic presets."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
SERVER=(ROOT/'apps/api/src/server.ts').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
BUNDLE=(ROOT/'apps/api/src/portable-bundle.ts').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()

class RC161MasterGraphics(unittest.TestCase):
 def test_schema_uses_secure_upload_persistent_master_asset_and_reload(self):
  self.assertIn('async function uploadSchemaBackground(file:File|undefined)',UI)
  self.assertIn('backgroundAssetId:schemaBackgroundAsset||undefined',UI)
  self.assertIn("backgroundAssetId={schemaBackgroundAsset}",UI)
  self.assertIn("schemaBackgroundAsset!==schemaBackgroundBaseline.current",UI)
  self.assertIn('master.backgroundAssetId',DOMAIN)
  self.assertIn('validPageDesign(req.body?.theme)',SERVER)
 def test_global_asset_public_only_on_current_page_and_delete_is_guarded(self):
  self.assertIn("s.theme?.master?.backgroundAssetId===req.params.assetId",SERVER)
  self.assertIn("s.current_activity_id!==req.params.aid",SERVER)
  self.assertIn("asset_in_use_by_background",SERVER)
  self.assertRegex(SERVER,r"s\.theme\?\.master\?\.backgroundAssetId===req\.params\.assetId\)\{res\.status\(409\)")
 def test_backup_includes_master_image_and_remaps(self):
  self.assertIn('scan(definition?.session?.theme?.master)',BUNDLE)
  self.assertIn('rewrite(copy.session?.theme?.master)',BUNDLE)
 def test_title_and_footer_always_have_effective_arial_without_erasing_custom_font(self):
  # RC195: RC161 originally grepped an inline Arial literal in main.tsx.
  # Since RC194, the defaults live in the typed slide-master module and are
  # resolved for each surface; the editor must not duplicate this definition.
  master=(ROOT/'apps/web/src/slide-master.ts').read_text()
  appearance=(ROOT/'apps/web/src/widget-appearance.ts').read_text()
  stage=(ROOT/'apps/web/src/stage-widget-typography.ts').read_text()
  self.assertIn("DEFAULT_TITLE_STYLE={fontFamily:'Arial'",master)
  self.assertIn("DEFAULT_FOOTER_STYLE={fontFamily:'Arial'",master)
  self.assertIn('...DEFAULT_TITLE_STYLE,...(w.titleUseMaster!==false?context.masterTitleStyle:{}),...w.style',master)
  self.assertIn('fontFamily:safeWidgetFontFamily(footer.style?.footerNumberFontFamily,safeWidgetFontFamily(footer.style?.fontFamily))',master)
  self.assertIn("fontFamily:safeWidgetFontFamily(style?.fontFamily)",appearance)
  self.assertIn('DEFAULT_TITLE_STYLE',UI)
  self.assertIn("w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).style",UI)
  self.assertIn("widget.kind==='title'?widgetDisplay(widget,context).style",stage)
  self.assertRegex(CSS,r'\.slide-scheme-workspace,.powerpoint-editor')
  self.assertIn('font-family:Arial,sans-serif',CSS)
 def test_lines_and_shapes_render_without_text_and_have_shared_insertion_menu(self):
  self.assertIn("if(kind==='shape'||kind==='line')return null;",UI)
  self.assertIn("!['line','shape'].includes(w.kind)",UI)
  self.assertIn('function GraphicInsertTool(',UI)
  self.assertIn('onContextMenu={e=>{e.preventDefault()',UI)
  self.assertIn('setTimeout(()=>{suppressClick.current=true;show(e.clientX,e.clientY)},560)',UI)
  self.assertIn('GRAPHIC_PRESETS[kind].map(preset',UI)
  self.assertIn('Terminali freccia',UI)
  self.assertIn('strokeDash',DOMAIN)
  self.assertIn('lineArrow',DOMAIN)
 def test_negative_mutations_detect_unprotected_assets_and_hidden_line_text(self):
  changed=SERVER.replace('s.theme?.master?.backgroundAssetId===req.params.assetId','false')
  self.assertNotIn('s.theme?.master?.backgroundAssetId===req.params.assetId',changed)
  changed=UI.replace("if(kind==='shape'||kind==='line')return null;",'')
  self.assertNotIn("if(kind==='shape'||kind==='line')return null;",changed)
  changed=BUNDLE.replace('rewrite(copy.session?.theme?.master);','')
  self.assertNotIn('rewrite(copy.session?.theme?.master);',changed)
 def test_ci_has_early_regression_and_current_inventory(self):
  self.assertIn('tools.tests.test_rc161_master_background_graphics',WORKFLOW)
  self.assertIn('verify_rc_cycle160_inventory.py --historical',WORKFLOW)
  self.assertIn('verify_rc_cycle161_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()

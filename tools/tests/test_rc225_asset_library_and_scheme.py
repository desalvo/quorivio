"""RC225 upload labels, delete 204, visual backgrounds and master canvas regression."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
API=(ROOT/'apps/api/src/server.ts').read_text()
SCHEMA=(ROOT/'apps/api/src/schema.sql').read_text()

class AssetLibraryRegression(unittest.TestCase):
 def test_delete_no_json_body_and_immediate_refresh(self):
  self.assertIn('res.status===204||res.status===205?undefined as T:res.json()',UI)
  self.assertIn('setAssets(old=>old.filter(item=>item.id!==id))',UI)
  self.assertIn('await refreshAssets();setNotice(\'Allegato eliminato.\')',UI)
 def test_names_are_persisted_and_rename_endpoint_available(self):
  self.assertIn("app.patch('/api/sessions/:id/assets/:assetId'",API)
  self.assertIn('session_assets ADD COLUMN IF NOT EXISTS display_name',SCHEMA)
  self.assertIn('uq_session_asset_display_name',SCHEMA)
  self.assertIn('uq_background_display_name',SCHEMA)
  self.assertIn("'X-Quorivio-Filename':encodeURIComponent(file.name)",UI)
  self.assertIn("'X-Quorivio-Allow-Rename':'1'",UI)
  self.assertIn("if(!window.confirm(`Esiste già un file",UI)
  self.assertIn('async function renameAsset(id:string)',UI)
 def test_opaque_backend_path_preserved(self):
  self.assertIn('const backgroundPath=(uid:string,id:string)=>path.join(backgroundRoot,uid,id);',API)
  self.assertNotIn('path.join(backgroundRoot,uid,named.name)',API)
 def test_gallery_covers_all_background_flows(self):
  self.assertIn('function BackgroundGallery(',UI)
  for a in ['Scegli sfondo canvas','Seleziona sfondo pagina dalla libreria','Seleziona sfondo risultati dalla libreria','Immagine sfondo dello schema','Immagine da gestire nella libreria']:
   self.assertIn(f'label="{a}"',UI)
  self.assertIn('background-gallery-choice',CSS)
  self.assertIn('<img loading="lazy" src={item.url}',UI)
 def test_background_copies_and_portable_names_survive_deletion(self):
  self.assertIn('background_library_copy boolean NOT NULL DEFAULT false',SCHEMA)
  self.assertIn('WHERE display_name IS NOT NULL AND participant_id IS NULL AND NOT background_library_copy',SCHEMA)
  self.assertIn('source_background_id,display_name,background_library_copy',API)
  self.assertIn('asset.background_library_copy===true',API)
  self.assertIn('background_library_copy:true',API)
  self.assertIn('coalesce(sa.display_name,b.display_name) AS display_name',API)
  bundle=(ROOT/'apps/api/src/portable-bundle.ts').read_text()
  self.assertIn('background_library_copy?:boolean',bundle)
  self.assertIn('display_name?:string',bundle)
 def test_background_name_migration_resolves_legacy_duplicates(self):
  self.assertIn('row_number() OVER (PARTITION BY owner_id,lower(display_name)',SCHEMA)
  self.assertIn('CREATE UNIQUE INDEX IF NOT EXISTS uq_background_display_name',SCHEMA)
  self.assertLess(SCHEMA.index('ADD COLUMN IF NOT EXISTS participant_id'),SCHEMA.index('uq_session_asset_display_name'))
 def test_scheme_background_previews_same_asset_as_pages(self):
  self.assertIn('backgroundAssetId={schemaBackgroundAsset}',UI)
  self.assertIn('.slide-scheme-canvas .canvas-with-rulers .widget-canvas{background-image:var(--editor-page-background,none)!important',CSS)
  self.assertIn('setSchemaBackgroundAsset(applied.id)',UI)

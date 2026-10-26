"""Static contracts complement unit tests and the real PostgreSQL/Chromium CI smoke."""
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
IMAGE=(ROOT/'apps/api/src/profile-image.ts').read_text()
HTTP=(ROOT/'tools/ci_portable_http.py').read_text()
BROWSER=(ROOT/'tools/ci_browser_profile.py').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()

class ProfileHardeningContracts(unittest.TestCase):
 def test_approved_user_can_read_profile_without_presenter_role(self):
  route=API.split("app.get('/api/auth/profile'",1)[1].split("app.patch('/api/auth/profile'",1)[0]
  self.assertIn('requireAuth',route)
  self.assertNotIn('requirePresenter',route)
  self.assertIn('nickname,display_name,profile_photo_url',route)
  self.assertIn("'Cache-Control','private, no-store'",route)
 def test_profile_page_uses_role_neutral_endpoint(self):
  self.assertIn("request<any>('/auth/profile').then",WEB)
 def test_uploaded_image_metadata_checked_before_scanning_and_publication(self):
  route=API.split("app.post('/api/auth/profile/photo'",1)[1].split("app.get('/api/auth/profile/photo/:imageId'",1)[0]
  self.assertLess(route.index('inspectProfileImage(await readFile(destination),type)'),route.index('await scanUploadedFile(destination)'))
  self.assertLess(route.index('await scanUploadedFile(destination)'),route.index('await replaceProfilePhoto(uid,url)'))
 def test_invalid_photo_returns_client_error(self):
  self.assertIn("res.status(415).json({error:'invalid_profile_image'})",API)
 def test_corrupted_stored_photos_are_not_served(self):
  self.assertEqual(API.count('inspectProfileImage(data,'),2)
 def test_max_image_side(self):
  self.assertIn('MAX_PROFILE_IMAGE_SIDE=4096',IMAGE)
 def test_max_decoded_pixels(self):
  self.assertIn('MAX_PROFILE_IMAGE_PIXELS=16_000_000',IMAGE)
 def test_webp_variants(self):
  for kind in ('VP8X','VP8L','VP8 '):self.assertIn(kind,IMAGE)
 def test_jpeg_marker_scan(self):
  self.assertIn('const size=b.readUInt16BE(offset)',IMAGE)
 def test_profile_photo_mutations_serialized_in_ui(self):
  self.assertIn('disabled={photoBusy||profileSaving}',WEB)
  self.assertIn('disabled={photoBusy||profileSaving||!myProfile?.profile_photo_url}',WEB)
 def test_profile_save_pending_and_validation(self):
  self.assertIn('setProfileSaving(true)',WEB)
  self.assertIn('profileName.trim().length<2',WEB)
 def test_avatar_cache_busting(self):
  self.assertIn('setPhotoVersion(v=>v+1)',WEB)
  self.assertIn('profile_photo_url}?v=${photoVersion}',WEB)
 def test_http_checks_anonymous_photo_scope(self):
  self.assertIn("profiles[0]['photo_url']",HTTP)
  self.assertIn('opener=anonymous',HTTP)
 def test_http_checks_photo_replacement_and_removal(self):
  self.assertIn("replacement['profile_photo_url'] != photo['profile_photo_url']",HTTP)
  self.assertIn("api('DELETE', '/api/auth/profile/photo')",HTTP)
 def test_browser_checks_real_file_upload(self):
  self.assertIn('.set_input_files(',BROWSER)
  self.assertIn("'mimeType':'image/png'",BROWSER)
 def test_browser_checks_public_private_separation(self):
  self.assertIn('private.status==401',BROWSER)
  self.assertIn('removed.status==404',BROWSER)
 def test_ci_runs_real_profile_browser_smoke(self):
  self.assertIn('python3 tools/ci_browser_profile.py',CI)
  self.assertIn('inputs.browser_test',CI)

if __name__=='__main__':unittest.main()

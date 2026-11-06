"""RC228: the RC225 gallery test must accept a portaled RC227 master dialog.

The regression is not just the label text: the dialog must still be present,
select the correct asset and close on selection. Verify compatibility with the
exact call-site shape committed in GitHub CI #42226572219 (which does not pass
an inline master label) and verify that deleting the modal fails the test.
"""
import unittest
from unittest.mock import patch
from tools.tests import test_rc225_asset_library_and_scheme as history

class RC228GalleryHistoryCompatibility(unittest.TestCase):
 def test_committed_modal_without_legacy_label_remains_covered(self):
  # The ZIP may carry an optional backward-compatible label prop; the original
  # RC227 GitHub commit used a static accessible gallery label instead.
  committed_shape = history.UI.replace(
   'label="Immagine sfondo dello schema" onSelect={setSchemaBackgroundAsset}',
   'onSelect={setSchemaBackgroundAsset}'
  ).replace(
   "label='Immagine sfondo dello schema'", "label='Scegli lo sfondo globale'"
  ).replace('disabled={disabled} label={label} onSelect={id=>{onSelect(id);setOpen(false)}}',
            'disabled={disabled} label="Scegli lo sfondo globale" onSelect={id=>{onSelect(id);setOpen(false)}}')
  self.assertNotIn('label="Immagine sfondo dello schema"',committed_shape)
  with patch.object(history,'UI',committed_shape):
   history.AssetLibraryRegression('test_gallery_covers_all_background_flows').test_gallery_covers_all_background_flows()
 def test_modal_removed_must_fail_historical_gallery_contract(self):
  self.assertIn('role="dialog" aria-modal="true"',history.UI)
  with patch.object(history,'UI',history.UI.replace('role="dialog" aria-modal="true"','role="group"')):
   with self.assertRaises(AssertionError):
    history.AssetLibraryRegression('test_gallery_covers_all_background_flows').test_gallery_covers_all_background_flows()
 def test_selection_no_longer_closes_must_fail_historical_contract(self):
  needle='onSelect={id=>{onSelect(id);setOpen(false)}}'
  self.assertIn(needle,history.UI)
  with patch.object(history,'UI',history.UI.replace(needle,'onSelect={onSelect}')):
   with self.assertRaises(AssertionError):
    history.AssetLibraryRegression('test_gallery_covers_all_background_flows').test_gallery_covers_all_background_flows()

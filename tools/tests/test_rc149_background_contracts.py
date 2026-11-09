"""RC149: preserve the RC110 assertions while allowing independent phone backgrounds."""
from pathlib import Path
import unittest

from tools.tests.test_rc110_background_cloud_answer import mobile_background_routing_contract

ROOT = Path(__file__).resolve().parents[2]
MAIN = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


class RC149BackgroundContracts(unittest.TestCase):
    def test_background_contract_is_device_aware(self):
        self.assertTrue(mobile_background_routing_contract(MAIN))

    def test_unconditional_desktop_asset_is_rejected(self):
        wrong = MAIN.replace(
            "backgroundAssetId={canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':slideBackground({backgroundAssetId:questionBackgroundAsset||undefined,backgroundUrl:questionBackground||undefined},snap.session.theme).assetId||''}",
            'backgroundAssetId={questionBackgroundAsset}', 1)
        self.assertNotEqual(wrong, MAIN)
        self.assertFalse(mobile_background_routing_contract(wrong))

    def test_mobile_upload_cannot_overwrite_desktop_background(self):
        wrong = MAIN.replace(
            "onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')}",
            'onBackgroundUpload={file=>uploadBackground(file,false)}', 1)
        self.assertNotEqual(wrong, MAIN)
        self.assertFalse(mobile_background_routing_contract(wrong))

    def test_background_mobile_color_uses_isolated_draft(self):
        self.assertIn('onBackgroundColorChange={color=>setMobileLayoutDraft(', MAIN)
        self.assertIn('backgroundAssetId:undefined', MAIN)

    def test_workflow_keeps_historical_and_current_inventory(self):
        self.assertIn('tools/verify_rc_cycle148_inventory.py --historical', WORKFLOW)
        self.assertIn('tools/verify_rc_cycle149_inventory.py', WORKFLOW)
        self.assertIn('tools.tests.test_rc149_background_contracts', WORKFLOW)
        self.assertLess(WORKFLOW.index('test_rc149_background_contracts'), WORKFLOW.index('npm ci --ignore-scripts'))


if __name__ == '__main__':
    unittest.main()

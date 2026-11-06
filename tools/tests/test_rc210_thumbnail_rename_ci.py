"""RC210: the legacy rename check must follow the selection-aware editor path.

This suite runs before npm, PostgreSQL, and Chromium. It does not replace
browser verification, but rejects a rename refactor that silently stops
calling the authorized title-only API for selected thumbnails.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WEB = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
LEGACY = (ROOT / 'tools/tests/test_page_rename_preview_contract_20261027.py').read_text(encoding='utf8')


def rename_batch_body(source: str) -> str:
    match = re.search(
        r'async function renameSelectedPages\(fallbackId\?:string\)\s*\{(.*?)\n\}\s*function openThumbnailMenu\(',
        source, re.S,
    )
    if not match:
        raise AssertionError('selection-aware thumbnail rename handler missing')
    block = match.group(1)
    if not re.search(r'orderedSelectedPageIds\(snapshot\.activities', block):
        raise AssertionError('rename no longer follows persisted page order')
    if not re.search(r'for\s*\(const id of ids\)\s*\{.*?await renameCanvasPage\(page\)', block, re.S):
        raise AssertionError('selected pages no longer call the single-page authorized rename')
    return block


class RC210ThumbnailRenameCI(unittest.TestCase):
    def test_single_and_multi_page_paths_preserved(self):
        rename_batch_body(WEB)
        self.assertRegex(WEB, r'async function renameCanvasPage\(page:Activity\)')
        self.assertIn('onRenamePage={renameCurrentCanvasPage}', WEB)
        self.assertIn('void renameSelectedPages(a.id)', WEB)
        self.assertIn("if(action==='rename')void renameSelectedPages()", WEB)
        self.assertIn("/pages/${page.id}/title`,'PATCH'", WEB)
        self.assertIn('setSnap(old=>old?{...old,activities:old.activities.map(', WEB)

    def test_original_direct_call_contract_reconciled(self):
        # Do not re-introduce an assertion tied to pre-RC206 inline JSX.
        self.assertNotIn("self.assertIn('void renameCanvasPage(a)'", LEGACY)
        self.assertIn("self.assertIn('void renameSelectedPages(a.id)',UI)", LEGACY)
        self.assertIn("self.assertIn('if(page)await renameCanvasPage(page)',UI)", LEGACY)

    def test_deleting_the_delegation_fails_closed(self):
        damaged = WEB.replace('if(page)await renameCanvasPage(page)', 'if(page)void page', 1)
        self.assertNotEqual(damaged, WEB)
        with self.assertRaisesRegex(AssertionError, 'no longer call'):
            rename_batch_body(damaged)


if __name__ == '__main__':
    unittest.main()

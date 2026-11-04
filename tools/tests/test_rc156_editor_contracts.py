"""RC156: source contracts must follow device-aware editor without weakening checks.

The full Python suite in GitHub run 41720825704 stopped at three literal
substring expectations after all PostgreSQL/Chromium acceptance. These tests
are designed to detect real regressions through deliberate negative mutations.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

def device_background_contract(source: str) -> bool:
    return all(x in source for x in (
        "onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')}",
        "backgroundAssetId={canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':slideBackground({backgroundAssetId:questionBackgroundAsset||undefined,backgroundUrl:questionBackground||undefined},snap.session.theme).assetId||''}",
        "if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}",
        "else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}",
    ))

def page_isolation_contract(source: str) -> bool:
    return all(x in source for x in (
        '<WidgetCanvas key={`${selected}:${designActivity}:${canvasDevice}`}',
        "widgets={canvasDevice==='phone'?mobilePageWidgets(pageWidgets,mobileLayoutDraft):pageWidgets}",
        "mobileMode={canvasDevice==='phone'}",
    ))

def preview_draft_contract(source: str) -> bool:
    return all(x in source for x in (
        'snapshot={{...snap,activities:snap.activities.map(a=>a.id===designActivity?',
        'widgets:pageWidgets,mobile:mobileLayoutDraft,backgroundColor:questionBackgroundColor',
        'backgroundAssetId:questionBackgroundAsset',
        'initialPageId={designActivity}',
    ))

class RC156Regression(unittest.TestCase):
    def test_live_source_matches_three_contracts(self):
        self.assertTrue(device_background_contract(SOURCE))
        self.assertTrue(page_isolation_contract(SOURCE))
        self.assertTrue(preview_draft_contract(SOURCE))
    def test_background_mutations_fail_closed(self):
        for original,changed in (
            ("uploadBackground(file,false,canvasDevice==='phone')",'uploadBackground(file,false)'),
            ("canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':slideBackground({backgroundAssetId:questionBackgroundAsset||undefined,backgroundUrl:questionBackground||undefined},snap.session.theme).assetId||''", 'questionBackgroundAsset'),
            ('if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}', 'if(forMobile){}'),
        ):
            self.assertIn(original,SOURCE)
            self.assertFalse(device_background_contract(SOURCE.replace(original,changed,1)))
    def test_canvas_identity_mutations_fail_closed(self):
        for original,changed in (
            ('${selected}:${designActivity}:${canvasDevice}', '${selected}:${designActivity}'),
            ("canvasDevice==='phone'?mobilePageWidgets(pageWidgets,mobileLayoutDraft):pageWidgets",'pageWidgets'),
            ("mobileMode={canvasDevice==='phone'}",'mobileMode={false}'),
        ):
            self.assertIn(original,SOURCE)
            self.assertFalse(page_isolation_contract(SOURCE.replace(original,changed,1)))
    def test_preview_mutations_fail_closed(self):
        for original,changed in (
            ('widgets:pageWidgets,mobile:mobileLayoutDraft,backgroundColor:questionBackgroundColor',
             'widgets:pageWidgets,backgroundColor:questionBackgroundColor'),
            ('snapshot={{...snap,activities:snap.activities.map(a=>a.id===designActivity?', 'snapshot={snap}'),
            ('initialPageId={designActivity}', 'initialPageId={undefined}'),
        ):
            self.assertIn(original,SOURCE)
            self.assertFalse(preview_draft_contract(SOURCE.replace(original,changed,1)))
    def test_workflow_runs_the_three_historical_checks_early(self):
        early=WORKFLOW.index('Validate active RC release headers')
        integration=WORKFLOW.index('Kubernetes wizard and worker integration tests')
        for name in ('test_canvas_background_native_context',
                     'test_editor_page_isolation',
                     'test_rc_rehearsal_unique_mount_20261028',
                     'test_rc156_editor_contracts'):
            self.assertIn(name, WORKFLOW[early:integration])

if __name__=='__main__': unittest.main()

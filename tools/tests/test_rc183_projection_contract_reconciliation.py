"""RC183: current cross-surface contracts, not historical source spellings.

The full Python discovery CI gate used to fail *after* authenticated Chromium
and PostgreSQL because four older tests expected removed inline expressions.
These guards verify the newer shared policy and public media fence, including
negative mutations, before npm/Chromium/PostgreSQL in subsequent runs.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
POLICY = (ROOT/'apps/web/src/live-slide-policy.ts').read_text(encoding='utf-8')
BACKGROUNDS = (ROOT/'apps/web/src/master-background.ts').read_text(encoding='utf-8')
SERVER = (ROOT/'apps/api/src/server.ts').read_text(encoding='utf-8')


def rating_policy(ui: str, policy: str) -> bool:
    return all(x in ui for x in (
        'function RatingStageContent(',
        'widgetTitleVisible(widget)&&<strong>',
        "w.kind==='rating'?{...w,showTitle:editing===w.id?false:w.showTitle}",
        'data-show-title={widgetTitleVisible(w)}',
    )) and all(x in policy for x in (
        'export function widgetTitleVisible(',
        'return widget.showTitle !== false',
    )) and ui.count('<RatingChoices') == 1 and ui.count('<RatingCommentField') == 1


def reading_policy(ui: str, policy: str) -> bool:
    return all(x in ui for x in (
        'aria-pressed={!participantReadingMode&&!audiencePortrait}',
        'aria-pressed={!!audiencePortrait}',
        'aria-pressed={participantReadingMode}',
        'participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets',
        'backgroundImage:"none",backgroundColor:"#ffffff"',
    )) and all(x in policy for x in (
        'export function participantVisibleWidgets',
        'export function participantReadingWidgets',
        "a.widget.kind === 'footer'",
        '!PRESENTER_ONLY_WIDGETS.has(widget.kind)',
    ))


def public_media_policy(ui: str, backgrounds: str, server: str) -> bool:
    return all(x in ui for x in (
        'slideBackgroundCss(entry.activity.page_design,entry.theme,id=>',
        'media/${encodeURIComponent(id)}`)',
        'media/${encodeURIComponent(w.assetId)}`}',
    )) and all(x in backgrounds for x in (
        'if(page?.backgroundAssetId)return {assetId:page.backgroundAssetId}',
        'if(theme?.master?.backgroundAssetId)return {assetId:theme.master.backgroundAssetId}',
        'assetUrl(chosen.assetId)',
    )) and all(x in server for x in (
        "app.get('/api/join/:code/activities/:aid/media/:assetId'",
        'current_activity_id!==req.params.aid',
    ))


class RC183ProjectionContracts(unittest.TestCase):
    def test_rating_and_reaction_heading_policy(self):
        self.assertTrue(rating_policy(UI, POLICY))
        self.assertEqual(UI.count('<ReactionChoices'), 3)
        self.assertIn("['reactions','results-button'].includes(w.kind)?{...w,showTitle:false}:w", UI)

    def test_rating_double_heading_mutation_is_detected(self):
        altered = UI.replace('widgetTitleVisible(widget)&&<strong>', 'true&&<strong>', 1)
        self.assertNotEqual(altered, UI)
        self.assertFalse(rating_policy(altered, POLICY))

    def test_three_modes_are_independent_and_results_private(self):
        self.assertTrue(reading_policy(UI, POLICY))

    def test_phone_and_reading_mutations_are_detected(self):
        altered = UI.replace('aria-pressed={!!audiencePortrait}',
                             'aria-pressed={participantReadingMode}', 1)
        self.assertNotEqual(altered, UI)
        self.assertFalse(reading_policy(altered, POLICY))
        altered_policy = POLICY.replace('!PRESENTER_ONLY_WIDGETS.has(widget.kind)', 'true', 1)
        self.assertNotEqual(altered_policy, POLICY)
        self.assertFalse(reading_policy(UI, altered_policy))

    def test_public_background_media_uses_scoped_asset_routes(self):
        self.assertTrue(public_media_policy(UI, BACKGROUNDS, SERVER))

    def test_unscoped_background_mutation_is_detected(self):
        altered = UI.replace('media/${encodeURIComponent(id)}`)', 'media/${id}`)', 1)
        self.assertNotEqual(altered, UI)
        self.assertFalse(public_media_policy(altered, BACKGROUNDS, SERVER))


if __name__=='__main__':
    unittest.main()

"""RC203: reject the RC200 two-row grid regression before Chromium or npm.

CI #42107111552: 140px wrapped catalog placed in a ~123px rail,
and the stage overflowed by a pixel on desktop. Keep the second, auto-sized
palette row even when the compact title/primary-owner header grows.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
BROWSER = (ROOT / 'tools/ci_editor_mock_layout_chromium.py').read_text(encoding='utf8')
MARKER = '/* RC200/RC203: title and owner stay below the actions; preserve three editor grid rows.'
ROWS = (
 'grid-template-rows:minmax(88px,auto) minmax(72px,auto) minmax(0,1fr)!important',
 'grid-template-rows:minmax(118px,auto) minmax(72px,auto) minmax(0,1fr)!important',
 'grid-template-rows:minmax(158px,auto) minmax(72px,auto) minmax(0,1fr)!important',
)


def verify_tracks(css: str) -> None:
    if MARKER not in css:
        raise AssertionError('compact header section is missing')
    rules = css.split(MARKER, 1)[-1]
    for track in ROWS:
        if track not in rules:
            raise AssertionError('palette grid track is missing: ' + track)
    if 'grid-template-rows:minmax(88px,auto) minmax(0,1fr)!important' in rules:
        raise AssertionError('legacy two-row desktop override clips catalog')
    if 'max-width:min(100%,calc((100dvh - 280px)*16/9))!important' not in css:
        raise AssertionError('desktop slide lacks sufficient height reserve')


class RC203EditorGridTrack(unittest.TestCase):
    def test_current_header_and_palette_track_cascade(self):
        verify_tracks(CSS)
        self.assertIn('editor-mock-action-buttons', CSS)
        self.assertIn('editor-mock-meta', CSS)

    def test_old_two_row_header_override_is_rejected(self):
        broken = CSS.replace(ROWS[0], 'grid-template-rows:minmax(88px,auto) minmax(0,1fr)!important')
        with self.assertRaises(AssertionError):
            verify_tracks(broken)

    def test_short_viewport_canvas_overflow_is_rejected(self):
        broken = CSS.replace('calc((100dvh - 280px)*16/9)', 'calc((100dvh - 240px)*16/9)')
        with self.assertRaises(AssertionError):
            verify_tracks(broken)

    def test_preflight_and_real_browser_are_both_required(self):
        self.assertIn('tools.tests.test_rc203_editor_grid_track', CI)
        self.assertIn('python3 tools/ci_editor_mock_layout_chromium.py', CI)
        self.assertIn('(960,760,False)', BROWSER)
        self.assertIn('(390,844,True)', BROWSER)
        self.assertIn("gb['y']+gb['height']<=rb['y']+rb['height']+2", BROWSER)


if __name__ == '__main__':
    unittest.main()

"""RC130: browser media-picker and autosave accept the restored editor, not a hidden dashboard."""
import ast
import asyncio
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL = (ROOT / 'tools/ci_browser_editor_postgres.py').read_text(encoding='utf-8')
MEDIA = (ROOT / 'tools/ci_browser_media_picker_postgres.py').read_text(encoding='utf-8')
SID = '01234567-89ab-4cde-8012-3456789abcde'
AID = '01234567-89ab-4cde-9012-3456789abcde'
TITLE = 'CI real browser JPG backgrounds and logo picker'

class FakeNotice:
    async def is_visible(self): return False

class FakeContext:
    async def cookies(self): return [{'name': 'q_cookie_notice'}]

class FakeEditor:
    def locator(self, selector):
        assert selector == '.page-editor-thumb-row.is-active .page-editor-thumb'
        return object()
    def get_by_role(self, role, name=None):
        assert role == 'group' and name == 'Canvas grafico widget'
        return object()

class FakePage:
    context = FakeContext()
    def __init__(self, state):
        self.state = state
        self.visits = []
        self.editor = FakeEditor()
        self.dashboard_click_requested = False
    async def goto(self, url, wait_until):
        assert wait_until == 'domcontentloaded'
        self.visits.append(url)
    async def evaluate(self, expression):
        assert 'sessionStorage.getItem' in expression
        return self.state
    def get_by_role(self, role, name=None):
        if role == 'dialog' and name == 'Informativa cookie funzionali':
            return FakeNotice()
        if role == 'region' and name == 'Editor grafico delle pagine':
            return self.editor
        self.dashboard_click_requested = True
        raise AssertionError(f'restored editor must not click background dashboard: {role}/{name}')

class FakeButton:
    def __init__(self, clicks, name): self.clicks, self.name = clicks, name
    @property
    def first(self): return self
    async def wait_for(self): pass
    async def click(self): self.clicks.append(self.name)

class FakeSessionCard:
    def __init__(self, clicks): self.clicks = clicks
    def filter(self, **kwargs): return self
    def locator(self, selector):
        assert selector == 'summary'
        return FakeButton(self.clicks, 'summary')
    def get_by_role(self, role, name=None):
        assert role == 'button' and name == 'Apri sessione'
        return FakeButton(self.clicks, 'card-open')

class FakeFreshPage(FakePage):
    def __init__(self):
        super().__init__(None)
        self.clicks = []
    def get_by_text(self, text, exact=False):
        assert text == TITLE and exact
        return object()
    def locator(self, selector):
        assert selector == 'details'
        return FakeSessionCard(self.clicks)
    def get_by_role(self, role, name=None):
        if role == 'button' and name == 'Apri sessione':
            return FakeButton(self.clicks, 'dashboard-open')
        if role == 'button' and name == '✎ Modifica le pagine':
            return FakeButton(self.clicks, 'open-editor')
        if role == 'group' and name == 'Canvas grafico widget':
            return object()
        return super().get_by_role(role, name)

class FakeExpect:
    def __init__(self, target, seen): self.target, self.seen = target, seen
    async def to_be_visible(self, **kwargs): self.seen.append('visible')
    async def to_have_count(self, count):
        assert count == 1
        self.seen.append('count')
    async def to_have_attribute(self, name, value):
        assert name == 'aria-current' and value == 'page'
        self.seen.append('current')

class RestoredEditorAcceptance(unittest.TestCase):
    @staticmethod
    def run_case(state):
        node = next(n for n in ast.parse(REAL).body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'open_editor')
        seen, reads = [], []
        async def call(context, method, path):
            reads.append((method, path))
            return {'session': {'title': TITLE}, 'activities': [{'id': AID}]}
        scope = {'BASE': 'http://127.0.0.1:8080', 'call': call, 'expect': lambda target: FakeExpect(target, seen)}
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<real-open-editor>', 'exec'), scope)
        page = FakePage(state)
        asyncio.run(scope['open_editor'](page, TITLE, session_id=SID, activity_id=AID))
        return page, seen, reads

    def test_new_session_still_uses_genuine_dashboard_opening(self):
        node = next(n for n in ast.parse(REAL).body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'open_editor')
        seen = []
        scope = {'BASE': 'http://127.0.0.1:8080', 'expect': lambda target: FakeExpect(target, seen)}
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<real-open-editor>', 'exec'), scope)
        page = FakeFreshPage()
        asyncio.run(scope['open_editor'](page, TITLE, session_id=SID, activity_id=AID))
        self.assertEqual(page.clicks, ['dashboard-open', 'summary', 'card-open', 'open-editor'])
        self.assertEqual(seen, ['visible'])

    def test_restored_page_stays_open_and_validates_server_identity(self):
        page, seen, reads = self.run_case({'sessionId': SID, 'pageId': AID, 'section': 'session', 'tab': 'pages'})
        self.assertEqual(page.visits, ['http://127.0.0.1:8080/'])
        self.assertFalse(page.dashboard_click_requested)
        self.assertEqual(reads, [('GET', f'/api/sessions/{SID}')])
        self.assertEqual(seen, ['visible', 'count', 'current', 'visible'])

    def test_recovered_different_session_is_rejected_not_clicked(self):
        with self.assertRaisesRegex(AssertionError, 'different session'):
            self.run_case({'sessionId': 'other', 'pageId': AID})

    def test_recovered_different_page_is_rejected_not_clicked(self):
        with self.assertRaisesRegex(AssertionError, 'different page'):
            self.run_case({'sessionId': SID, 'pageId': 'other'})

    def test_both_real_postgres_flows_check_reentry_after_reload(self):
        self.assertIn('await open_editor(page, title, session_id=sid, activity_id=aid)', MEDIA)
        self.assertIn('await open_editor(page,title,session_id=sid,activity_id=aid)', REAL)
        self.assertEqual(REAL.count('await open_editor(page,title,session_id=sid,activity_id=aid)'), 2)
        self.assertNotIn('force=True', REAL)
        self.assertNotIn('force=True', MEDIA)
        self.assertIn('await expect(current).to_have_attribute(\'aria-current\',\'page\')', REAL)
        self.assertIn("await call(page.context,'GET',f'/api/sessions/{session_id}')", REAL)

if __name__ == '__main__': unittest.main()

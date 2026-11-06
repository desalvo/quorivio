"""Dependency-free RC206 release contracts for page selection, footer numbering,
long choice options, library ownership and viewport-safe menus."""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class RC206EditorContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.web=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.css=(ROOT/'apps/web/src/style.css').read_text()
        cls.api=(ROOT/'apps/api/src/server.ts').read_text()
        cls.domain=(ROOT/'apps/api/src/domain.ts').read_text()
        cls.sql=(ROOT/'apps/api/src/schema.sql').read_text()
        cls.seq=(ROOT/'apps/web/src/page-thumbnail-selection.ts').read_text()

    def test_page_shortcuts_are_scoped_to_thumbnail_focus(self):
        self.assertIn("thumbnailShortcut(event,focusInThumbnails)",self.web)
        self.assertIn(".page-editor-thumbnails,.page-editor-thumb-menu-floating",self.web)
        self.assertIn("if(event.defaultPrevented||target?.closest('input,textarea,select",self.web)
        for code in ('duplicateSelectedPages','renameSelectedPages','deleteSelectedPages'):
            self.assertIn(code+'()',self.web)
        self.assertIn("event.key==='Backspace'",self.seq)
        self.assertIn("event.key.toLowerCase()==='d'",self.seq)
        self.assertIn("event.key.toLowerCase()==='r'",self.seq)

    def test_multi_selection_and_safe_server_operations(self):
        self.assertIn('choosePageIds(v,a.id,true)',self.web)
        self.assertIn('duplicatePageOrder(original,copies)',self.web)
        self.assertIn('window.confirm(`Eliminare definitivamente ${ids.length}',self.web)
        self.assertIn("/pages/${id}`,'DELETE'",self.web)
        self.assertIn("/pages/order`,'PUT'",self.web)

    def test_thumbnail_portal_is_viewport_bounded(self):
        self.assertIn('page-editor-thumb-menu-floating',self.web)
        self.assertIn('</div>,document.body)',self.web)
        self.assertIn('max-height:calc(100dvh - 16px)!important',self.css)
        self.assertIn('overflow:auto!important',self.css)

    def test_255_choice_limits_are_consistent(self):
        self.assertGreaterEqual(self.web.count('maxLength={255}'),3)
        self.assertGreaterEqual(self.domain.count('label.length<=255'),3)
        self.assertNotIn('label.length<=160',self.domain)

    def test_presenter_number_is_publicly_identical_in_live_and_http(self):
        self.assertIn('presenter_page_number:presenterNumber',self.api)
        self.assertIn('presenter_page_number:pageIndex>=0?pageIndex+1:1',self.api)
        self.assertIn('slidePageNumber(activities,activity.id)',self.web)
        self.assertIn('entry.session.presenter_page_number',self.web)

    def test_background_image_mutations_enforce_owner_and_in_use(self):
        self.assertIn("app.patch('/api/sessions/:id/backgrounds/:bid'",self.api)
        self.assertIn("app.delete('/api/sessions/:id/backgrounds/:bid'",self.api)
        self.assertIn("AND owner_id=$2",self.api)
        self.assertIn("error:'background_in_use'",self.api)
        self.assertIn('source_background_id',self.api)
        self.assertIn('source_background_id uuid REFERENCES presenter_backgrounds(id)',self.sql)
        self.assertIn('position(sa.id::text in coalesce(s.theme::text',self.api)
        self.assertIn('sa.source_background_id IS NULL AND sa.uploaded_by=$2',self.api)
        self.assertIn('position(sa.id::text in coalesce(a.result_design::text',self.api)
        self.assertIn('onRenameLibraryImage={renameLibraryImage}',self.web)
        self.assertIn('onDeleteLibraryImage={deleteLibraryImage}',self.web)

    def test_result_bar_counts_have_separate_accessible_style(self):
        self.assertIn('widget-results-bar-caption',self.web)
        self.assertIn('widget-results-bar-row',self.css)
        self.assertIn('linked-result-final output',self.css)

if __name__=='__main__':unittest.main()

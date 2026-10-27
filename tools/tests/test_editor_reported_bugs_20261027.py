"""Regression contracts for user-reported editor layout and save failures."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text()
CSS = (ROOT / 'apps/web/src/style.css').read_text()

class EditorReportedBugs(unittest.TestCase):
    def test_generated_widget_ids_fit_backend_limits(self):
        # The API validator rejects old `${kind}-${crypto.randomUUID()}` IDs for
        # topic-question, results-button and participant-count (>48 chars).
        self.assertNotRegex(UI, r'\$\{(?:k|kind|w\.kind)\}-\$\{crypto\.randomUUID\(\)\}')
        self.assertIn('id:crypto.randomUUID(),kind:k', UI)
        self.assertIn('id:crypto.randomUUID(),kind', UI)

    def test_save_confirms_authoritative_readback(self):
        self.assertIn('const refreshed=await request<Snapshot>', UI)
        self.assertIn('stableJson(persisted.page_design?.widgets||[])', UI)
        self.assertIn('setNotice(`Salvataggio non riuscito:', UI)
        self.assertIn('editor-save-feedback', UI)
        self.assertIn('unconfiguredMedia', UI)

    def test_canvas_fills_middle_column(self):
        self.assertIn('grid-template-columns:clamp(120px,14vw,205px) minmax(0,1fr)', CSS)
        self.assertIn('.editor-ux-v2 .canvas-editor-group{width:100%;max-width:none;', CSS)
        self.assertIn('aspect-ratio:16/9', CSS)

    def test_no_native_duplicate_tooltip_and_menu_overlap(self):
        self.assertIn('className="editor-icon-tool" data-widget-kind={kind} aria-label={label}', UI)
        self.assertIn('data-tools-open={arrangeMenu}', UI)
        self.assertIn('Strumenti di selezione e allineamento', UI)
        self.assertIn('.page-editor-sidebar:has(.page-editor-thumb-menu){z-index:120', CSS)

    def test_geometry_and_question_editing(self):
        self.assertIn('freeWidgetPosition(old,{x:4+(i%4)*24,y:4+Math.floor(i/4)*24},22,20)', UI)
        self.assertIn("['question','timed-quiz','topic-question'].includes(w.kind)", UI)
        self.assertIn('data-rotate-handle', UI)
        self.assertIn('data-resize-edge', UI)
        self.assertIn('canvas-widget-answer-preview', UI)

if __name__=='__main__': unittest.main()

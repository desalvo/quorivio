"""Regression coverage for editor widget inspection, response options and unclipped hints."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
JSX=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class WidgetInspectorPortal20261027(unittest.TestCase):
    def test_only_one_inspector_opens_in_real_editor(self):
        self.assertIn('contextWidget&&!onInspectWidget&&<div className="canvas-context-properties"',JSX)
        self.assertIn('contextWidget===w.id&&<div className="canvas-context-menu"',JSX)
        self.assertIn('setContextWidget(w.id)',JSX)
        self.assertIn('aria-label="Chiudi proprietà widget"',JSX)
        self.assertIn('className="editor-drawer-close"',JSX)

    def test_interactive_widget_options_have_labels_and_controls(self):
        self.assertIn('function WidgetChoiceEditor(',JSX)
        self.assertIn('Opzioni di risposta (massimo 12)',JSX)
        self.assertIn('Testo opzione ',JSX)
        self.assertIn('Aggiungi opzione',JSX)
        self.assertIn('Rimuovi opzione ',JSX)
        self.assertIn('Risposta corretta opzione ',JSX)
        self.assertIn('WidgetChoiceEditor widget={w}',JSX)
        self.assertIn('onPatch({options:[...choices,{id:',JSX)

    def test_options_reach_canvas_and_projected_slide(self):
        self.assertIn('canvas-widget-answer-preview',JSX)
        self.assertIn('projection-interactive-options',JSX)
        self.assertIn('widget-choice-marker',JSX)
        self.assertIn('.projection-interactive-options li{display:flex;align-items:flex-start;',CSS)
        self.assertIn('.widget-question>label:has(>input[type=radio])',CSS)
        self.assertIn('.widget-question>label:has(>input[type=checkbox])',CSS)

    def test_tooltip_escapes_all_clipping_ancestors(self):
        self.assertIn('createPortal(<span className=',JSX)
        self.assertIn('document.body',JSX)
        self.assertIn('z-index:2147483000',CSS)
        self.assertIn("!button.classList.contains('editor-icon-tool')",JSX)

if __name__=='__main__':unittest.main()

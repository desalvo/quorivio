"""RC242 early CI guard: authoring fonts, compact master commands, universal zoom."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]

class RC242ArialMasterZoom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=(ROOT/'apps/web/src/main.tsx').read_text()
        cls.css=(ROOT/'apps/web/src/style.css').read_text()
        cls.zoom=(ROOT/'apps/web/src/global-page-zoom.ts').read_text()

    def test_widget_font_defaults_are_arial_without_mutating_custom_faces(self):
        typography=(ROOT/'apps/web/src/widget-typography-defaults.ts').read_text()
        appearance=(ROOT/'apps/web/src/widget-appearance.ts').read_text()
        self.assertIn("fontFamily:safeWidgetFontFamily(style?.fontFamily)",typography)
        self.assertIn("answerFontFamily:safeWidgetFontFamily(style?.answerFontFamily,safeWidgetFontFamily(style?.fontFamily))",typography)
        self.assertIn("fontFamily:safeWidgetFontFamily(style?.fontFamily)",appearance)
        self.assertIn('font-family:inherit;',self.css)
        self.assertIn('RC242: the application theme',self.css)
        self.assertIn('initialWidgetTextStyle(kind)',self.main)
        self.assertIn('widgetTypographyStyle(w.kind===',self.main)

    def test_scheme_save_is_always_accessible_without_second_ribbon_row(self):
        self.assertIn('slide-scheme-ribbon-save',self.main)
        self.assertIn('flex-wrap:nowrap!important',self.css)
        self.assertIn('position:sticky!important;right:0!important',self.css)
        self.assertIn('min-height:39px!important',self.css)

    def test_zoom_is_app_wide_not_editor_only_and_has_accessible_buttons(self):
        self.assertIn('function GlobalPageZoomShell()',self.main)
        self.assertIn('<WorkspaceErrorBoundary/>',self.main)
        self.assertIn('<GlobalPageZoomShell/>',self.main)
        self.assertIn("root.style.setProperty('zoom',value)",self.main)
        self.assertIn('aria-label="Aumenta zoom dell\'interfaccia"',self.main)
        self.assertIn('aria-label="Riduci zoom dell\'interfaccia"',self.main)
        self.assertIn('Ripristina zoom al 100%',self.main)
        self.assertIn('window.localStorage.setItem',self.main)
        self.assertIn('GLOBAL_ZOOM_STORAGE_KEY',self.zoom)

    def test_preserves_custom_font_controls_and_existing_page_decorations(self):
        self.assertIn('fontFamily:e.target.value',self.main)
        self.assertIn('onClick={()=>void saveSchemaEditor()}',self.main)
        self.assertIn('slide-scheme-ribbon-icon',self.css)

if __name__=='__main__':unittest.main()

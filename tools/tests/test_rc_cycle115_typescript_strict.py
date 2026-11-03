"""RC115: fail-closed contracts for the TS errors reported by full CI RC114.

This preflight is intentionally dependency-free; the strict TypeScript/Vite build
remains mandatory and independently validates the real program.
"""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def autofit_types(source: str) -> bool:
    block=source[source.index(' // Automatic content sizing is the default.'):source.index(' const patch=(id:string',source.index(' // Automatic content sizing is the default.'))]
    return all(x in block for x in (
        'const current: any[]=changes??widgets;',
        'const proposal:any[]=current.map((z:any)=>',
        'const accepted:any[]=rejectWidgetCollisions(current,proposal,[w.id]);',
        'if(accepted.find(z=>z.id===w.id)?.position?.height>p.height+.1)changes=accepted;',
    )) and 'const current=changes||widgets' not in block


def editor_types(source: str, domain: str) -> bool:
    marker='type EditorWidgetPermissionFields = Pick<NonNullable<PageDesign[\'widgets\']>[number],'
    if marker not in source:return False
    declaration=source[source.index(marker):source.index(';',source.index(marker))]
    if not all(re.search(r"\b'"+name+r"'\b", declaration) or "'"+name+"'" in declaration for name in ('autoFit','showTitle')): return False
    for key in ('autoFit?:boolean','showTitle?:boolean'):
        if key not in domain: return False
    return True


def graphic_type_narrowing(source: str, domain: str) -> bool:
    for property in ('shapeType','lineDirection','strokeDash'):
        expected=property+":e.target.value as WidgetTextStyle['"+property+"']"
        if expected not in source: return False
        if property+"?:'" not in domain:return False
        if property+':e.target.value}}:z))' in source:return False
    return True

class RC115StrictTypeContracts(unittest.TestCase):
    def test_autofit_collision_arrays_have_explicit_types(self):
        self.assertTrue(autofit_types(UI))
    def test_page_editor_widget_fields_are_inferred_from_shared_domain(self):
        self.assertTrue(editor_types(UI,DOMAIN))
    def test_graphic_options_use_exact_domain_unions(self):
        self.assertTrue(graphic_type_narrowing(UI,DOMAIN))
    def test_negative_mutations_reject_original_compiler_errors(self):
        self.assertFalse(autofit_types(UI.replace('const current: any[]=changes??widgets;','const current=changes||widgets;',1)))
        self.assertFalse(editor_types(UI.replace(" | 'showTitle' | 'autoFit' | 'resultsOnly'>;", ">;",1),DOMAIN))
        self.assertFalse(graphic_type_narrowing(UI.replace("shapeType:e.target.value as WidgetTextStyle['shapeType']",'shapeType:e.target.value',1),DOMAIN))
        self.assertFalse(graphic_type_narrowing(UI.replace("lineDirection:e.target.value as WidgetTextStyle['lineDirection']",'lineDirection:e.target.value',1),DOMAIN))
        self.assertFalse(graphic_type_narrowing(UI.replace("strokeDash:e.target.value as WidgetTextStyle['strokeDash']",'strokeDash:e.target.value',1),DOMAIN))
    def test_preflight_and_strict_build_remain_mandatory(self):
        self.assertIn('test_rc_cycle115_typescript_strict',CI)
        self.assertLess(CI.index('test_rc_cycle115_typescript_strict'),CI.index('npm install --ignore-scripts'))
        self.assertIn('npm run build',CI)
        self.assertIn('tsc --noEmit && vite build',(ROOT/'apps/web/package.json').read_text())
        self.assertIn('"strict":true',(ROOT/'apps/web/tsconfig.json').read_text().replace(' ',''))

if __name__=='__main__': unittest.main()

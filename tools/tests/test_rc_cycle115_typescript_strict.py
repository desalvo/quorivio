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
    """RC326: legacy geometry-growth arrays are gone. Verify the current
    strictly typed proportional fit and that it cannot mutate widget bounds.
    Keep this a mutation-sensitive contract; the mandatory tsc/Vite build
    independently enforces actual TypeScript correctness.
    """
    marker='function WidgetContentFit({'
    if marker not in source or 'type DiskVolumeStatus=' not in source:
        return False
    block=source.split(marker,1)[1].split('type DiskVolumeStatus=',1)[0]
    implementation=(ROOT/'apps/web/src/widget-content-scale.ts').read_text()
    return all(x in block for x in (
        'const frame=useRef<HTMLDivElement>(null),body=useRef<HTMLDivElement>(null);',
        'const a=frame.current,b=body.current',
        'const next=proportionalWidgetScale({',
        'frameWidth:a.clientWidth,frameHeight:a.clientHeight',
        'contentWidth:Math.max(b.scrollWidth,b.clientWidth)',
        'contentHeight:Math.max(b.scrollHeight,b.clientHeight)',
        'setFactor(previous=>',
    )) and all(x in implementation for x in (
        'export type FitDimensions=',
        'export function proportionalWidgetScale(d:FitDimensions):number',
    )) and 'autoFitExpandedPosition(' not in source and 'rejectWidgetCollisions(current,proposal,[w.id])' not in block


def editor_permission_fields(source: str) -> set[str] | None:
    """Extract the actual Pick<> union instead of relying on old field order.

    RC150 appended new persisted fields after ``resultsOnly``. A test based on
    the previous exact suffix silently mutated nothing and falsely failed CI.
    """
    match=re.search(
        r"type\s+EditorWidgetPermissionFields\s*=\s*"
        r"Pick<NonNullable<PageDesign\['widgets'\]>\[number\],\s*([^;]+)>\s*;",
        source,
    )
    if not match:
        return None
    declaration=match.group(1)
    fields=re.findall(r"'([^']+)'",declaration)
    # Disallow broadened unions or malformed content masquerading as a Pick.
    if not fields or not re.fullmatch(r"\s*'[^']+'(?:\s*\|\s*'[^']+')*\s*",declaration):
        return None
    if len(fields)!=len(set(fields)):
        return None
    return set(fields)


def editor_types(source: str, domain: str) -> bool:
    fields=editor_permission_fields(source)
    if fields is None or not {'autoFit','showTitle'}.issubset(fields):
        return False
    if not re.search(r'newWidgetHistory<.*?&\s*EditorWidgetPermissionFields>\(',source,re.S):
        return False
    for key in ('autoFit?:boolean','showTitle?:boolean'):
        if key not in domain:
            return False
    return True


def remove_editor_permission(source: str, field: str) -> str:
    """Delete a field from the real Pick union, whatever its neighbors."""
    marker="type EditorWidgetPermissionFields = Pick<NonNullable<PageDesign['widgets']>[number],"
    start=source.find(marker)
    if start<0:
        return source
    end=source.find(';',start)
    if end<0:
        return source
    original=source[start:end+1]
    replacement=re.sub(r"\s*\|\s*'"+re.escape(field)+r"'",'',original,count=1)
    if replacement==original:
        replacement=re.sub(r"'"+re.escape(field)+r"'\s*\|\s*",'',original,count=1)
    return source[:start]+replacement+source[end+1:]


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
        self.assertFalse(autofit_types(UI.replace('const next=proportionalWidgetScale({','const next=unsafeAutoFit({',1)))
        # Mutate the actual current union: RC150 extends it past resultsOnly.
        for field in ('showTitle','autoFit'):
            mutated=remove_editor_permission(UI,field)
            self.assertNotEqual(mutated,UI,f'negative mutation did not remove {field}')
            self.assertFalse(editor_types(mutated,DOMAIN),f'accepted missing {field}')
        self.assertFalse(graphic_type_narrowing(UI.replace("shapeType:e.target.value as WidgetTextStyle['shapeType']",'shapeType:e.target.value',1),DOMAIN))
        self.assertFalse(graphic_type_narrowing(UI.replace("lineDirection:e.target.value as WidgetTextStyle['lineDirection']",'lineDirection:e.target.value',1),DOMAIN))
        self.assertFalse(graphic_type_narrowing(UI.replace("strokeDash:e.target.value as WidgetTextStyle['strokeDash']",'strokeDash:e.target.value',1),DOMAIN))
    def test_preflight_and_strict_build_remain_mandatory(self):
        self.assertIn('test_rc_cycle115_typescript_strict',CI)
        self.assertLess(CI.index('test_rc_cycle115_typescript_strict'),CI.index('npm ci --ignore-scripts'))
        self.assertIn('npm run build',CI)
        self.assertIn('tsc --noEmit && vite build',(ROOT/'apps/web/package.json').read_text())
        self.assertIn('"strict":true',(ROOT/'apps/web/tsconfig.json').read_text().replace(' ',''))

if __name__=='__main__': unittest.main()

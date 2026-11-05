"""RC189: prevent the RC188 portable page-map TS2345 compilation failure.

Real npm-installed backend typechecking runs immediately after installation;
this early preflight also exercises the exact map-building source with Node 22.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SERVER = (ROOT / 'apps/api/src/server.ts').read_text(encoding='utf-8')
ROUTING = (ROOT / 'apps/api/src/presentation-routing.ts').read_text(encoding='utf-8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')


def portable_map_source(server: str) -> str:
    start = server.index('  const pageMap=new Map', server.index('async function createFromPortable('))
    end = server.index('  for(let i=0;i<definition.activities.length;i++){\n   const a=', start)
    return server[start:end]


def isolated_typescript(snippet: str) -> str:
    return """declare const definition: any;
declare const newIds: string[];
declare function remapPortablePageRouting(design: unknown, ids: ReadonlyMap<string,string>): unknown;
""" + snippet + "\nremapPortablePageRouting({}, pageMap);\n"


def compile_with_tsc(source: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix='quorivio-rc189-') as d:
        file = Path(d) / 'portable-map.ts'
        file.write_text(source, encoding='utf-8')
        # The isolated map fixture must not import ambient types from partially
        # installed workspace packages; the full API typecheck runs after npm.
        isolated_types = Path(d) / 'types'
        isolated_types.mkdir()
        return subprocess.run(
            ['tsc', '--strict', '--noEmit', '--target', 'ES2022', '--module', 'NodeNext',
             '--moduleResolution', 'NodeNext', '--skipLibCheck', '--typeRoots', str(isolated_types), str(file)],
            cwd=ROOT, text=True, capture_output=True, timeout=20, check=False)


class RC189PortableMapTypecheck(unittest.TestCase):
    def test_import_map_is_string_typed_and_drops_legacy_missing_ids(self):
        source = portable_map_source(SERVER)
        self.assertIn('new Map<string,string>()', source)
        self.assertIn('const oldId:unknown=definition.activities[i].portable_id;', source)
        self.assertIn("if(typeof oldId==='string')pageMap.set(oldId,newIds[i]);", source)
        self.assertIn('remapPortablePageRouting(a.page_design,pageMap)', SERVER)
        self.assertIn('remapPortablePageRouting(a.result_design,pageMap)', SERVER)
        self.assertIn('pageIds:ReadonlyMap<string,string>', ROUTING)

    def test_real_node_uses_exact_server_source_and_skips_undefined_id(self):
        source = portable_map_source(SERVER)
        code = """const definition={activities:[{portable_id:'old-question'},{portable_id:undefined},{portable_id:'old-results'}]};
const newIds=['new-question','new-legacy','new-results'];
""" + source + """
import assert from 'node:assert/strict';
assert.deepEqual([...pageMap], [['old-question','new-question'],['old-results','new-results']]);
assert.equal(pageMap.has(undefined),false);
assert.equal(pageMap.has('outside-session'),false);
"""
        with tempfile.TemporaryDirectory(prefix='quorivio-rc189-node-') as d:
            fixture = Path(d) / 'portable-map.mts'
            fixture.write_text(code, encoding='utf-8')
            result = subprocess.run(['node', '--experimental-strip-types', str(fixture)],
                                    cwd=ROOT, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_strict_ts_compile_and_negative_regression(self):
        if not shutil.which('tsc'):
            self.skipTest('standalone tsc not available before npm; mandatory API tsc follows npm install')
        good = compile_with_tsc(isolated_typescript(portable_map_source(SERVER)))
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        old = 'const pageMap=new Map(definition.activities.map((a:any,i:number)=>[a.portable_id,newIds[i]]));'
        broken = compile_with_tsc(isolated_typescript(old))
        self.assertNotEqual(broken.returncode, 0)
        self.assertIn('TS2345', broken.stdout + broken.stderr)

    def test_ci_runs_full_backend_typecheck_immediately_after_npm(self):
        early = WORKFLOW.index('test_rc189_portable_map_types')
        install = WORKFLOW.index('name: Install reproducibly')
        strict = WORKFLOW.index('name: RC189 strict API TypeScript typecheck before extended CI')
        unit = WORKFLOW.index('name: Unit tests')
        full = WORKFLOW.index('name: Compile frontend and backend')
        self.assertLess(early, install)
        self.assertLess(install, strict)
        self.assertLess(strict, unit)
        self.assertLess(strict, full)
        self.assertIn('run: ./node_modules/.bin/tsc --noEmit -p apps/api/tsconfig.json', WORKFLOW)


if __name__ == '__main__':
    unittest.main()

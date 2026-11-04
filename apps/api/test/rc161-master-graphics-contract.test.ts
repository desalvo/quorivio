import {test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {validPageDesign,validWidgetTextStyle} from '../src/domain.ts';
import {referencedAssets,remapPortableAssets} from '../src/portable-bundle.ts';
const masterId=randomUUID();
test('RC161 master image UUID and graphics styles are validated fail-closed',()=>{
 assert.equal(validPageDesign({master:{backgroundAssetId:masterId}}),true);
 assert.equal(validPageDesign({master:{backgroundAssetId:'data:image/svg+xml,bad'}}),false);
 assert.equal(validPageDesign({master:{backgroundAssetId:'x'.repeat(36)}}),false);
 assert.equal(validPageDesign({master:{backgroundAssetId:masterId,evil:'unknown'}}),false);
 for(const arrow of ['none','start','end','both'])assert.equal(validWidgetTextStyle({fontFamily:'Arial',strokeWidth:2,lineArrow:arrow}),true);
 assert.equal(validWidgetTextStyle({lineArrow:'unsupported'}),false);
 assert.equal(validWidgetTextStyle({strokeWidth:13}),false);
 assert.equal(validPageDesign({widgets:[{id:'line1',kind:'line',showTitle:false,label:'',style:{lineArrow:'both',strokeDash:'dash',strokeWidth:4}}]}),true);
});
test('RC161 portable bundle always includes global master backgrounds and remaps on import',()=>{
 const source={session:{theme:{master:{backgroundAssetId:masterId}}},activities:[{page_design:{widgets:[]},result_design:{}}]};
 assert.deepEqual(referencedAssets(source),new Set([masterId]));
 const mapped=remapPortableAssets(source,[masterId]);
 assert.notEqual(mapped.ids.get(masterId),masterId);
 assert.equal(mapped.definition.session.theme.master.backgroundAssetId,mapped.ids.get(masterId));
 assert.equal(source.session.theme.master.backgroundAssetId,masterId);
 assert.throws(()=>remapPortableAssets(source,[]),/unmatched_import_assets/);
});

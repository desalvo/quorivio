import test from 'node:test';
import assert from 'node:assert/strict';
import {createPageDraftBackup,parsePageDraftBackup,planPageDraftRecovery,validateEditablePageDraft} from '../../web/src/page-draft-recovery.ts';
import {mergePageDrafts} from '../../web/src/page-merge.ts';
import type {EditablePageDraft} from '../../web/src/page-draft.ts';
const base=():EditablePageDraft=>({widgets:[{id:'w1',kind:'text',label:'Original',position:{x:1,y:2,width:30,height:20}}],questionHeader:'Q',resultHeader:'R',questionBackground:'',resultBackground:'',questionBackgroundColor:'#ffffff',resultBackgroundColor:'#ffffff',questionBackgroundAsset:'',resultBackgroundAsset:''});
const exportV2=(draft=base(),b=base(),revision=3)=>JSON.stringify(createPageDraftBackup('session-1','page-1',revision,draft,b));
const read=(text:string)=>parsePageDraftBackup(text,'session-1','page-1');
const mutate=(fn:(x:any)=>void)=>{const x=JSON.parse(exportV2());fn(x);return JSON.stringify(x)};
const reject=(s:string,code:string)=>assert.throws(()=>read(s),new RegExp(code));

test('01 v2 export identifies format',()=>assert.equal(read(exportV2()).format,'quorivio-local-draft-v2'));
test('02 v2 export includes base snapshot',()=>assert.equal(read(exportV2()).base_draft?.questionHeader,'Q'));
test('03 backup includes current edits',()=>assert.equal(read(exportV2({...base(),questionHeader:'Changed'})).draft.questionHeader,'Changed'));
test('04 matching revision restores without merge',()=>assert.equal(planPageDraftRecovery(read(exportV2()),3).mode,'restore'));
test('05 stale v2 revision requires reconciliation',()=>assert.equal(planPageDraftRecovery(read(exportV2()),4).mode,'reconcile'));
test('06 future v2 revision also requires reconciliation',()=>assert.equal(planPageDraftRecovery(read(exportV2()),2).mode,'reconcile'));
test('07 invalid server revision blocks',()=>assert.equal(planPageDraftRecovery(read(exportV2()),0).mode,'blocked'));
test('08 v1 backups remain readable',()=>{const x=JSON.parse(exportV2());x.format='quorivio-local-draft-v1';delete x.base_draft;assert.equal(read(JSON.stringify(x)).format,'quorivio-local-draft-v1')});
test('09 v1 matching revision restores',()=>{const x=JSON.parse(exportV2());x.format='quorivio-local-draft-v1';delete x.base_draft;assert.equal(planPageDraftRecovery(read(JSON.stringify(x)),3).mode,'restore')});
test('10 v1 stale revision is blocked',()=>{const x=JSON.parse(exportV2());x.format='quorivio-local-draft-v1';delete x.base_draft;assert.deepEqual(planPageDraftRecovery(read(JSON.stringify(x)),4),{mode:'blocked',reason:'legacy_backup_stale'})});
test('11 rejects unrelated session',()=>reject(mutate(x=>x.session_id='other'),'draft_page_mismatch'));
test('12 rejects unrelated page',()=>reject(mutate(x=>x.activity_id='other'),'draft_page_mismatch'));
test('13 rejects missing session ID',()=>reject(mutate(x=>delete x.session_id),'draft_page_mismatch'));
test('14 rejects invalid format',()=>reject(mutate(x=>x.format='other'),'unsupported_draft_format'));
test('15 rejects missing format',()=>reject(mutate(x=>delete x.format),'unsupported_draft_format'));
test('16 rejects broken JSON',()=>reject('{broken','invalid_draft_json'));
test('17 rejects oversized JSON text',()=>reject('x'.repeat(2_000_001),'draft_file_too_large'));
test('18 rejects zero revision',()=>reject(mutate(x=>x.base_revision=0),'invalid_draft_revision'));
test('19 rejects fractional revision',()=>reject(mutate(x=>x.base_revision=1.5),'invalid_draft_revision'));
test('20 rejects missing base snapshot in v2',()=>reject(mutate(x=>delete x.base_draft),'invalid_page_draft'));
test('21 rejects missing widget array',()=>reject(mutate(x=>delete x.draft.widgets),'invalid_page_widgets'));
test('22 rejects duplicate widget identities',()=>reject(mutate(x=>x.draft.widgets.push(x.draft.widgets[0])),'invalid_page_widget_id'));
test('23 rejects empty widget identity',()=>reject(mutate(x=>x.draft.widgets[0].id=''),'invalid_page_widget_id'));
test('24 rejects widget without kind',()=>reject(mutate(x=>delete x.draft.widgets[0].kind),'invalid_page_widget_kind'));
test('25 rejects missing page text field',()=>reject(mutate(x=>delete x.draft.questionHeader),'invalid_page_field_questionHeader'));
test('26 rejects excessively long page text',()=>reject(mutate(x=>x.draft.questionHeader='a'.repeat(100001)),'invalid_page_field_questionHeader'));
test('27 rejects prototype pollution keys',()=>{reject(mutate(x=>Object.defineProperty(x.draft.widgets[0],'__proto__',{value:{polluted:true},enumerable:true})),'unsafe_draft_key')});
test('28 rejects constructor pollution in nested object',()=>reject(mutate(x=>x.draft.widgets[0].style=JSON.parse('{"constructor":{"prototype":{"polluted":true}}}')),'unsafe_draft_key'));
test('29 stale v2 merges independent recovered and server changes',()=>{const b=base(),l={...b,questionHeader:'Local'},r={...b,resultHeader:'Server'};const backup=read(exportV2(l,b));const plan=planPageDraftRecovery(backup,4);assert.equal(plan.mode,'reconcile');const out=mergePageDrafts(backup.base_draft!,backup.draft,r);assert.equal(out.conflicts.length,0);assert.equal(out.draft.questionHeader,'Local');assert.equal(out.draft.resultHeader,'Server')});
test('30 stale v2 conflicting edits require explicit choice',()=>{const b=base(),l={...b,questionHeader:'Local'},r={...b,questionHeader:'Server'};const backup=read(exportV2(l,b));const out=mergePageDrafts(backup.base_draft!,backup.draft,r);assert.equal(out.conflicts.length,1);assert.equal(mergePageDrafts(backup.base_draft!,backup.draft,r,{'/questionHeader':'local'}).draft.questionHeader,'Local')});

// RC121: export must be compatible with legitimate optional UI widget props.
test('31 export omits undefined optional widget props and nested styles without mutating editor state',()=>{
 const source=base();
 (source.widgets[0] as any).showTitle=undefined;
 (source.widgets[0] as any).style={fillColor:'#123456',answerBold:undefined,nested:{label:undefined,strokeWidth:2}};
 const saved=read(exportV2(source,source));
 const widget=saved.draft.widgets[0] as any;
 assert.equal('showTitle' in widget,false);
 assert.equal('answerBold' in widget.style,false);
 assert.equal('label' in widget.style.nested,false);
 assert.equal(widget.style.fillColor,'#123456');
 assert.equal(widget.style.nested.strokeWidth,2);
 assert.equal('showTitle' in (source.widgets[0] as any),true);
 assert.equal('answerBold' in (source.widgets[0] as any).style,true);
 assert.deepEqual(saved.base_draft?.widgets,saved.draft.widgets);
});
test('32 export refuses undefined array elements instead of silently changing positions',()=>{
 const source=base();(source.widgets[0] as any).options=['yes',undefined,'no'];
 assert.throws(()=>exportV2(source,source),/invalid_draft_value/);
});
test('33 export refuses invalid nested values and non-finite geometry',()=>{
 const source=base();(source.widgets[0] as any).position.width=Infinity;
 assert.throws(()=>exportV2(source,source),/invalid_draft_number/);
 const source2=base();(source2.widgets[0] as any).formatter=()=>{};
 assert.throws(()=>exportV2(source2,source2),/invalid_draft_value/);
});
test('34 export retains prototype-pollution protection after optional-prop normalization',()=>{
 const source=base();(source.widgets[0] as any).optional=undefined;
 Object.defineProperty(source.widgets[0],'__proto__',{value:{polluted:true},enumerable:true});
 assert.throws(()=>exportV2(source,source),/unsafe_draft_key/);
});
test('35 export rejects cyclic graph without mutating the input',()=>{
 const source=base();const cyclic:any={color:'#123456'};cyclic.self=cyclic;(source.widgets[0] as any).style=cyclic;
 assert.throws(()=>exportV2(source,source),/invalid_draft_value/);
});

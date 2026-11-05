import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {presenterVisiblePages,presenterAdjacentPage,presenterPageIndex} from '../src/presenter-navigation.ts';
import {linkedStatisticActivity,linkedStatisticSource,effectiveResultView} from '../src/widget-results.ts';
const question={id:'question',page_design:{presenterHidden:true,widgets:[{id:'q',kind:'question',label:'Domanda',resultsView:'cloud'}]}};
const results={id:'results',page_design:{audiencePageId:'question',widgets:[{id:'result',kind:'results-button',targetActivityId:'question',targetWidgetId:'q'}]}};
const ending={id:'end',page_design:{widgets:[]}};
test('presenter navigation omits hidden question pages without removing their widgets',()=>{
 const ordered=presenterVisiblePages([question,results,ending]);
 assert.deepEqual(ordered.map(p=>p.id),['results','end']);
 assert.equal(presenterPageIndex(ordered,'results'),0);
 assert.equal(presenterAdjacentPage(ordered,'results',1)?.id,'end');
 assert.equal(presenterAdjacentPage(ordered,'end',-1)?.id,'results');
 assert.equal(presenterAdjacentPage(ordered,'end',1),null);
});
test('presenter statistic reference resolves to the hidden question page',()=>{
 const widget=results.page_design.widgets[0];
 const activity=linkedStatisticActivity(widget,results,[question,results,ending]);
 assert.equal(activity?.id,'question');
 const source=linkedStatisticSource(widget,activity?.page_design.widgets||[]);
 assert.equal(source?.id,'q');
 assert.equal(effectiveResultView(widget,activity?.page_design.widgets||[]),'cloud');
 assert.equal(linkedStatisticActivity({...widget,targetActivityId:'foreign'},results,[question,results]),undefined);
 assert.equal(linkedStatisticActivity({id:'self',kind:'results-button'},results,[question,results])?.id,'results');
});
test('editor exposes dedicated canvas routing controls and source page selector',()=>{
 const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
 assert.match(ui,/Pagina partecipanti dal menu canvas/);
 assert.match(ui,/Nascondi al presentatore dal menu canvas/);
 assert.match(ui,/Pagina sorgente statistiche/);
 assert.match(ui,/presenterVisiblePages\(data\?\.activities\|\|\[\]\)/);
 assert.match(ui,/expected_presenter_activity_id/);
 assert.match(ui,/PresenterLinkedResult sessionId=\{sessionId\} activity=\{activity\} widget=\{w\} widgets=\{widgets\} activities=\{snapshot\.activities\}/);
});

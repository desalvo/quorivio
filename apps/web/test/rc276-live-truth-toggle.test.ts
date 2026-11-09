/** RC276: live cross-page truth toggling is owned by the shared results renderer. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const liveSection=(source:string)=>source.split('function PresenterLinkedResult(',2)[1]?.split('function ProjectedQuestionPart(',1)[0]||'';
const chartSection=(source:string)=>source.split('function LinkedResultChart(',2)[1]?.split('function PresenterLinkedResult(',1)[0]||'';
const liveTruthWiring=(source:string)=>{
 const live=liveSection(source),chart=chartSection(source);
 return live.includes('linkedStatisticContext(widget,activity,activities,widgets)') &&
   live.includes('const sourceWidgets=context?.widgets||[]') &&
   live.includes('<LinkedResultChart widget={widget} widgets={sourceWidgets} rows={rows} emptyLabel="live"/>') &&
   chart.includes('const source=linkedStatisticSource(widget,widgets)') &&
   chart.includes('resultHasAnswerKey(source,widget.targetQuestionId') &&
   chart.includes('const viewWidget={...widget,showCorrectAnswers:hasKey&&truthVisible}') &&
   chart.includes('{hasKey&&<button') &&
   chart.includes('aria-pressed={truthVisible}') &&
   chart.includes('setTruthVisible(v=>!v)') &&
   chart.includes('<LinkedResultSourceQuestion result={viewWidget} source={source}/>') &&
   chart.includes('answerTruthVerdict(source,widget.targetQuestionId') &&
   !live.includes('showCorrectLive');
};
test('live presenter resolves a cross-page source and uses the shared toggle and truth overlay',()=>{
 assert.equal(liveTruthWiring(ui),true);
});
test('regression: losing source-page widgets must disable the cross-page source contract',()=>{
 assert.equal(liveTruthWiring(ui.replace('widgets={sourceWidgets} rows={rows} emptyLabel="live"','widgets={widgets} rows={rows} emptyLabel="live"')),false);
});
test('regression: removing R activation must invalidate the live contract',()=>{
 assert.equal(liveTruthWiring(ui.replace('setTruthVisible(v=>!v)','void 0')),false);
});
test('regression: never pass the original widget to the truth-aware source copy',()=>{
 assert.equal(liveTruthWiring(ui.replace('result={viewWidget} source={source}','result={widget} source={source}')),false);
});
test('regression: a missing answer key must never enable the truth overlay',()=>{
 assert.equal(liveTruthWiring(ui.replace('showCorrectAnswers:hasKey&&truthVisible','showCorrectAnswers:truthVisible')),false);
});

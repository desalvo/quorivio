import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {answerTruthVerdict,feedbackOptionVerdict,truthVerdictClass,truthVerdictSymbol} from '../src/answer-truth-presentation.ts';
import {gradeChoiceAnswer} from '../../api/src/widget-answer-key.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const quiz={kind:'question',answerMode:'multiple',answerKeyEnabled:true,correctOptionIds:['a','c'],options:[{id:'a',label:'A'},{id:'b',label:'B'},{id:'c',label:'C'}]};

test('no feedback before submission, correct and incorrect labels after submitting a multiple-choice answer',()=>{
 for(const o of quiz.options)assert.equal(feedbackOptionVerdict(null,o.id),null);
 const feedback=gradeChoiceAnswer(quiz,'question',['a','b']);
 assert.equal(feedback?.is_correct,false);
 assert.equal(feedbackOptionVerdict(feedback,'a'),'correct');
 assert.equal(feedbackOptionVerdict(feedback,'b'),'incorrect');
 assert.equal(feedbackOptionVerdict(feedback,'c'),'correct');
 assert.equal(feedbackOptionVerdict(feedback,'unknown'),null);
 assert.equal(gradeChoiceAnswer(quiz,'question',['a','c'])?.is_correct,true);
});

test('truth rendering never enables for a disabled key, missing source or before pressing R',()=>{
 assert.equal(answerTruthVerdict(quiz,'','a',false),null);
 assert.equal(answerTruthVerdict({...quiz,answerKeyEnabled:false},'','a',true),null);
 assert.equal(answerTruthVerdict(null,'','a',true),null);
 assert.equal(answerTruthVerdict(quiz,'','a',true),'correct');
 assert.equal(answerTruthVerdict(quiz,'','b',true),'incorrect');
 assert.equal(answerTruthVerdict(quiz,'','invalid',true),null);
 assert.equal(truthVerdictSymbol('correct'),'✓');
 assert.equal(truthVerdictSymbol('incorrect'),'✕');
 assert.match(truthVerdictClass('correct'),/true/);
 assert.match(truthVerdictClass('incorrect'),/false/);
});

test('independent subquestions use their own answer key',()=>{
 const source={kind:'question',answerMode:'text',questions:[{...quiz,id:'q1'},{id:'q2',answerMode:'single',answerKeyEnabled:true,correctOptionId:'b',options:quiz.options}]};
 assert.equal(answerTruthVerdict(source,'q1','a',true),'correct');
 assert.equal(answerTruthVerdict(source,'q2','a',true),'incorrect');
 assert.equal(answerTruthVerdict(source,'q2','b',true),'correct');
 assert.equal(answerTruthVerdict(source,'missing','a',true),null);
});

test('inline verdict appears in live participant and rehearsal, never below a separate solution',()=>{
 assert.match(ui,/submitted\?feedbackOptionVerdict\(feedback,o\.id\):null/);
 assert.match(ui,/const demoFeedback=sent\?gradeChoiceAnswer\(/);
 assert.match(ui,/data-answer-verdict=\{verdict\|\|undefined\}/);
 assert.doesNotMatch(ui,/>Soluzione:<\/p>/);
 assert.match(ui,/Risposta sbagliata\./);
 assert.match(css,/border:2px solid #15803d!important/);
 assert.match(css,/border:2px solid #b91c1c!important/);
});

test('R toggle is interactive in the shared result renderer (live, editor, previews)',()=>{
 assert.match(ui,/className=\{'result-answer-key-toggle'/);
 assert.match(ui,/aria-pressed=\{truthVisible\}/);
 assert.match(ui,/setTruthVisible\(v=>!v\)/);
 assert.match(ui,/showCorrectAnswers:hasKey&&truthVisible/);
 assert.match(ui,/answerTruthVerdict\(source,widget.targetQuestionId/);
 assert.match(ui,/answerTruthVerdict\(source,questionId/);
 assert.match(ui,/formatTab==='content'&&\['question','timed-quiz'\]\.includes\(w.kind\)/);
 assert.match(css,/border-radius:50%!important/);
});

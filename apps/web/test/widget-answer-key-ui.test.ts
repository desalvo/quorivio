import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
test('question answer key available in property drawer, independent subquestions and canvas context menu',()=>{
 assert.match(ui,/function ChoiceTruthEditor/);
 assert.match(ui,/question=\{selectedQuestion\} kind=\{selectedQuestion.kind\}/);
 assert.match(ui,/question=\{q\} kind=\{widget.kind\}/);
 assert.match(ui,/context question=\{w\} kind=\{w.kind\}/);
 assert.match(ui,/setChoiceTruth\(/);
 assert.match(ui,/clearChoiceTruth\(/);
 assert.match(ui,/Stato vero falso opzione/);
 assert.match(ui,/Resetta stati vero\/falso/);
 assert.match(ui,/Assegna vero\/falso alle opzioni e mostra il risultato dopo l'invio/);
});
test('feedback is sourced from response API, displayed only after success, not from leaked public key',()=>{
 assert.match(ui,/setFeedback\(r.feedback\|\|null\)/);
 assert.match(ui,/submitted&&feedback&&/);
 assert.match(ui,/Risposta corretta!/);
 assert.match(ui,/Risposta errata\./);
 assert.match(ui,/o.correct\?'Vero':'Falso'/);
 assert.doesNotMatch(ui.slice(ui.indexOf('function QuestionWidgetSingle('),ui.indexOf('type RehearsalMode=')),/answerKeyIds\(/);
 assert.match(css,/widget-answer-feedback\[data-answer-correct="true"\]/);
 assert.match(css,/widget-answer-feedback\[data-answer-correct="false"\]/);
});

/** Shared verdict presentation: no grading key is exposed by this module.
 * Participant views use server feedback after submission, never page design. */
/** The result source is private for editor/presenter; public snapshots strip keys. */
function keyedPart(source:any,questionId:string):any|null{
 if(!source||!['question','timed-quiz'].includes(source.kind))return null;
 const part=questionId?source.questions?.find((q:any)=>q.id===questionId):source;
 if(!part||!['single','multiple'].includes(part.answerMode||(source.kind==='timed-quiz'?'single':'text'))||!(part.answerKeyEnabled===true||source.kind==='timed-quiz'))return null;
 return part;
}
export type AnswerVerdict='correct'|'incorrect'|null;
export type SubmittedFeedback={is_correct:boolean;choices:{id:string;correct:boolean}[]}|null;
export function feedbackOptionVerdict(feedback:SubmittedFeedback|undefined,id:string):AnswerVerdict{
 const choice=feedback?.choices?.find(o=>o.id===id);
 return choice?choice.correct?'correct':'incorrect':null;
}
export function answerTruthVerdict(source:any,questionId:string,optionId:string,visible:boolean):AnswerVerdict{
 const part=visible?keyedPart(source,questionId):null;
 if(!part?.options?.some((o:any)=>o.id===optionId))return null;
 const ids=part.answerMode==='multiple'?(part.correctOptionIds||[]):(part.correctOptionId?[part.correctOptionId]:(part.correctOptionIds?.length===1?part.correctOptionIds:[]));
 return ids.includes(optionId)?'correct':'incorrect';
}
export function truthVerdictClass(verdict:AnswerVerdict):string{
 return verdict==='correct'?' linked-source-answer-true':verdict==='incorrect'?' linked-source-answer-false':'';
}
export function truthVerdictSymbol(verdict:AnswerVerdict):string{
 return verdict==='correct'?'✓':verdict==='incorrect'?'✕':'';
}

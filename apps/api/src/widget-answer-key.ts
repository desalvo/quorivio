/** An optional answer key for ordinary choice widgets; timed quizzes retain their
 * historical mandatory scorer. Never add these keys to a public snapshot. */
export type KeyedChoice = {id:string;label:string};
export type KeyedQuestion = {kind?:string;answerMode?:string;answerKeyEnabled?:boolean;options?:KeyedChoice[];correctOptionId?:string;correctOptionIds?:string[]};

export function hasAnswerKey(question:KeyedQuestion,kind:string):boolean {
 return (kind==='timed-quiz'||question.answerKeyEnabled===true)&&['single','multiple'].includes(question.answerMode||(kind==='timed-quiz'?'single':'text'));
}
export function answerKeyIds(question:KeyedQuestion):string[] {
 const options=Array.isArray(question.options)?question.options:[];
 const ids=question.answerMode==='multiple'
  ?(Array.isArray(question.correctOptionIds)?question.correctOptionIds:[])
  :(typeof question.correctOptionId==='string'&&question.correctOptionId?[question.correctOptionId]
    :Array.isArray(question.correctOptionIds)&&question.correctOptionIds.length===1?question.correctOptionIds:[]);
 const allowed=new Set(options.map(o=>o.id));
 return [...new Set(ids.filter(id=>allowed.has(id)))];
}
/** Set one state. The first assignment activates the entire answer key, with all
 * other choices false. A single-choice question can have at most one true. */
export function setChoiceTruth(question:KeyedQuestion,optionId:string,correct:boolean):Partial<KeyedQuestion> {
 if(!question.options?.some(o=>o.id===optionId))throw new Error('Unknown choice');
 const prior=question.answerKeyEnabled===true||question.kind==='timed-quiz'?answerKeyIds(question):[];
 const ids=correct?(question.answerMode==='multiple'?[...new Set([...prior,optionId])]:[optionId]):prior.filter(id=>id!==optionId);
 return {answerKeyEnabled:true,correctOptionId:question.answerMode==='multiple'?undefined:ids[0],correctOptionIds:ids};
}
export function clearChoiceTruth():Partial<KeyedQuestion>{return {answerKeyEnabled:false,correctOptionId:undefined,correctOptionIds:[]}}
export type AnswerFeedback={is_correct:boolean;choices:{id:string;label:string;correct:boolean}[]};
export function gradeChoiceAnswer(question:KeyedQuestion,kind:string,selected:unknown):AnswerFeedback|null {
 if(!hasAnswerKey(question,kind)||!Array.isArray(selected)||!selected.every(x=>typeof x==='string'))return null;
 const options=question.options||[];
 const correct=new Set(answerKeyIds(question));
 const chosen=new Set(selected as string[]);
 return {is_correct:chosen.size===correct.size&&[...chosen].every(id=>correct.has(id)),choices:options.map(option=>({id:option.id,label:option.label,correct:correct.has(option.id)}))};
}

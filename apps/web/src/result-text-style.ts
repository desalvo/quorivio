import type {CSSProperties} from 'react';
/** Bounded per-element presentation styles. Values are persisted as data, never CSS source. */
export type ResultTextStyle={fontFamily?:string;fontSize?:number;color?:string;bold?:boolean;italic?:boolean;underline?:boolean;strikethrough?:boolean};
export type ResultTextStyles=Record<string,ResultTextStyle>;
export const RESULT_FONTS=['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'] as const;
export function validResultTextStyles(value:unknown):value is ResultTextStyles {
 if(value===undefined)return true;
 if(!value||typeof value!=='object'||Array.isArray(value))return false;
 const styles=value as Record<string,unknown>;
 if(Object.keys(styles).length>50)return false;
 return Object.entries(styles).every(([key,item])=>{
  if(!/^(sourceTitle|question:(main|[A-Za-z0-9_-]{1,40})|option:([A-Za-z0-9_-]{1,40}:)?[A-Za-z0-9_-]{1,40}|row:([A-Za-z0-9_-]{1,40}:)?[A-Za-z0-9_-]{1,40})$/.test(key))return false;
  if(!item||typeof item!=='object'||Array.isArray(item))return false;
  const fmt=item as Record<string,unknown>;
  if(Object.keys(fmt).some(name=>!['fontFamily','fontSize','color','bold','italic','underline','strikethrough'].includes(name)))return false;
  return Object.entries(fmt).every(([name,val])=>name==='fontFamily'?RESULT_FONTS.includes(val as any):name==='fontSize'?Number.isInteger(val)&&Number(val)>=8&&Number(val)<=96:name==='color'?typeof val==='string'&&/^#[0-9a-fA-F]{6}$/.test(val):typeof val==='boolean');
 });
}
export function resultTextCss(styles:ResultTextStyles|undefined,key:string,defaults:ResultTextStyle={}):CSSProperties{
 const x={...defaults,...(styles?.[key]||{})};
 return {fontFamily:x.fontFamily,fontSize:x.fontSize?`${x.fontSize}px`:undefined,color:x.color,fontWeight:x.bold===undefined?undefined:x.bold?700:400,fontStyle:x.italic===undefined?undefined:x.italic?'italic':'normal',textDecoration:[x.underline?'underline':'',x.strikethrough?'line-through':''].filter(Boolean).join(' ')||undefined};
}
export function resultElementKey(kind:'option'|'row',questionId:string,optionId:string):string{
 return kind+':'+(questionId?questionId+':':'')+optionId;
}
export function resultTrueOptionIds(source:any,questionId=''):string[]{
 if(!['question','timed-quiz'].includes(source?.kind))return [];
 const part=questionId?source.questions?.find((q:any)=>q.id===questionId):source;
 if(!part||!['single','multiple'].includes(part.answerMode||(source.kind==='timed-quiz'?'single':'text'))||!(part.answerKeyEnabled===true||source.kind==='timed-quiz'))return [];
 const ids=part.answerMode==='multiple'?(part.correctOptionIds||[]):(part.correctOptionId?[part.correctOptionId]:part.correctOptionIds?.length===1?part.correctOptionIds:[]);
 const valid=new Set((part.options||[]).map((o:any)=>o.id));return [...new Set((ids as string[]).filter(id=>valid.has(id)))];
}
export function resultHasAnswerKey(source:any,questionId=''):boolean{
 if(!['question','timed-quiz'].includes(source?.kind))return false;
 const part=questionId?source.questions?.find((q:any)=>q.id===questionId):source;
 return !!part&&['single','multiple'].includes(part.answerMode||(source.kind==='timed-quiz'?'single':'text'))&&(part.answerKeyEnabled===true||source.kind==='timed-quiz');
}

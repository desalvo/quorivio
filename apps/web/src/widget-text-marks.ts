/** Persistent, HTML-free character-range formatting for editable widget content.
 * Text is kept as plain strings, with bounded formatting marks validated by API.
 * Range offsets are UTF-16 string offsets, like HTMLInputElement selectionStart.
 */
import type {WidgetTextStyle} from '../../api/src/domain';
export type InlineStyle=Pick<WidgetTextStyle,'fontFamily'|'fontSize'|'color'|'bold'|'italic'|'underline'|'strikethrough'>;
export type TextMark={field:string;start:number;end:number;style:InlineStyle};
export const inlineKeys=['fontFamily','fontSize','color','bold','italic','underline','strikethrough'] as const;
export function formatTextRange(marks:TextMark[],field:string,start:number,end:number,style:InlineStyle):TextMark[]{
 if(start<0||end<=start||end>500||marks.length>=64)return marks;
 return [...marks,{field,start,end,style}];
}
/** Preserve marks across edits, expanding on inserted characters within a marked run. */
export function remapMarks(marks:TextMark[],field:string,oldText:string,newText:string):TextMark[]{
 let first=0;while(first<Math.min(oldText.length,newText.length)&&oldText[first]===newText[first])first++;
 let suffix=0;while(suffix<Math.min(oldText.length-first,newText.length-first)&&oldText[oldText.length-1-suffix]===newText[newText.length-1-suffix])suffix++;
 const endOld=oldText.length-suffix,endNew=newText.length-suffix,delta=endNew-endOld;
 return marks.flatMap(mark=>{
  if(mark.field!==field)return [mark];
  if(mark.end<=first)return [mark];
  if(mark.start>=endOld)return [{...mark,start:mark.start+delta,end:mark.end+delta}];
  const start=Math.min(mark.start,first);
  const end=Math.max(first,mark.end+delta);
  return end>start?[{...mark,start,end}]:[];
 }).filter(m=>m.field!==field||(m.start>=0&&m.end<=newText.length&&m.end>m.start));
}
export function styledSegments(text:string,marks:TextMark[]|undefined,field:string):{text:string;style:InlineStyle}[]{
 if(!text)return [];
 const relevant=(marks||[]).filter(m=>m.field===field&&m.end>m.start&&m.start>=0&&m.end<=text.length);
 const points=[...new Set([0,text.length,...relevant.flatMap(m=>[m.start,m.end])])].sort((a,b)=>a-b);
 return points.slice(0,-1).map((start,index)=>({text:text.slice(start,points[index+1]),style:Object.assign({},...relevant.filter(m=>m.start<=start&&m.end>=points[index+1]).map(m=>m.style))}));
}
export function inlineMarkCss(s:InlineStyle):Record<string,string|undefined>{
 return {fontFamily:s.fontFamily,fontSize:s.fontSize!==undefined?`${(s.fontSize/1280*100).toFixed(5)}cqw`:undefined,color:s.color,fontWeight:s.bold?'bold':s.bold===false?'normal':undefined,fontStyle:s.italic?'italic':s.italic===false?'normal':undefined,textDecoration:[s.underline?'underline':'',s.strikethrough?'line-through':''].filter(Boolean).join(' ')||undefined};
}

export function changedRegion(before:string,after:string):{start:number;end:number}{
 let start=0;while(start<Math.min(before.length,after.length)&&before[start]===after[start])start++;
 let suffix=0;while(suffix<Math.min(before.length-start,after.length-start)&&before[before.length-suffix-1]===after[after.length-suffix-1])suffix++;
 return {start,end:after.length-suffix};
}

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
/** The insertion style must come from the glyph *before* the caret, even
 * when that glyph belongs to the second or later styled segment. */
export function styleOfPreviousCharacter(text:string,marks:TextMark[],field:string,at:number):InlineStyle{
 if(!text)return {} as InlineStyle;
 const position=Math.max(0,Math.min(text.length-1,at-1));
 let offset=0;
 for(const part of styledSegments(text,marks,field)){
  offset+=part.text.length;
  if(position<offset)return part.style;
 }
 return {} as InlineStyle;
}
/** Preserve marks across edits, expanding on inserted characters within a marked run. */
export function remapMarks(marks:TextMark[],field:string,oldText:string,newText:string):TextMark[]{
 let first=0;while(first<Math.min(oldText.length,newText.length)&&oldText[first]===newText[first])first++;
 let suffix=0;while(suffix<Math.min(oldText.length-first,newText.length-first)&&oldText[oldText.length-1-suffix]===newText[newText.length-1-suffix])suffix++;
 const endOld=oldText.length-suffix,endNew=newText.length-suffix,delta=endNew-endOld;
 const inherited=delta>0&&endOld===first&&oldText.length>0?
  styleOfPreviousCharacter(oldText,marks,field,first):null;
 const shifted=marks.flatMap(mark=>{
  if(mark.field!==field)return [mark];
  if(mark.end<=first)return [mark];
  if(mark.start>=endOld)return [{...mark,start:mark.start+delta,end:mark.end+delta}];
  const start=Math.min(mark.start,first);
  const end=Math.max(first,mark.end+delta);
  return end>start?[{...mark,start,end}]:[];
 }).filter(m=>m.field!==field||(m.start>=0&&m.end<=newText.length&&m.end>m.start));
 // A keyboard insertion at a formatting boundary inherits the character
 // immediately BEFORE the caret, not the run following it. This includes
 // font face, size, weight and underline. Preserve IME and UTF-16 positions.
 if(inherited&&Object.keys(inherited).length&&first<endNew){
  const next=applySelectionInlineStyle(shifted,field,newText,first,endNew,inherited);
  return next;
 }
 return shifted;
}
export function styledSegments(text:string,marks:TextMark[]|undefined,field:string):{text:string;style:InlineStyle}[]{
 if(!text)return [];
 const relevant=(marks||[]).filter(m=>m.field===field&&m.end>m.start&&m.start>=0&&m.end<=text.length);
 const points=[...new Set([0,text.length,...relevant.flatMap(m=>[m.start,m.end])])].sort((a,b)=>a-b);
 return points.slice(0,-1).map((start,index)=>({text:text.slice(start,points[index+1]),style:Object.assign({},...relevant.filter(m=>m.start<=start&&m.end>=points[index+1]).map(m=>m.style))}));
}
export function inlineMarkCss(s:InlineStyle):Record<string,string|undefined>{
 return {fontFamily:s.fontFamily,fontSize:s.fontSize!==undefined?`${(s.fontSize/1280*100).toFixed(5)}cqw`:undefined,
  '--q-inline-phone-font-size':s.fontSize!==undefined?`${s.fontSize}px`:undefined,color:s.color,fontWeight:s.bold?'bold':s.bold===false?'normal':undefined,fontStyle:s.italic?'italic':s.italic===false?'normal':undefined,textDecoration:[s.underline?'underline':'',s.strikethrough?'line-through':''].filter(Boolean).join(' ')||(s.underline===false||s.strikethrough===false?'none':undefined)};
}


/** Compute the effective text style from the widget base and ordered inline marks.
 * A toggle is active only if EVERY character of the selected range has the flag.
 */
export function selectionUniformValue<K extends keyof InlineStyle>(text:string,marks:TextMark[],field:string,start:number,end:number,base:InlineStyle,key:K):InlineStyle[K]|undefined{
 if(start<0||end<=start||end>text.length)return undefined;
 let offset=0;let current:InlineStyle[K]|undefined;let first=true;
 for(const part of styledSegments(text,marks,field)){
  const from=offset,to=offset+part.text.length;offset=to;
  if(to<=start||from>=end)continue;
  const value=(part.style[key]??base[key]) as InlineStyle[K]|undefined;
  if(first){current=value;first=false}else if(current!==value)return undefined;
 }
 return current;
}
/** Apply a change ONLY to the highlighted text. Rebuild contiguous marks so
 * repeated toggles overwrite earlier runs instead of creating unbounded layers.
 * Data is deliberately plain text plus bounded safe inline style objects.
 */
export function applySelectionInlineStyle(marks:TextMark[],field:string,text:string,start:number,end:number,change:InlineStyle):TextMark[]{
 if(start<0||end<=start||end>text.length||end>500)return marks;
 const current=marks.filter(m=>m.field===field);
 const other=marks.filter(m=>m.field!==field);
 const points=[...new Set([0,text.length,start,end,...current.flatMap(m=>[m.start,m.end])])].filter(n=>n>=0&&n<=text.length).sort((a,b)=>a-b);
 const next:TextMark[]=[];
 for(let i=0;i<points.length-1;i++){
  const from=points[i],to=points[i+1];if(from===to)continue;
  const effective=Object.assign({},...current.filter(m=>m.start<=from&&m.end>=to).map(m=>m.style)) as InlineStyle;
  const applied=from>=start&&to<=end?{...effective,...change}:effective;
  if(!Object.keys(applied).length)continue;
  const last=next[next.length-1];
  if(last&&last.end===from&&JSON.stringify(last.style)===JSON.stringify(applied))last.end=to;
  else next.push({field,start:from,end:to,style:applied});
 }
 return other.length+next.length<=64?[...other,...next]:marks;
}

export function changedRegion(before:string,after:string):{start:number;end:number}{
 let start=0;while(start<Math.min(before.length,after.length)&&before[start]===after[start])start++;
 let suffix=0;while(suffix<Math.min(before.length-start,after.length-start)&&before[before.length-suffix-1]===after[after.length-suffix-1])suffix++;
 return {start,end:after.length-suffix};
}

/** Scale the widget's base size and each independently authored size by the same factor.
 * Do not rewrite colors, faces, weights or per-character overrides. */
export function scaleWidgetFont(widget:{style?:{fontSize?:number};textMarks?:TextMark[]},nextSize:number):{style:Record<string,unknown>;textMarks:TextMark[]}{
 const base=widget.style?.fontSize??16;
 if(!Number.isInteger(nextSize)||nextSize<10||nextSize>96)return {style:{...(widget.style||{})},textMarks:widget.textMarks||[]};
 const factor=nextSize/base;
 return {style:{...(widget.style||{}),fontSize:nextSize},textMarks:(widget.textMarks||[]).map(mark=>({
  ...mark,style:mark.style.fontSize===undefined?mark.style:{...mark.style,fontSize:Math.max(10,Math.min(96,Math.round(mark.style.fontSize*factor)))}
 }))};
}

/** A whole-widget typography change keeps all authored relative size differences.
 * Text options, answer field and submit text inherit the same proportional factor.
 * Persist only server-approved fields; never turn a multi-size widget into one size.
 */
export function scaleAllWidgetTypography(widget:{kind?:string;style?:{fontSize?:number;answerFontSize?:number;submitButtonSize?:number;footerNumberFontSize?:number};textMarks?:TextMark[]},factor:number){
 if(!Number.isFinite(factor)||factor<=0)return {style:{...(widget.style||{})},textMarks:widget.textMarks||[]};
 const scale=(size:number,min:number,max:number)=>Math.max(min,Math.min(max,Math.round(size*factor)));
 return {style:{...(widget.style||{}),fontSize:scale(widget.style?.fontSize??16,10,96),
  answerFontSize:scale(widget.style?.answerFontSize??widget.style?.fontSize??16,10,96),
  ...(['question','timed-quiz','topic-question'].includes(widget.kind||'')?{submitButtonSize:scale(widget.style?.submitButtonSize??16,12,40)}:widget.style?.submitButtonSize?{submitButtonSize:scale(widget.style.submitButtonSize,12,40)}:{}),
  ...(widget.kind==='footer'?{footerNumberFontSize:scale(widget.style?.footerNumberFontSize??14,8,96)}:widget.style?.footerNumberFontSize?{footerNumberFontSize:scale(widget.style.footerNumberFontSize,8,96)}:{})},
  textMarks:(widget.textMarks||[]).map(mark=>({...mark,style:mark.style.fontSize===undefined?mark.style:
    {...mark.style,fontSize:scale(mark.style.fontSize,10,96)}}))};
}

/** Apply formatting to a chosen field without accidentally applying it to the
 * entire widget. An empty caret selection formats the complete field. */
export function formatSelectedOrEntireField(marks:TextMark[],field:string,text:string,range:{start:number;end:number}|null,style:InlineStyle):TextMark[]{
 if(!text||text.length>500)return marks;
 const from=range&&range.end>range.start?range.start:0;
 const to=range&&range.end>range.start?range.end:text.length;
 return applySelectionInlineStyle(marks,field,text,from,to,style);
}

/** Apply whole-widget font/color changes across existing inline overrides too,
 * including independent subquestions and response-option marks. */
export function applyAllWidgetTypeface(widget:{style?:Record<string,unknown>;textMarks?:TextMark[]},change:InlineStyle){
 const style={...(widget.style||{}),...change};
  // Keep answer-option typography synchronized with the widget-wide style.
  // Object.assign retains the inferred return type while adding the valid
  // optional answer fields supported by the saved widget schema.
  Object.assign(style,
    change.fontFamily!==undefined?{answerFontFamily:change.fontFamily}:{},
    change.fontFamily!==undefined?{submitFontFamily:change.fontFamily,footerNumberFontFamily:change.fontFamily}:{},
    change.color!==undefined?{submitColor:change.color,footerNumberColor:change.color}:{},
    change.bold!==undefined?{submitBold:change.bold,footerNumberBold:change.bold}:{},
    change.italic!==undefined?{submitItalic:change.italic,footerNumberItalic:change.italic}:{},
    change.underline!==undefined?{submitUnderline:change.underline,footerNumberUnderline:change.underline}:{},
    change.strikethrough!==undefined?{submitStrikethrough:change.strikethrough,footerNumberStrikethrough:change.strikethrough}:{},
    change.color!==undefined?{answerColor:change.color}:{},
    change.bold!==undefined?{answerBold:change.bold}:{},
    change.italic!==undefined?{answerItalic:change.italic}:{},
    change.underline!==undefined?{answerUnderline:change.underline}:{},
    change.strikethrough!==undefined?{answerStrikethrough:change.strikethrough}:{});
 const marks=(widget.textMarks||[]).map(mark=>({...mark,style:{...mark.style,...change}}));
 return {style,textMarks:marks};
}

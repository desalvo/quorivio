/** Browser acceptance fixture mounts the production RichWidgetText, not a reimplementation. */
import React,{useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {RichWidgetText,type TextRange} from '../../apps/web/src/widget-rich-editor';
import {changedRegion,formatTextRange,remapMarks,styledSegments,inlineMarkCss,type TextMark,type InlineStyle} from '../../apps/web/src/widget-text-marks';
function Demo(){
 const [value,setValue]=useState('Alpha beta');
 const [marks,setMarks]=useState<TextMark[]>([]);
 const [active,setActive]=useState(true);
 const range=useRef<TextRange>({start:0,end:0});
 const pending=useRef<InlineStyle>({});
 const update=(next:string)=>{
  let updated=remapMarks(marks,'label',value,next);
  const added=changedRegion(value,next);
  if(added.end>added.start&&Object.keys(pending.current).length)updated=formatTextRange(updated,'label',added.start,added.end,pending.current);
  setMarks(updated);setValue(next);
 };
 const apply=(style:InlineStyle)=>{
  const {start,end}=range.current;
  if(end>start)setMarks(m=>formatTextRange(m,'label',start,end,style));
  else pending.current={...pending.current,...style};
 };
 return <><RichWidgetText value={value} marks={marks} field="label" active={active} onChange={update} onSelection={r=>range.current=r} onFinish={()=>setActive(false)} ariaLabel="Titolo widget"/>
 <button type="button" data-test="bold" onClick={()=>apply({bold:true})}>B</button>
 <button type="button" data-test="italic" onClick={()=>apply({italic:true})}>I</button>
 <button type="button" data-test="finish" onClick={()=>setActive(false)}>Done</button>
 <div data-test="projection" aria-label="Proiezione">{styledSegments(value,marks,'label').map((part,i)=><span key={i} style={inlineMarkCss(part.style)}>{part.text}</span>)}</div>
 <pre data-test="json">{JSON.stringify({value,marks})}</pre></>;
}
createRoot(document.getElementById('root')!).render(<Demo/>);

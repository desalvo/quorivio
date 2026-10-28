/** Inline rich-text editor that keeps the exact plain-text + bounded-mark contract
 * used by PostgreSQL, presenter and participant projection. Never persists HTML. */
import React,{useLayoutEffect,useRef} from 'react';
import {styledSegments,inlineMarkCss,type TextMark} from './widget-text-marks.js';

export type TextRange={start:number;end:number};
export function domTextRange(root:HTMLElement):TextRange|null {
 const selection=window.getSelection();
 if(!selection||!selection.rangeCount||!root.contains(selection.anchorNode)||!root.contains(selection.focusNode))return null;
 const before=(node:Node|null,offset:number)=>{
  if(!node)return 0;
  const range=document.createRange();range.selectNodeContents(root);range.setEnd(node,offset);
  return range.toString().length;
 };
 try{const a=before(selection.anchorNode,selection.anchorOffset),b=before(selection.focusNode,selection.focusOffset);return {start:Math.min(a,b),end:Math.max(a,b)}}catch{return null}
}
export function restoreDomTextRange(root:HTMLElement,selection:TextRange):void{
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 const nodes:Text[]=[];let node:Node|null;
 while((node=walker.nextNode()))nodes.push(node as Text);
 const point=(offset:number):[Node,number]=>{
  let remaining=Math.max(0,offset);
  for(const text of nodes){const len=text.textContent?.length||0;if(remaining<=len)return [text,remaining];remaining-=len}
  const last=nodes[nodes.length-1];return last?[last,last.textContent?.length||0]:[root,0];
 };
 try{const range=document.createRange();const [a,ao]=point(selection.start),[b,bo]=point(selection.end);range.setStart(a,ao);range.setEnd(b,bo);const selectionApi=window.getSelection();selectionApi?.removeAllRanges();selectionApi?.addRange(range)}catch{/* detaching a widget during autosave may invalidate a range */}
}
export function RichWidgetText({value,marks,field,active,onChange,onSelection,onFinish,ariaLabel,maxLength=240}:{value:string;marks?:TextMark[];field:string;active:boolean;onChange:(next:string)=>void;onSelection:(range:TextRange)=>void;onFinish?:()=>void;ariaLabel:string;maxLength?:number}){
 const root=useRef<HTMLDivElement>(null);
 const remembered=useRef<TextRange|null>(null);
 const lock=useRef(false);
 const composing=useRef(false);
 const capture=()=>{if(!root.current)return;const range=domTextRange(root.current);if(range){remembered.current=range;onSelection(range)}};
 // React must not reconcile children inside a live contentEditable. If it does,
 // browser-inserted text nodes can coexist with newly rendered spans and a
 // single keystroke appears twice on the following composition or input event.
 // Own ONLY the text DOM; still derive every span from validated plain text + marks.
 useLayoutEffect(()=>{
  const el=root.current;if(!el||composing.current)return;
  const selection=remembered.current;
  const fragment=document.createDocumentFragment();
  for(const part of styledSegments(value,marks,field)){
   const span=document.createElement('span');span.textContent=part.text;
   Object.assign(span.style,inlineMarkCss(part.style));fragment.appendChild(span);
  }
  lock.current=true;
  el.replaceChildren(fragment);
  lock.current=false;
  if(active&&document.activeElement===el&&selection)restoreDomTextRange(el,selection);
 },[value,marks,field,active]);
 return <div ref={root} className={'widget-rich-inline '+(active?'widget-rich-editing':'widget-rich-display')} role={active?'textbox':undefined} aria-label={ariaLabel} aria-multiline="false" tabIndex={active?0:undefined} contentEditable={active} suppressContentEditableWarning spellCheck={active}
  onFocus={capture} onKeyUp={capture} onMouseUp={capture} onPointerUp={capture}
  onBeforeInput={e=>{const evt=e.nativeEvent as InputEvent;if(evt.inputType==='insertParagraph'||evt.inputType==='insertLineBreak')e.preventDefault()}}
  onPaste={e=>{e.preventDefault();const plain=e.clipboardData.getData('text/plain').replace(/[\r\n]+/g,' ');const selection=window.getSelection();if(!selection||!selection.rangeCount)return;const range=selection.getRangeAt(0);const old=root.current?.textContent||'';const selected=domTextRange(root.current!);if(!selected)return;const available=maxLength-(old.length-(selected.end-selected.start));const safe=plain.slice(0,Math.max(0,available));range.deleteContents();const node=document.createTextNode(safe);range.insertNode(node);range.setStartAfter(node);range.collapse(true);selection.removeAllRanges();selection.addRange(range);remembered.current={start:selected.start+safe.length,end:selected.start+safe.length};onSelection(remembered.current);onChange(root.current?.textContent?.slice(0,maxLength)||'')}}
  // An IME may emit several interim onInput events. React must not replace the
  // composition DOM with styled spans until the browser commits the final text.
  onCompositionStart={()=>{composing.current=true}}
  onCompositionEnd={e=>{composing.current=false;const el=e.currentTarget;const next=(el.textContent||'').replace(/[\r\n]/g,' ');capture();if(next.length>maxLength){lock.current=true;el.textContent=value;lock.current=false;return}onChange(next)}}
  onInput={e=>{if(lock.current||composing.current)return;const el=e.currentTarget;const next=(el.textContent||'').replace(/[\r\n]/g,' ');capture();if(next.length>maxLength){lock.current=true;el.textContent=value;lock.current=false;return}onChange(next)}}
  onKeyDown={e=>{e.stopPropagation();if(!composing.current&&(e.key==='Enter'||e.key==='Escape')){e.preventDefault();onFinish?.();e.currentTarget.blur()}}}>
 </div>;
}

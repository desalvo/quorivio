/** Keyboard slide navigation in preview. Never consume arrow keys used by a
 * text field, choice control, slider, editor, or modified shortcut. */
export function rehearsalPageDirection(event:{key:string;altKey?:boolean;ctrlKey?:boolean;metaKey?:boolean;shiftKey?:boolean;target?:EventTarget|null}): -1|0|1 {
 if(event.altKey||event.ctrlKey||event.metaKey||event.shiftKey)return 0;
 const target=event.target;
 if(target&&typeof target==='object'&&'closest' in target&&typeof (target as Element).closest==='function'){
  if((target as Element).closest('input,textarea,select,[contenteditable="true"],[role="slider"],[role="textbox"],[role="spinbutton"]'))return 0;
 }
 if(event.key==='ArrowLeft'||event.key==='PageUp')return -1;
 if(event.key==='ArrowRight'||event.key==='PageDown')return 1;
 return 0;
}

export type PresenterPage={id:string};
export function presenterPageIndex<T extends PresenterPage>(activities:readonly T[], current:string|null|undefined):number {
 return activities.findIndex(page=>page.id===current);
}
export function presenterAdjacentPage<T extends PresenterPage>(activities:readonly T[],current:string|null|undefined,direction:-1|1):T|null{
 const index=presenterPageIndex(activities,current);
 const target=index+direction;
 return index<0||target<0||target>=activities.length?null:activities[target];
}
export function presenterKeyboardDirection(event:{key:string;altKey?:boolean;ctrlKey?:boolean;metaKey?:boolean;target?:EventTarget|null}):-1|1|null {
 if(event.altKey||event.ctrlKey||event.metaKey)return null;
 const el=event.target;
 if(typeof Element!=='undefined' && el instanceof Element && (el.closest('input,textarea,select,video,audio,[contenteditable="true"],[role="textbox"],[role="slider"]')||el.closest('[data-no-slide-keyboard]')))return null;
 if(event.key==='ArrowLeft'||event.key==='ArrowUp'||event.key==='PageUp')return -1;
 if(event.key==='ArrowRight'||event.key==='ArrowDown'||event.key==='PageDown')return 1;
 return null;
}

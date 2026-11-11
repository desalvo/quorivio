import {blocksSlideNavigation,type SlideNavigationKeyEvent} from './slide-keyboard-guard.ts';

export type PresenterPage={id:string};
export function presenterPageIndex<T extends PresenterPage>(activities:readonly T[], current:string|null|undefined):number {
 return activities.findIndex(page=>page.id===current);
}
export function presenterAdjacentPage<T extends PresenterPage>(activities:readonly T[],current:string|null|undefined,direction:-1|1):T|null{
 const index=presenterPageIndex(activities,current);
 const target=index+direction;
 return index<0||target<0||target>=activities.length?null:activities[target];
}
export function presenterKeyboardDirection(event:SlideNavigationKeyEvent):-1|1|null {
 if(blocksSlideNavigation(event))return null;
 if(event.key==='ArrowLeft'||event.key==='ArrowUp'||event.key==='PageUp')return -1;
 if(event.key==='ArrowRight'||event.key==='ArrowDown'||event.key==='PageDown')return 1;
 return null;
}
/** Pages hidden from the presenter stay available to the audience and results. */
export function presenterVisiblePages<T extends PresenterPage & {page_design?:{presenterHidden?:boolean}|null}>(activities:readonly T[]):T[]{
 return activities.filter(page=>page.page_design?.presenterHidden!==true);
}

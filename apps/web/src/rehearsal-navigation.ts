/** Rehearsal and live presentation share one keyboard focus policy. */
import {blocksSlideNavigation,type SlideNavigationKeyEvent} from './slide-keyboard-guard.ts';

export function rehearsalPageDirection(event:SlideNavigationKeyEvent): -1|0|1 {
 if(blocksSlideNavigation(event))return 0;
 if(event.key==='ArrowLeft'||event.key==='PageUp')return -1;
 if(event.key==='ArrowRight'||event.key==='PageDown')return 1;
 return 0;
}

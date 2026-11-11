/** Shared focus-aware shortcut policy for presenter and rehearsal.
 * Arrow and Page keys belong to interactive controls before slide navigation.
 * Never advance on modified, already handled, composing or repeated key events.
 */
export type SlideNavigationKeyEvent = {
  key:string;
  altKey?:boolean;
  ctrlKey?:boolean;
  metaKey?:boolean;
  shiftKey?:boolean;
  defaultPrevented?:boolean;
  isComposing?:boolean;
  repeat?:boolean;
  target?:EventTarget|null;
};

const INTERACTIVE_FOCUS_SELECTOR = [
  'input','textarea','select','button','a','summary','iframe','audio','video',
  '[contenteditable]','[role="textbox"]','[role="slider"]',
  '[role="spinbutton"]','[role="combobox"]','[role="listbox"]',
  '[role="option"]','[role="radio"]','[role="radiogroup"]',
  '[role="checkbox"]','[role="switch"]','[role="menu"]',
  '[role="menuitem"]','[role="menuitemcheckbox"]','[role="menuitemradio"]',
  '[role="tab"]','[role="tablist"]','[role="button"]','[role="link"]',
  '[role="tree"]','[role="treeitem"]','[role="grid"]','[role="gridcell"]',
  '[role="dialog"]','[aria-modal="true"]','[data-no-slide-keyboard]'
].join(',');

/** DOM-independent for node:test, but uses real Element.closest in browsers. */
export function blocksSlideNavigation(event:SlideNavigationKeyEvent):boolean {
  if(event.defaultPrevented||event.isComposing||event.repeat||
    event.altKey||event.ctrlKey||event.metaKey||event.shiftKey)return true;
  const target=event.target;
  if(!target||typeof target!=='object'||!('closest' in target))return false;
  const closest=(target as {closest?:unknown}).closest;
  return typeof closest==='function'&&Boolean(
    (closest as (selector:string)=>unknown).call(target,INTERACTIVE_FOCUS_SELECTOR)
  );
}

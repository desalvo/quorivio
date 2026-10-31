/** A context-button press must not update React selection/layout before
 * Chromium dispatches `contextmenu`. The menu handler itself owns selection.
 * Touch and primary-pen presses use button=0 just like the primary mouse key.
 */
export function startsWidgetSelectionOnPointerDown(button:number):boolean{
 return button===0;
}

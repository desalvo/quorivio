/** Browser-native canvas context ownership, independent of CSS event retargeting.
 * A context menu on a widget must not accidentally open the page background
 * menu when transform, overflow or pointer-capture retargets the event.
 */
export type WidgetContextRect = {left:number;top:number;right:number;bottom:number};
export function contextWidgetIndex(rectangles:readonly WidgetContextRect[],x:number,y:number):number{
 // Later siblings are visually on top when equal stacking context.
 for(let i=rectangles.length-1;i>=0;i--){
  const r=rectangles[i];
  if(Number.isFinite(x)&&Number.isFinite(y)&&x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom)return i;
 }
 return -1;
}
export function canvasWidgetAtPoint(canvas:HTMLElement,x:number,y:number):HTMLElement|null{
 const widgets=Array.from(canvas.querySelectorAll<HTMLElement>('.widget-canvas-item'));
 const index=contextWidgetIndex(widgets.map(widget=>widget.getBoundingClientRect()),x,y);
 return index<0?null:widgets[index];
}

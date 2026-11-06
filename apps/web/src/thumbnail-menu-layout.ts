/** Portaled thumbnail menus are viewport bounded even beside the last page.
 * Compact, initially collapsed groups reduce height; maxHeight is measured
 * from the actual top, not from the top of the viewport. */
export function thumbnailMenuPosition(x:number,y:number,viewportWidth:number,viewportHeight:number){
 const pad=8;
 const width=Math.min(270,Math.max(1,viewportWidth-pad*2));
 const availableHeight=Math.max(1,viewportHeight-pad*2);
 const preferredHeight=Math.min(340,availableHeight);
 const safeX=Number.isFinite(x)?x:pad,safeY=Number.isFinite(y)?y:pad;
 const left=Math.round(Math.max(pad,Math.min(safeX,Math.max(pad,viewportWidth-width-pad))));
 const top=Math.round(Math.max(pad,Math.min(safeY,Math.max(pad,viewportHeight-preferredHeight-pad))));
 const maxHeight=Math.max(1,Math.floor(viewportHeight-top-pad));
 return {left,top,maxHeight};
}

/** Same-session, cross-page editor clipboard; deliberately never persisted to disk. */
type Saved={sessionId:string;widgets:any[]};
let clipboard:Saved|null=null;
export function saveEditorWidgetClipboard(sessionId:string,widgets:ReadonlyArray<any>):number{
 if(!sessionId||!widgets.length)return 0;
 clipboard={sessionId,widgets:structuredClone(widgets.slice(0,16))};
 return clipboard.widgets.length;
}
export function readEditorWidgetClipboard(sessionId:string):any[]{
 return sessionId&&clipboard?.sessionId===sessionId?structuredClone(clipboard.widgets):[];
}
export function clearEditorWidgetClipboard():void{clipboard=null;}

/** Shared percentage geometry for the editable slide, audience, and presenter.
 * Keep CSS positioning consistent: page position is authoritative, not the
 * fallback dimensions of the surrounding panel. */
export type WidgetGeometry={x:number;y:number;width:number;height?:number;rotation?:number};
export function widgetGeometryStyle(p:WidgetGeometry):{position:'absolute';left:string;top:string;width:string;height:string;transform:string}{
 return {position:'absolute',left:p.x+'%',top:p.y+'%',width:p.width+'%',height:(p.height??24)+'%',transform:`rotate(${p.rotation??0}deg)`};
}

/** Deterministic, page-local multi-widget alignment; never mutates the draft. */
export type ArrangeMode='left'|'right'|'top'|'bottom'|'center-x'|'center-y'|'same-width'|'same-height'|'distribute-x'|'distribute-y'|'space-x'|'space-y'|'canvas-center-x'|'canvas-center-y';
type Rect={x:number;y:number;width:number;height:number;rotation?:number};
type Item={id:string;position?:Partial<Rect>};
const bounded=(n:number,limit:number)=>Math.max(0,Math.min(Math.max(0,limit),n));
const rect=(w:Item):Rect=>{
 const p=w.position||{};
 const width=bounded(Number.isFinite(p.width)?p.width!:48,100)||.01;
 const height=bounded(Number.isFinite(p.height)?p.height!:24,100)||.01;
 return {x:bounded(Number.isFinite(p.x)?p.x!:0,100-width),y:bounded(Number.isFinite(p.y)?p.y!:0,100-height),width,height,rotation:Number.isFinite(p.rotation)?p.rotation:0};
};
const round=(v:number)=>+v.toFixed(4);
export function arrangeWidgets<T extends Item>(widgets:T[],ids:readonly string[],mode:ArrangeMode):T[]{
 const chosen=new Set(ids),selected=widgets.filter(w=>chosen.has(w.id));
 if(selected.length<(mode.startsWith('canvas-center')?1:mode.startsWith('distribute')||mode.startsWith('space')?3:2))return widgets;
 const positions=new Map(selected.map(w=>[w.id,rect(w)]));
 const all=selected.map(w=>positions.get(w.id)!);
 const left=Math.min(...all.map(p=>p.x)),top=Math.min(...all.map(p=>p.y));
 const right=Math.max(...all.map(p=>p.x+p.width)),bottom=Math.max(...all.map(p=>p.y+p.height));
 const centerX=(left+right)/2,centerY=(top+bottom)/2;
 const newPositions=new Map<string,Rect>();
 for(const w of selected){const p=positions.get(w.id)!;let q={...p};
  switch(mode){
   case 'left':q.x=left;break;case 'right':q.x=right-p.width;break;
   case 'top':q.y=top;break;case 'bottom':q.y=bottom-p.height;break;
   case 'center-x':q.x=centerX-p.width/2;break;case 'center-y':q.y=centerY-p.height/2;break;
   case 'canvas-center-x':q.x=p.x+(50-centerX);break;case 'canvas-center-y':q.y=p.y+(50-centerY);break;
   case 'same-width':q.width=Math.min(100-p.x,positions.get(ids.find(id=>positions.has(id))!)!.width);break;
   case 'same-height':q.height=Math.min(100-p.y,positions.get(ids.find(id=>positions.has(id))!)!.height);break;
  }
  newPositions.set(w.id,q);
 }
 if(mode==='distribute-x'||mode==='distribute-y'||mode==='space-x'||mode==='space-y'){
  const horizontal=mode.endsWith('-x');
  const sorted=[...selected].sort((a,b)=>{
   const pa=positions.get(a.id)!,pb=positions.get(b.id)!;
   return (horizontal?pa.x+pa.width/2:pa.y+pa.height/2)-(horizontal?pb.x+pb.width/2:pb.y+pb.height/2)||a.id.localeCompare(b.id);
  });
  const first=positions.get(sorted[0].id)!,last=positions.get(sorted[sorted.length-1].id)!;
  const start=horizontal?first.x+first.width/2:first.y+first.height/2;
  const end=horizontal?last.x+last.width/2:last.y+last.height/2;
  if(mode.startsWith('space')){
   const firstEdge=horizontal?first.x:first.y;
   const lastEdge=horizontal?last.x+last.width:last.y+last.height;
   const total=sorted.reduce((sum,w)=>sum+(horizontal?positions.get(w.id)!.width:positions.get(w.id)!.height),0);
   const gap=(lastEdge-firstEdge-total)/(sorted.length-1);
   let edge=firstEdge;
   for(const w of sorted){const p=positions.get(w.id)!;const q=newPositions.get(w.id)!;
    if(horizontal){q.x=edge;edge+=p.width+gap}else{q.y=edge;edge+=p.height+gap}
   }
  }else sorted.forEach((w,i)=>{const p=positions.get(w.id)!;const mid=start+(end-start)*i/(sorted.length-1);const q=newPositions.get(w.id)!;
   if(horizontal)q.x=mid-p.width/2;else q.y=mid-p.height/2;
  });
 }
 return widgets.map(w=>{
  const q=newPositions.get(w.id);if(!q)return w;
  const p={...w.position,x:round(bounded(q.x,100-q.width)),y:round(bounded(q.y,100-q.height)),width:round(q.width),height:round(q.height)};
  return JSON.stringify(p)===JSON.stringify(w.position)?w:{...w,position:p};
 });
}

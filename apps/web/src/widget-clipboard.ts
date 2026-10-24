/** Clone a canvas widget with a new identity and a bounded offset. */
export function pasteWidget<T extends {id:string;position?:{x?:number;y?:number;width?:number;height?:number}}>(source:T, id:string, offset=5):T {
  if(!id || id===source.id) throw new Error('Pasted widget needs a distinct ID');
  const copy=structuredClone(source);
  const p=copy.position||{};
  const width=Math.max(.01,Math.min(100,Number.isFinite(p.width)?p.width!:48));
  const height=Math.max(.01,Math.min(100,Number.isFinite(p.height)?p.height!:24));
  const x=Math.max(0,Math.min(100-width,(Number.isFinite(p.x)?p.x!:0)+offset));
  const y=Math.max(0,Math.min(100-height,(Number.isFinite(p.y)?p.y!:0)+offset));
  return {...copy,id,position:{...p,x,y,width,height}};
}
